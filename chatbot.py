from rich.console import Console
from rich.prompt import Prompt
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
import json

# Charger le modèle SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Charger les données depuis un fichier JSON
def load_data():
    try:
        with open("ideo_metiers_onisep.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Erreur lors du chargement du fichier JSON : {e}")
        return pd.DataFrame()

# Créer un index FAISS à partir des descriptions des métiers
def create_faiss_index(df):
    descriptions = df["description"].tolist()
    embeddings = model.encode(descriptions)

    # Créer un index FAISS
    index = faiss.IndexFlatL2(embeddings[0].shape[0])
    index.add(embeddings)
    return index

# Fonction pour rechercher des résultats dans FAISS
def search_faiss(query, index, df, top_k=3):
    query_vector = model.encode([query], convert_to_numpy=True)
    _, indices = index.search(query_vector, top_k)
    
    results = df.iloc[indices[0]]
    return results[["libellé métier", "description"]]

# Fonction du chatbot avec interface améliorée
def chatbot():
    console = Console()
    # Charger les données et créer l'index
    df = load_data()
    index = create_faiss_index(df)
    console.print("\n[bold green]🤖 Bonjour ! Posez-moi une question sur un métier ou une formation.")
    console.print("👉 Tapez 'exit' pour quitter.", style="dim")
    
    while True:
        query = Prompt.ask("\n[cyan]Vous : ", default="")
        
        if query.lower() in ["exit", "quitter", "bye"]:
            console.print("[bold yellow]👋 Au revoir !", style="bold red")
            break
        
        results = search_faiss(query, index, df)
        if results.empty:
            console.print("[bold red]⚠️ Aucun résultat trouvé.")
        else:
            for _, row in results.iterrows():
                console.print("\n[bold blue]**Résultat trouvé**")
                console.print(f"🧑‍🏫 **Métier** : {row['libellé métier']}", style="bold")
                console.print(f"📚 **Description** : {row['description']}", style="italic")

# Lancer le chatbot
chatbot()