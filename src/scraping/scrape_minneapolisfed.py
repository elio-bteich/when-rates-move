import pandas as pd
from bs4 import BeautifulSoup
from urllib import request

URL = "https://www.minneapolisfed.org/about-us/monetary-policy/inflation-calculator/consumer-price-index-1913-"


html_page = request.urlopen(URL).read()

# Parser le HTML avec BeautifulSoup
soup = BeautifulSoup(html_page, 'html.parser')

# Initialiser des listes pour stocker les données
years = []
cpi_values = []
inflation_rates = []

# Parcourir les lignes du tableau
for row in soup.find_all('tr')[1:]:  # Ignorer la première ligne (en-têtes)
    cols = row.find_all('td')
    if len(cols) == 3:  # Vérifier qu'il y a bien 3 colonnes
        years.append(cols[0].get_text(strip=True))
        cpi_values.append(cols[1].get_text(strip=True))
        inflation_rates.append(cols[2].get_text(strip=True).replace('%', ''))  # Retirer le symbole %

# Créer un DataFrame pandas
df = pd.DataFrame({
    'Year': years,
    'Annual Average CPI(-U)': cpi_values,
    'Annual Percent Change (rate of inflation)': inflation_rates
})

# Exporter en CSV
df.to_csv('data/cpi_data.csv', index=False)

print("Données exportées avec succès dans 'cpi_data.csv'")