from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import pandas as pd

def get_highcharts_data():
    driver = webdriver.Chrome()
    driver.get("https://www.newyorkfed.org/householdcredit/hhdc-iframe")
    
    # Attendre que les graphiques soient chargés
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "highcharts-series"))
    )
    
    # Exécuter du JavaScript pour extraire les données Highcharts
    script = """
    var results = [];
    // Parcourir toutes les instances Highcharts
    Highcharts.charts.forEach(function(chart, index) {
        if(chart) {
            var chartData = {
                title: chart.title.text,
                series: [],
                xAxis: []
            };
            
            // Récupérer les séries de données
            chart.series.forEach(function(serie) {
                chartData.series.push({
                    name: serie.name,
                    data: serie.options.data.map(function(point) {
                        return (typeof point === 'object' && point.y !== undefined) ? point.y : point;
                    })
                });
            });
            
            // Récupérer les catégories de l'axe X
            chartData.xAxis = chart.xAxis[0].categories;
            
            results.push(chartData);
        }
    });
    return JSON.stringify(results);
    """
    
    # Exécuter le script et parser le résultat
    raw_data = driver.execute_script(script)
    chart_data = json.loads(raw_data)
    
    driver.quit()
    return chart_data


# Fonction pour convertir "2024:Q1" en "Année" et "Quadrimestre"
def split_quarter(date_str):
    if ":" in date_str:
        year, quarter = date_str.split(":")
        return int(year), quarter
    return None, None  # Gère les cas invalides

# Exemple d'utilisation
data = get_highcharts_data()

# Formater les résultats
formatted_data = []
for chart in data:
    chart_entry = {
        "title": chart["title"],
        "dates": chart["xAxis"],
        "series": {s["name"]: s["data"] for s in chart["series"]}
    }
    formatted_data.append(chart_entry)

# Liste pour stocker les DataFrames
dfs = []

# Boucle sur chaque graphique du JSON
for chart in formatted_data:
    title = chart["title"]
    dates = chart["dates"]  # Ex: ["2004:Q1", "2004:Q2", ...]
    
    # Initialiser le DataFrame avec Année et Quadrimestre
    df = pd.DataFrame([split_quarter(d) for d in dates], columns=["Année", "Quadrimestre"])
    
    # Ajouter chaque série du graphique comme colonne
    for serie_name, values in chart["series"].items():
        df[serie_name] = values  # Associe les valeurs correspondantes
    
    # Sauvegarder le DataFrame
    csv_filename = f"data/{title.replace(' ', '_')}.csv"
    df.to_csv(csv_filename, index=False)
    
    print(f"✅ {csv_filename} créé avec succès.")
    
    # Ajouter à la liste des DataFrames si besoin d'un traitement global
    dfs.append(df)

# Exemple d'affichage d'un des DataFrames
print("\n🔹 Extrait du premier DataFrame :")
print(dfs[0].head())
print(dfs[1].head())
print(dfs[2].head())


# print(json.dumps(formatted_data, indent=2))

