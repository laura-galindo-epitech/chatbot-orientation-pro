import requests
from bs4 import BeautifulSoup

# URL de la page des métiers
url = "https://www.cidj.com/metiers"

# Headers pour éviter d’être bloqué
headers = {"User-Agent": "Mozilla/5.0"}

# Envoyer la requête HTTP
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Trouver tous les métiers (balises <h3> contenant les titres)
    metiers = soup.find_all("h3", class_="node-title")

    for metier in metiers:
        titre = metier.text.strip()
        lien = "https://www.cidj.com" + metier.a["href"]
        print(f"{titre} -> {lien}")
else:
    print("Erreur :", response.status_code)
