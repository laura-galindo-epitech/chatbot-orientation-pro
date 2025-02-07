#!/usr/bin/env python
# coding: utf-8

import os
import json
import getpass

import requests
import chromadb
from chromadb import PersistentClient
from dotenv import load_dotenv

from langchain.vectorstores import Chroma
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate, PromptTemplate, PipelinePromptTemplate
)
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain import hub


# Load environment variables from .env file

load_dotenv()

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# Building a Retrieval Augmented Generation (RAG) Chatbot

get_ipython().system('pip install --quiet --upgrade langchain-text-splitters langchain-community langgraph')
get_ipython().system('pip install -qU langchain-mistralai')
get_ipython().system('pip install -qU langchain-chroma')
get_ipython().system('pip install python-dotenv')

# Chat model initialization
llm = ChatMistralAI(
    mistral_api_key=MISTRAL_API_KEY,
    model=MODEL_NAME,
    streaming=True,
    temperature=0.6
)

# Embeddings model
embeddings = MistralAIEmbeddings(model="mistral-embed")

# 1️⃣ Connect to the existing ChromaDB instance
db_path = "./RAG/final_chroma_db"
collection_name = "final_vector_store_collection"

client = PersistentClient(path=db_path)
collection = client.get_or_create_collection(name=collection_name)

# 2️⃣ Load stored embeddings from ChromaDB
stored_data = collection.get()

# 3️⃣ Check how many embeddings are loaded
num_loaded = len(stored_data["ids"])

# 🔄 Recharger le vector store depuis la base de données ChromaDB
vector_store = Chroma(
    persist_directory=db_path,
    collection_name=collection_name,
    embedding_function=embeddings
)

# LLM Prompt-Engineering

prompt_principal = ChatPromptTemplate.from_template(
    """
    Tu es **Crystal Bot**, un assistant intelligent d'orientation professionnelle.
    Tu dois fournir des réponses basées sur les informations récupérées.
    
    Ton objectif est d'aider chaque utilisateur à **clarifier son avenir** en lui proposant **des conseils sur-mesure et motivants**.

    **Contexte pertinent issu de la base de connaissances :** 
    {context}
    
    ➤ **Adapte-toi à l’utilisateur** : si indécis, propose des pistes d’exploration.
    ➤ **Si comparaison de plusieurs options**, aide-le à peser le pour et le contre.
    ➤ **Propose une réponse fluide, naturelle et pas trop longue**, qui ne se contente pas d’une liste figée, mais qui établit un dialogue et donne des solutions plus large.
    """
)

topic_prompt = PromptTemplate.from_template(
    """
    Analyse la question suivante et identifie le ou les domaines principaux auxquels elle appartient.

    Question: {input}

    Réponds en listant **un ou plusieurs domaines** parmi les suivants (séparés par une virgule) :
    - "Informatique et Numérique"
    - "Sciences et Ingénierie"
    - "Santé et Médecine"
    - "Droit et Sciences Politiques"
    - "Économie et Gestion"
    - "Sciences Sociales et Psychologie"
    - "Arts, Design et Culture"
    - "Lettres et Langues"
    - "Sciences de l'Éducation"
    - "Communication et Journalisme"
    - "Tourisme, Hôtellerie et Restauration"
    - "Environnement et Développement Durable"
    - "Sport et Activité Physique"
    - "Architecture et Urbanisme"
    - "Agronomie et Agroalimentaire"

    Si aucun domaine n’est clair, réponds uniquement par "Autre".

    Domaines identifiés :
    """
)

intent_prompt = PromptTemplate.from_template(
    """
    Analyse la question suivante et identifie l’intention principale de l’utilisateur :

    Question: {input}

    Réponds par l’une ou plusieurs des options suivantes :
    - "Métiers"
    - "Formations"
    - "Salaire"
    - "Offres d'emploi"
    - "Parcoursup"
    - "Autre"

    Intention détectée :
    """
)

