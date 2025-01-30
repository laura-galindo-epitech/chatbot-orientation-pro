import requests
import csv
import time
from bs4 import BeautifulSoup

# URL de la page principale des métiers
BASE_URL = "https://www.cidj.com/metiers"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_metiers_urls():
    """Récupère les liens des fiches métiers sur plusieurs pages"""
    metiers_data = []

    for page in range(0, 5):  # Adapter le nombre de pages si besoin
        url = f"{BASE_URL}?page={page}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            metiers = soup.find_all("h3", class_="node-title")

            for metier in metiers:
                titre = metier.text.strip()
                lien = "https://www.cidj.com" + metier.a["href"]
                metiers_data.append((titre, lien))

            print(f"✅ Page {page} scrappée avec succès !")
        else:
            print(f"❌ Erreur {response.status_code} sur la page {page}")

        time.sleep(2)  # Pause pour éviter de surcharger le serveur
    
    return metiers_data

def scrape_fiche_metier(url):
    """Scrape la description d'un métier à partir de son URL"""
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        description_tag = soup.find("div", class_="field field-name-body")
        
        if description_tag:
            return description_tag.get_text(strip=True)
    
    return "Description non disponible"

def save_to_csv(metiers_data, filename="metiers_cidj.csv"):
    """Enregistre les données des métiers dans un fichier CSV"""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Métier", "Lien", "Description"])  # En-tête
        
        for titre, lien in metiers_data:
            description = scrape_fiche_metier(lien)
            writer.writerow([titre, lien, description])
            print(f"📄 Métier sauvegardé : {titre}")
            time.sleep(2)  # Pause entre chaque fiche métier
    
    print(f"✅ Données enregistrées dans {filename}")

if __name__ == "__main__":
    print("🔍 Scraping des métiers en cours...")
    metiers = get_metiers_urls()
    
    print(f"📌 {len(metiers)} métiers trouvés !")
    save_to_csv(metiers)
    print("🎉 Scraping terminé avec succès !")

