import yfinance as yf
import pandas as pd
from tqdm import tqdm  # Barre de progression

# Définition des tickers avec leurs périodes spécifiques
tickers = {
    "^GSPC": {"name": "sp500", "start": "1954-01-01", "end": "2025-12-31"},
    "GC=F": {"name": "gold", "start": "1970-01-01", "end": "2025-12-31"},
}

# Boucle pour récupérer les données de chaque actif
for ticker, info in tqdm(tickers.items(), desc="Téléchargement des données"):
    start_date = info["start"]
    end_date = info["end"]
    name = info["name"]

    print(f"\n📊 Récupération des données de {name} ({start_date} → {end_date})...")

    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        print(f"⚠️ Aucune donnée trouvée pour {name} ({ticker}) !")
    else:
        filename = f"../data/{name}_{start_date[:4]}_{end_date[:4]}.csv"
        data.to_csv(filename)
        print(f"✅ Données de {name} enregistrées dans {filename}")

print("\n🚀 Téléchargement terminé !")
