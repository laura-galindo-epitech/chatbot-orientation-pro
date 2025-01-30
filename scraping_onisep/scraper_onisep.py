import requests
import pandas as pd

# URL du fichier CSV
url = "https://api.opendata.onisep.fr/downloads/5fa591127f501/5fa591127f501.csv"

# Télécharger le CSV
response = requests.get(url)

if response.status_code == 200:
    print("🔎 Contenu brut de la réponse :\n")
    print(response.text[:500])  # Afficher seulement les 500 premiers caractères

    # Charger le CSV avec pandas
    from io import StringIO
    df = pd.read_csv(StringIO(response.text), sep=";")  # Vérifier le séparateur ici

    # Sauvegarder en JSON
    df.to_json("onisep_data.json", orient="records", force_ascii=False, indent=4)

    print(f"Données enregistrées dans onisep_data.json ({len(df)} entrées)")

else:
    print(f"Erreur {response.status_code}: Impossible de récupérer les données.")
