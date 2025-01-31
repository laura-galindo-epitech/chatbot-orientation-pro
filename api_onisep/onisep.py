import requests
import json

EMAIL = "laura.galindo@epitech.digital"
PASSWORD = "^l=6aw_9.tNBu0M"

def get_api_token(email, password):
    """Get an Onisep API token using credentials"""
    url = "https://api.opendata.onisep.fr/api/1.0/login"
    payload = {"email": email, "password": password}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception("Authentication error: " + response.text)

def list_datasets():
    """Get list of Onisep datasets"""
    url = "https://api.opendata.onisep.fr/api/1.0/dataset"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error while retrieving datasets: " + response.text)

def fetch_dataset(token, dataset_code):
    """Get a dataset's metadata"""
    url = f"https://api.opendata.onisep.fr/api/1.0/dataset/{dataset_code}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error while retrieving dataset {dataset_code}: " + response.text)

def save_to_json(data, filename):
    """Save data to a JSON file"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved in {filename}")

if __name__ == "__main__":    
    try:
        # Get API token
        token = get_api_token(EMAIL, PASSWORD)
        print("Token successfully retrieved")

        # Get list of datasets
        datasets = list_datasets()

        # Save the list of datasets in a JSON file
        save_to_json(datasets, 'datasets.json')

        # Define filter themes
        target_themes = {"formations", "structures d'enseignement", "certifications", 
                         "fiches", "métiers", "options", "spécialités de baccalauréat", "langues"}

        # Filter the datasets
        filtered_datasets = []
        results = datasets.get("results", [])  # Ensure "results" exists

        for dataset in results:
            title = dataset.get("title", "N/A")
            code = dataset.get("code", "N/A")
            themes = dataset.get("themes", [])

            if set(themes) & set(target_themes):
                files = dataset.get("files", {})  # Default to empty dictionary
                
                if isinstance(files, dict):  # Ensure "files" is a dictionary
                    download_url = files.get("json") or next(iter(files.values()), None)
                else:
                    download_url = None  # Skip if "files" is not a dictionary

                if download_url:  # Ensure there's a valid URL
                    filtered_datasets.append({
                        "title": title,
                        "code": code,
                        "themes": themes,
                        "url": download_url,
                    })

        # Print the final list after filtering
        print(f"Filtered {len(filtered_datasets)} datasets.")
        print(filtered_datasets)  # Print final output for debugging

        # Save the results in a JSON file
        save_to_json(filtered_datasets, 'filtered_datasets.json')

    except Exception as e:
        print(f"Error: {e}")