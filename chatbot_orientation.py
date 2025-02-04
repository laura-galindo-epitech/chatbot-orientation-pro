from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from pathlib import Path

app = FastAPI()

# Charger les données depuis le fichier JSON
def load_data():
    try:
        with open("ideo_metiers_onisep.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier JSON : {e}")
        return []

# Modèle pour la question utilisateur
class Question(BaseModel):
    question: str

# Route principale pour afficher la page HTML
@app.get("/", response_class=HTMLResponse)
async def get_home():
    html_content = Path(__file__).parent / "index.html"
    with open(html_content, "r", encoding="utf-8") as file:
        return file.read()

# Route pour analyser la question et renvoyer une réponse
@app.post("/analyze_offer/")
async def analyze_offer(request: Question):
    data = load_data()
    question = request.question.lower()
    # Recherche dans les données pour trouver une réponse
    results = []
    for item in data:
        if question in item['libellé métier'].lower() or question in item['description'].lower():
            results.append(item)
    if results:
        return {"results": results}
    else:
        return {"message": "Aucune offre trouvée."}
