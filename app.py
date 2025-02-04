from fastapi import FastAPI, Request
from pydantic import BaseModel
import json

app = FastAPI()

# Charger les données des métiers à partir du fichier JSON
with open("ideo_metiers_onisep.json", encoding="utf-8") as f:
    metiers_data = json.load(f)

class Question(BaseModel):
    question: str

@app.post("/analyze_offer")
async def analyze_offer(question: Question):
    question_text = question.question.lower()
    results = []
    for metier in metiers_data:
        # Recherche de mots-clés dans le libellé métier
        if any(keyword.lower() in metier['libellé métier'].lower() for keyword in question_text.split()):
            results.append({
                'libellé métier': metier['libellé métier'],
                'description': metier.get('domaine/sous-domaine', 'Description non disponible')
            })
        # Recherche de mots-clés dans la description (domaine/sous-domaine)
        elif any(keyword.lower() in metier.get('domaine/sous-domaine', '').lower() for keyword in question_text.split()):
            results.append({
                'libellé métier': metier['libellé métier'],
                'description': metier.get('domaine/sous-domaine', 'Description non disponible')
            })
    return {"results": results}

@app.get("/")
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    return content
