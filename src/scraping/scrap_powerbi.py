from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd

# Configuration de Chrome pour le mode headless (sans interface graphique)
def configure_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Activer le mode headless
    chrome_options.add_argument("--disable-gpu")  # Option pour éviter les erreurs GPU
    chrome_options.add_argument("--no-sandbox")  # Utile pour certaines configurations
    return webdriver.Chrome(options=chrome_options)

# Fonction pour accéder à la page Power BI et interagir avec le graphique
def get_html(driver):
    driver.set_window_size(1920, 1080)
    url = "https://app.powerbi.com/view?r=eyJrIjoiNjk1Mzc4YzgtODMxOS00ODMxLWE1MTMtMjBiOGI5NmNhNTUzIiwidCI6IjViOTczZjk5LTc3ZGYtNGJlYi1iMjdkLWFhMGM3MGI4NDgyYyIsImMiOjh9"
    driver.get(url)
    
    # Attendre que le graphique soit visible et cliquable
    wait = WebDriverWait(driver, 30)
    graphique = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "cartesianChart")))  # XPATH à ajuster si nécessaire

    action = ActionChains(driver)
    action.move_to_element(graphique).perform()

    # Cliquer sur le bouton drill-down
    bouton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="drill-down-level-grouped-btn"]')))
    bouton.click()
    
    # Attendre quelques secondes pour que l'animation se termine
    time.sleep(3)

    # Clic droit sur le graphique pour afficher un menu contextuel
    action.context_click(graphique).perform()

    # Attendre l'apparition du menu contextuel
    time.sleep(1)

    # Cliquer sur l'option "Afficher sous forme de table"
    span = driver.find_element(By.XPATH, '//span[text()="Afficher sous forme de table"]')
    span.click()

    # Attendre quelques secondes pour que la table soit affichée
    time.sleep(3)

    # Récupérer le code HTML de la page
    html_page = driver.page_source
    
    # Fermer le driver
    driver.quit()
    
    return html_page

# Fonction pour extraire les coordonnées de translation d'un élément SVG
def get_translate_x(element):
    """
    Fonction pour extraire la valeur de translation X d'un élément SVG (par exemple, un rectangle).
    """
    transform = element.get('transform', '')
    if transform and transform.startswith('translate('):
        # Extraire les valeurs entre parenthèses
        values = transform.split('(')[1].split(')')[0].split(',')
        if len(values) >= 1:
            return float(values[0])  # Convertir la première coordonnée en float
    return 0  # Valeur par défaut si `transform` n'est pas valide

# Fonction pour analyser le HTML et extraire les données pertinentes
def extract_data_from_html(html_page):
    """
    Fonction qui analyse le code HTML pour extraire les informations sur les années, trimestres,
    valeurs de deals et nombres de deals depuis le graphique Power BI.
    """
    soup = BeautifulSoup(html_page, 'html.parser')

    # Extraire les éléments de type "rect" et les ticks
    rects = soup.find_all('rect')[1:]  # Ignorer le premier rectangle qui est généralement une légende
    x = soup.find('g', class_='x')
    ticks = x.find_all('g', class_='tick')
    labels = soup.find_all('g', class_='label-container')

    # Trier les labels en fonction de leur position sur l'axe X
    sorted_g_elements = [
        label for label in sorted(labels, key=get_translate_x)
        if not "$" in label.find('text').find('tspan').get_text().strip()
    ]

    # Extraire le nombre de deals depuis les labels
    nb_deals = []
    for label in sorted_g_elements:
        text_label = label.find('text').find('tspan').get_text().strip()
        if not '$' in text_label:
            nb_deals.append(text_label)

    # Extraire les données complètes de chaque rect, tick et label
    data = []
    for rect, tick, nb_deal in zip(rects, ticks, nb_deals):
        valeur = rect["aria-label"].strip()  # Valeur du deal
        text_element = tick.find('text').find('title')

        if text_element:
            annee = text_element.get_text().split()[0].strip()
            q = text_element.get_text().split()[1].strip()

            # Ajouter les données extraites dans la liste 'data'
            data.append({
                "Année": annee,
                "Quadrimestre": q,
                "Valeur Deal": valeur,
                "Nombre de deals": nb_deal
            })

    return data

# Fonction principale pour orchestrer tout le processus
def main():
    # Initialiser le driver et récupérer la page Power BI
    driver = configure_chrome_driver()
    html_page = get_html(driver)

    # Fermer le navigateur après récupération des données
    driver.quit()

    # Extraire les données de la page HTML
    data = extract_data_from_html(html_page)

    # Convertir les données en DataFrame et les enregistrer dans un fichier CSV
    df = pd.DataFrame(data)
    df.to_csv("data/venture_capitalist_powerbi.csv", index=False)
    print("Données extraites et sauvegardées avec succès.")

if __name__ == "__main__":
    main()
