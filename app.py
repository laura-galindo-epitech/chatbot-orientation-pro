from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Ajouter le middleware CORS pour permettre l'accès depuis d'autres origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet à toutes les origines de se connecter
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Permet tous les en-têtes
)

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        # Lire le fichier index.html
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return {"message": f"Erreur lors de la lecture du fichier index.html: {e}"}

@app.post("/analyze_offer/")
async def analyze_offer(data: dict):
    try:
        # Exemple de logique d'analyse de l'offre, modifiez selon votre besoin
        question = data.get("question", "")
        response = {
            "message": f"Analyse de l'offre pour la question: {question}"
        }
        return response
    except Exception as e:
        return {"message": f"Erreur dans l'analyse de l'offre: {e}"}
