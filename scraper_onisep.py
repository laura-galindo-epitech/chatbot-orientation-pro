import pandas as pd
import json

# Fonction pour charger et convertir le fichier CSV en JSON
def load_and_convert_to_json(file_path, output_file_path):
    try:
        # Charger le fichier CSV avec gestion des lignes mal formées
        df = pd.read_csv(file_path, delimiter=";", on_bad_lines="skip")
        
        # Convertir le DataFrame en JSON
        result_json = df.to_json(orient="records", lines=False)
        
        # Convertir le JSON en dictionnaire Python
        result_dict = json.loads(result_json)
        
        # Sauvegarder le JSON dans un fichier
        with open(output_file_path, 'w') as json_file:
            json.dump(result_dict, json_file, indent=4)
        
        print(f"Le fichier JSON a été créé avec succès : {output_file_path}")
    except Exception as e:
        print(f"Erreur lors de la conversion en JSON : {e}")

# Spécifier le chemin vers ton fichier CSV et le fichier de sortie JSON
file_path = "ideo-metiers_onisep.csv"
output_file_path = "ideo_metiers_onisep.json"

# Appel de la fonction pour convertir le CSV en JSON et sauvegarder dans un fichier
load_and_convert_to_json(file_path, output_file_path)
