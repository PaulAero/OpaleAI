# RAG_pipeline.py

from RAG_module.Retrieve_generation.retrieve import retrieve
from RAG_module.Retrieve_generation.generation import query_ollama


def rag_pipeline(query, model="mistral-nemo", n_results=5, show_full_prompt=False):
    """
    Pipeline complet RAG : recherche des documents et génération d'une réponse via Ollama.
    :param query: La requête utilisateur.
    :param model: Modèle Ollama à utiliser (ex: mistral-nemo).
    :param n_results: Nombre de documents à retourner pour la génération.
    :return: Réponse générée.
    """
    # Étape 1 : Récupérer les documents pertinents
    results = retrieve(query, n_results)

    documents = results["context"]
    sources = results["list_metadatas"]

    for data in sources:
        show_sources = data["file"] + data["url"] +data["last_updated"] + '\n'

    # Étape 2 : Générer la réponse avec les documents
    response = query_ollama(model, query, documents, show_full_prompt)
    response = response+ '\n' + show_sources

    with open("log_RAG.txt", "w") as log_RAG:
        log_RAG.write(f"Resultat Retrieve: \n{results}")
        log_RAG.write("########################################")
        log_RAG.write(f"\n\nReponse:\n{response}")
        log_RAG.write(f"\n\nSources:\n{show_sources}")

    return response


if __name__ == "__main__":
    # query = "Explique moi l'application de la norme Opale relatif au budget ?\n"
    query = ""
    while query != "/bye":
        query = input("User prompt: ")
        exemple = "Evalue la pertinence du contexte et ce que tu aimerais comme contenu pour l'améliorer."
        #print(f"Prompt utilisateur: {query}\n")
        model = "mistral-nemo"

        # Appeler le pipeline RAG complet
        response = rag_pipeline(query, model, n_results=5, show_full_prompt=True)
        print("\n##########################################################################""")
        print(f"Réponse finale : {response}")
        print("###########################################################################""")