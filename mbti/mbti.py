from playwright.sync_api import sync_playwright
import json

def scrape_mbti_jobs():
    with sync_playwright() as p:
        # 1) Lancement du navigateur Chromium sans interface
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 2) Ouvrir la page ciblée
        url = "https://go.olecio.fr/metiers/mbti-personnalites-metiers"
        page.goto(url, timeout=60000)
        
        # 3) Attendre qu'au moins un <h2> avec cette classe apparaisse
        page.wait_for_selector("h2.wp-block-heading", timeout=60000)

        # 4) Récupérer tous les titres MBTI (ex: "ESFP – L’Amuseur")
        headings = page.query_selector_all("h2.wp-block-heading")

        mbti_data = {}

        for heading in headings:
            mbti_title = heading.inner_text().strip()

            # Chercher le blockquote suivant dans les éléments frères
            blockquote_handle = heading.evaluate_handle("""
                (el) => {
                    let sibling = el.nextElementSibling;
                    while (sibling) {
                        if (sibling.tagName && sibling.tagName.toLowerCase() === "blockquote") {
                            return sibling;
                        }
                        sibling = sibling.nextElementSibling;
                    }
                    return null;
                }
            """)

            # Vérifier si on a trouvé un blockquote
            if not blockquote_handle:
                mbti_data[mbti_title] = ["Métier non trouvé"]
                continue

            blockquote_element = blockquote_handle.as_element()
            if not blockquote_element:
                mbti_data[mbti_title] = ["Métier non trouvé"]
                continue
            
            # Récupérer le premier <p> dans ce blockquote
            p_element = blockquote_element.query_selector("p")
            if not p_element:
                mbti_data[mbti_title] = ["Métier non trouvé"]
                continue
            
            # Extraire le texte (ex. "Métiers potentiels : Acteur, Musicien, ...")
            text = p_element.inner_text().strip()
            
            if "Métiers potentiels" in text:
                splitted = text.split("Métiers potentiels :")
                if len(splitted) > 1:
                    jobs_part = splitted[1]
                    # Séparer par virgules
                    jobs = [j.strip() for j in jobs_part.split(",") if j.strip()]
                    mbti_data[mbti_title] = jobs
                else:
                    mbti_data[mbti_title] = ["(Problème de parsing)"]
            else:
                mbti_data[mbti_title] = ["Métier non trouvé"]

        # 5) Fermer le navigateur
        browser.close()

        # 6) Sauvegarder les résultats dans un fichier JSON
        with open("mbti_jobs.json", "w", encoding="utf-8") as f:
            json.dump(mbti_data, f, indent=4, ensure_ascii=False)

        print("✅ Extraction terminée, résultats dans mbti_jobs.json")


if __name__ == "__main__":
    scrape_mbti_jobs()
