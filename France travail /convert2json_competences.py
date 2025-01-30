import pandas as pd

def excel_to_json(excel_file, json_file):
    try:
        # Lire la feuille "Metier"
        df = pd.read_excel(excel_file, sheet_name="Compétences-brutes")

        # Convertir en JSON et enregistrer
        df.to_json(json_file, orient='records', lines=True, force_ascii=False)
        print(f" Le fichier JSON '{json_file}' a été créé avec succès.")

    except ValueError as ve:
        print(f" Erreur : La feuille 'Compétences-brutes n'existe pas dans le fichier Excel ({ve})")
    except FileNotFoundError:
        print(f" Erreur : Le fichier Excel '{excel_file}' est introuvable.")
    except Exception as e:
        print(f" Une erreur est survenue : {e}")

if __name__ == "__main__":
    # Chemin du fichier Excel
    excel_file_path = "/Users/Paq/Desktop/Projetchatbot/Competences-Rome-themes.xlsx"
    
    #  Chemin du fichier JSON à générer
    json_file_path = "/Users/Paq/Desktop/Projetchatbot/output.json"
    
    # ✅ Exécuter la conversion
    excel_to_json(excel_file_path, json_file_path)
