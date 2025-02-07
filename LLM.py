import os
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

# Charger les variables d'environnement
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral-small-latest")

if not MISTRAL_API_KEY:
    raise ValueError("La clé API Mistral est manquante.")

# Initialisation du modèle Mistral
llm = ChatMistralAI(
    mistral_api_key=MISTRAL_API_KEY,
    model=MODEL_NAME,
    streaming=True
)

prompt_template = ChatPromptTemplate.from_template(
    """
    Tu es un assistant d'orientation professionnelle. Aide l'utilisateur à choisir un métier.
    
    CONTEXTE:
    ---------------------
    {context}
    ---------------------
    
    Question: {input}
    """
)

def generate_response(user_query: str):
    context = "Informations générales sur les métiers et l'orientation."
    formatted_prompt = prompt_template.format(input=user_query, context=context)
    
    try:
        response = llm.invoke(formatted_prompt)
        return response if response else "Désolé, je n'ai pas compris."
    except Exception as e:
        return f"Erreur: {str(e)}"

if __name__ == "__main__":
    question = input("Posez une question au modèle : ")
    response = generate_response(question)
    print("Réponse :", response)