chatbot_prompt = PromptTemplate.from_template(
    """
    
    Je suis **Crystal Bot**, ton conseiller d'orientation professionnelle. 🔮✨  
    
    L'utilisateur a demandé : {input}.
    Domaine détecté : {topic} (caché à l'utilisateur)
    Intention détectée : {intent} (caché à l'utilisateur)
    
  ➤ **Si l'intention est "Métiers"** :
        - Propose des **métiers adaptés** au profil de l’utilisateur en allant au-delà des évidences.   
        - Explique **les missions, conditions de travail et débouchés** en t’adaptant à la curiosité de l’utilisateur.  
        - **N’hésite pas à raconter une anecdote ou une tendance actuelle, personnalise la réponse** pour rendre la réponse plus vivante et personnalisée.  
        - **Fournis une vision inspirante et dynamique**, et pas seulement une simple liste de métiers.

    ➤ **Si l'intention est "Formations"** :
        - Présente des **formations pertinentes** mais **ajoute des alternatives originales** (double cursus, parcours atypiques).
        - Décris les options de manière dynamique : **BTS, Licence, Master, écoles spécialisées, mais aussi MOOC et certifications**.  
        - **Varie les approches selon la question de l’utilisateur**, sans donner toujours la même liste figée.
        - Rassure l’utilisateur en expliquant que *sa motivation est un facteur clé*. *Donne lui des conseils*
        - **N’hésite pas à raconter une anecdote ou une tendance actuelle, personnalise la réponse** pour rendre la réponse plus vivante et personnalisée. 
        - Si pertinent propose à l'utilisateur de visiter des salons pour en savoir plus sur les formations. 

    ➤ **Si l'intention est "Salaire"** :
        - Donne **un aperçu détaillé des salaires**, mais va au-delà des chiffres standards en ajoutant **les tendances du marché**.  
        - Explique **les différences selon l’expérience, le secteur, et la localisation**.  
        - **Si pertinent, parle des avantages indirects** (avantages en nature, perspectives d’évolution, travail à l’international).  
         - **N’hésite pas à raconter une anecdote ou une tendance actuelle, personnalise la réponse** pour rendre la réponse plus vivante et personnalisée.  

    ➤ **Si l'intention est "Offres d'emploi"** :
        - **Décris le marché actuel** du secteur concerné : quelles entreprises recrutent ? Quelles compétences sont recherchées ?
        - Donne **des conseils personnalisés** pour optimiser les candidatures, en fonction du domaine visé.
        - **Propose une approche proactive** : comment créer des opportunités, réseauter efficacement ou se démarquer ?  
         - **N’hésite pas à raconter une anecdote ou une tendance actuelle, personnalise la réponse** pour rendre la réponse plus vivante et personnalisée.  

    ➤ **Si l'intention est "Parcoursup"** :
        - **Explique Parcoursup en t’adaptant au profil de l’utilisateur** (lycéen stressé, étudiant en réorientation…).
        - Fournis **des conseils concrets pour réussir son dossier** et éviter les pièges.  
        - Fournis **des conseils concrets pour réussir la lettre de motivation** et se distinguer des autres candidats. 
        - Si pertinent, parle **des alternatives à Parcoursup** (écoles privées, études à l’étranger, admissions parallèles).  
    

    ➤ **Si l'intention est "Autre"** :
        - **Interprète la demande de l’utilisateur avec souplesse** et propose une réponse originale.  
        - Si possible, **ouvre la discussion sur des idées nouvelles** en fonction de son profil.
        - **Demande lui plus de précisions sur ce qu'il souhaite apprendre ou approfondir** en terme professionnel ou de formation.
         
    """
)

closing_prompt = PromptTemplate.from_template(
    """
    J’espère que cette réponse **t’a aidé à y voir plus clair !** 🔮  
    **As-tu d’autres questions ?** Je suis là pour explorer toutes les possibilités avec toi.  
    """
)

# Setting up conversation memory

memory = MemorySaver()
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    """Appelle le modèle avec historique de conversation"""
    response = llm.invoke(state["messages"])
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
chatbot = workflow.compile(checkpointer=memory)

# Creating the retrieval chain with LangChain

def build_retrieval_chain(vector_store, llm, k=5):
    """
    Build a retrieval chain using a given vector store and LLM
    
    Parameters:
        - vector_store: The vector store containing document embeddings
        - llm: The language model to generate responses
        - k: Number of most relevant document chunks to retrieve (default is 5)
    
    Returns:
        - retrieval_chain: A LangChain retrieval chain object.
    """
    # Create a retriever from the vector store
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    
    # Load a pre-defined prompt template for retrieval-based Q&A
    retrieval_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    
    # Create a document combination chain
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_chat_prompt)
    
    # Create and return the retrieval chain
    return create_retrieval_chain(retriever, combine_docs_chain)

def retrieve_and_format_context(user_query, vector_store, llm):
    """Retrieve documents from vector store and format the context"""
    retrieval_chain = build_retrieval_chain(vector_store, llm)
    retrieved_docs = retrieval_chain.invoke({"input": user_query})

    documents = retrieved_docs["context"]

    formatted_context = "\n".join([doc.page_content for doc in documents])
    sources = [doc.metadata.get("source", "Unknown source") for doc in documents]

    return formatted_context, sources

# Building a full ChatBot response

