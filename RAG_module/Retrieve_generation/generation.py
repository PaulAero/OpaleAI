# generation.py
import requests
import json

def query_ollama(model, query, documents, show_full_prompt=False):
    url = f"http://localhost:11434/api/generate"

    headers = {
        "Content-Type": "application/json"
    }

    prompt = (f"**Generate Response to User Query**\n"
            f"**Step 1: Parse Context Information**\n"
            f"Extract and utilize relevant knowledge from the provided context within `<context></context>` XML tags.\n"
            f"**Step 2: Analyze User Query**\n"
            f"Carefully read and comprehend the user's query, pinpointing the key concepts, entities, and intent behind the question.\n"
            f"**Step 3: Determine Response**\n"
            f"If the answer to the user's query can be directly inferred from the context information, provide a concise and accurate response in the same language as the user's query.\n"
            f"**Step 4: Handle Uncertainty**\n"
            f"If the answer is not clear, ask the user for clarification to ensure an accurate response.\n"
            f"**Step 5: Avoid Context Attribution**\n"
            f"When formulating your response, do not indicate that the information was derived from the context.\n"
            f"**Step 6: Respond in User's Language**\n"
            f"Maintain consistency by ensuring the response is in the same language as the user's query.\n"
            f"**Step 7: Provide Response**\n"
            f"Generate a clear and informative response to the user's query, adhering to the guidelines outlined above.\n"
            f"<context>\n"
            f"{documents}"
            f"\n</context>\n"
            f"User Query: {query}\n")

    # Payload pour l'API d'Ollama
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    if show_full_prompt == True:
        print(f"\nPrompt complete:\n{payload["prompt"]}\n")

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Erreur avec Ollama : {response.status_code}, {response.text}")

# Test
if __name__ == "__main__":
    model = "mistral-nemo"
    prompt = "Quels sont les impacts environnementaux du projet décrit ?"

    documents = ("Le projet de construction d'une nouvelle usine dans la région X a soulevé des préoccupations importantes en matière d'impact environnemental. "
    "\nLe rapport d'évaluation indique que l'usine augmentera les émissions de CO2 de 15% dans les zones avoisinantes et pourrait affecter la qualité de l'air localement. "
    "\nCependant, des mesures d'atténuation sont prévues, notamment la plantation de 500 arbres et l'utilisation de filtres à air de haute qualité. "
    "\nL'usine adoptera également des pratiques de gestion des déchets plus durables pour minimiser les impacts à long terme sur la biodiversité.")

    response = query_ollama(model, prompt, documents, show_full_prompt=True)
    print(f"Generated Response: {response}")