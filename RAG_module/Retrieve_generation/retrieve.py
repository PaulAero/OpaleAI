# retrieve.py
from oauthlib.uri_validate import segment

from RAG_module.Process_documents.vectorization_and_storage import vectorize_and_store_in_chroma, search_in_chroma, \
    get_chroma_collection, client, check_collection, get_with_segment

def retrieve(query, n_results=5):
    # Rechercher les documents en fonction de la requête dans ChromaDB
    results = search_in_chroma(query, n_results=n_results)

    if results['documents'] != 0:
        list_documents = results['documents'][0]
        print(f"Résultat de la recherche, {query}:")

        # On récupère les autres infos
        try:
            list_metadatas = results['metadatas'][0]
        except:
            print("Erreur lors de la récupération des métadatas")

        return {
            "context": "\n".join(list_documents),
            "list_documents": list_documents,
            "list_metadatas": list_metadatas
        }

    else:
        print("Aucun résultat")
        return ""

if __name__ == "__main__":
    # On vérifie que la collection n'est pas vide
    check_collection()

    # Exemple d'utilisation pour tester la recherche de documents
    query = "définition du budget"
    print(f"Query: {query}")

    retrieve_data = retrieve(query)
    print(retrieve_data["context"])
    print(retrieve_data["list_metadatas"])
    print("Longueurs liste de documents: ",len(retrieve_data["list_documents"]))