def generate_response(user_query, vector_store, llm):
    """Generate an optimized response with CrystalBot and keep the history"""

    context, sources = retrieve_and_format_context(user_query, vector_store, llm)
    
    global conversation_history  # Utilisation d'une variable distincte pour stocker les messages

    # Charger l'historique des messages de manière locale
    past_messages = conversation_history if 'conversation_history' in globals() else []  

    # **🔹 Étape 1 : Détection du domaine / topic**
    topic_output = topic_prompt.format(input=user_query)

    # **🔹 Étape 2 : Détection de l’intention utilisateur**
    intent_output = intent_prompt.format(input=user_query)
    if not intent_output:
        intent_output = "Autre"

    # **🔹 Étape 3 : Génération de la réponse principale**
    chatbot_prompt_hidden = chatbot_prompt.format(
        input=user_query, 
        topic=topic_output, 
        intent=intent_output,
        context=context,
    )

    chatbot_output = chatbot_prompt_hidden.replace(topic_output, "").replace(intent_output, "")

    # **🔹 Étape 4 : Génération des suggestions d’exploration selon l’intention détectée**
    exploration_suggestions = ""

    if "Métiers" in intent_output:
        exploration_suggestions += """
        **🌍 Pour aller plus loin :**  
        - 🔍 **Découvre des métiers similaires** via des plateformes comme Onisep ou Studyrama.  
        - 🎭 **Participe à des salons professionnels** et rencontres avec des experts du domaine.  
        - 👥 **Échange avec des professionnels** sur LinkedIn ou lors d’événements.  
        """

    if "Formations" in intent_output or "Parcoursup" in intent_output:
        exploration_suggestions += """
        **📚 Pour approfondir ton parcours :**  
        - 🎤 **Découvre les parcours d’anciens étudiants** via des témoignages en ligne.  
        - 🔎 **Explore les formations en alternance** et internationales.  
        - 🏫 **Assiste aux journées portes ouvertes** des écoles et universités.  
        """

    if "Salaire" in intent_output:
        exploration_suggestions += """
        **💰 Pour mieux comprendre les salaires et évolutions de carrière :**  
        - 📊 **Consulte des études de rémunération** sur Glassdoor et l’APEC.  
        - 📈 **Analyse les évolutions de carrière possibles** en fonction de ton secteur.  
        """

    if "Offres d'emploi" in intent_output:
        exploration_suggestions += """
        **📝 Pour trouver des opportunités professionnelles :**  
        - 🔍 **Consulte des plateformes spécialisées** comme Indeed ou Pôle Emploi.  
        - 📩 **Optimise ton CV et ta lettre de motivation** pour te démarquer.  
        """

    if "Les deux" in intent_output:
        exploration_suggestions += """
        **🌟 Pour lier formations et métiers :**  
        - 📚 **Découvre les formations qui recrutent le plus**.  
        - 👀 **Explore les tendances de recrutement dans ton secteur**.  
        """

    if "Autre" in intent_output:
        exploration_suggestions += """
        **🔍 Explorons d’autres pistes !**  
        - 🤔 **Précise un peu plus ta demande**, veux-tu parler de reconversion, d’entrepreneuriat, d’études à l’étranger ?  
        - 💡 **Inspiration** : Parfois, explorer d’autres secteurs peut ouvrir des portes inattendues.  
        - 🔎 **Découvre des parcours inspirants** : interviews, conférences, podcasts sur des choix de carrière atypiques.  
        """

    # **🔹 Étape 5 : Conclusion dynamique**
    closing_output = closing_prompt.format()

    # ✅ **Ajout d’une introduction engageante pour la toute première réponse**
    intro_message = f"""
    Bonjour ! 😊  

    Je suis **Crystal Bot**, ton conseiller d'orientation professionnelle. 🔮✨  
    Mon objectif est de **t’aider à clarifier ton avenir** en te proposant des pistes adaptées et personnalisées.  
    Voici quelques idées et conseils pour t’aider à avancer :  
    """

    # ✅ **Création du message final à envoyer au modèle**
    final_prompt = f"""
    {intro_message}  

    **💡 Recommandation de Crystal Bot :**  
    {chatbot_output}  

    {exploration_suggestions}  

    {closing_output}  
    """

    # ✅ **Ajout du message dans l'historique**
    messages = past_messages + [HumanMessage(content=final_prompt)]

    # ✅ **Envoi de la requête complète au modèle**
    response = llm.invoke(messages)

    # ✅ **Mise à jour de l'historique de la conversation**
    conversation_history = messages + [response]

    return {
        "response": response.content,
        "sources": sources
    }

def refine_response(chatbot_output, user_query, llm):
    """Improve clarity and precision of response with LLM"""
    refinement_prompt = f"""
    Améliore la réponse suivante en la rendant plus précise et engageante :
    Contexte : {user_query}
    Réponse initiale : {chatbot_output}
    Réponse améliorée :
    """

    refined_response = llm.invoke([HumanMessage(content=refinement_prompt)]).content

    return refined_response