import requests
import json


def query_mistral_nemo(prompt):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "mistral-nemo",
        "prompt": prompt,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        return response.json()['response']
    else:
        return f"Erreur: {response.status_code}, {response.text}"


# Exemple d'utilisation
if __name__ == "__main__":
    # user_prompt = input("Entrez votre question pour Mistral-Nemo : ")
    user_prompt = "Explique moi l'origine des chats Persan ?"
    print(user_prompt)
    result = query_mistral_nemo(user_prompt)
    print("Réponse de Mistral-Nemo :")
    print(result)