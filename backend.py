import os
from fastapi import FastAPI, Response
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from fastapi.middleware.cors import CORSMiddleware
 
# Charger les variables d'environnement
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral-small-latest")
 
if not MISTRAL_API_KEY:
    raise ValueError("⚠️ Clé API Mistral non trouvée dans les variables d'environnement.")
 
# Initialisation de FastAPI
app = FastAPI()
 
# Gestion des CORS pour éviter les blocages entre frontend et backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
class UserQuery(BaseModel):
    query: str
 
# Route POST pour interroger Mistral AI
@app.post("/chat/")
async def ask_llm(payload: UserQuery):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": payload.query}],
        "max_tokens": 150
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return {"response": response.json().get("choices")[0].get("message").get("content", "Réponse non disponible.")}
    return {"error": "Erreur lors de l'appel à l'API Mistral."}
 
# Route pour servir index.html sans static/
@app.get("/")
def serve_index():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return Response(content=html_content, media_type="text/html")
    except FileNotFoundError:
        return Response(content="Erreur : index.html introuvable", media_type="text/plain", status_code=404)