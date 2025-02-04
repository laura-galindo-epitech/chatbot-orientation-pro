from playwright.sync_api import sync_playwright
import json

def scrape_salons():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://diplomeo.com/actualite-salons_orientation_2024_2025", timeout=60000)

        # Attendre que le tableau soit chargé
        page.wait_for_selector("table")

        # Récupérer toutes les lignes du tableau
        rows = page.query_selector_all("table tr")

        salons = []
        for row in rows[1:]:  # Ignorer la première ligne (en-tête)
            cols = row.query_selector_all("td")
            if len(cols) >= 5:  # Vérifier qu'il y a bien 5 colonnes
                date = cols[0].inner_text().strip()
                theme = cols[1].inner_text().strip()
                organisateur = cols[2].inner_text().strip()
                ville = cols[3].inner_text().strip()
                duree = cols[4].inner_text().strip()
                salons.append({
                    "date": date,
                    "thème": theme,
                    "organisateur": organisateur,
                    "ville": ville,
                    "durée": duree
                })

        browser.close()

        # Enregistrer en JSON
        with open("salons_may_june.json", "w", encoding="utf-8") as f:
            json.dump(salons, f, indent=4, ensure_ascii=False)

        print(f"✅ {len(salons)} salons enregistrés dans salons_diplomeo.json")

# Exécuter le scraper
scrape_salons()
