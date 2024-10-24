# vectorization_and_storage.py
import chromadb
import uuid
import os

from sentence_transformers import SentenceTransformer
from chromadb.config import Settings
from typing import List

# Obtenir le chemin absolu du répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
persist_directory = os.path.join(project_root, ".chromadb")

print(f"Répertoire de persistance ChromaDB : {persist_directory}")

# Initialisation du client ChromaDB avec le chemin absolu
client = chromadb.PersistentClient(path=persist_directory)


class SentenceTransformerEmbeddingFunction:
    def __init__(self):
        #self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        self.model = SentenceTransformer('all-mpnet-base-v2')

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()

embedding_function = SentenceTransformerEmbeddingFunction()

def get_chroma_collection(collection_name="document_embeddings"):
    """
    Récupère la collection ChromaDB en fournissant la fonction d'embedding.
    """
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

# Stocke les segments et les métadonnées dans ChromaDB.
def vectorize_and_store_in_chroma(segments, metadatas, show_indexation=False, collection_name="document_embeddings"):
    collection = get_chroma_collection(collection_name)

    # Générer des IDs uniques (UUID) pour chaque segment
    ids = [str(uuid.uuid4()) for _ in segments]

    # Ajouter les documents dans ChromaDB sans fournir les embeddings
    collection.add(
        ids=ids,
        documents=segments,
        metadatas=metadatas
    )

    if show_indexation == True:
        # Vérifier le contenu de la collection après l'ajout
        stored_documents = collection.get(include=['documents', 'metadatas'])
        print("\nIndexation")
        print(f"Documents indexés : {stored_documents['documents']}")
        print(f"Métadonnées indexées : {stored_documents['metadatas']}")

def search_in_chroma(query, n_results=2, collection_name="document_embeddings"):
    """
    Effectue une recherche dans ChromaDB avec une requête textuelle (query_texts).
    """
    collection = get_chroma_collection(collection_name)

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return results

def search_in_chroma_segment(query, segment_index, n_results=2, collection_name="document_embeddings"):
    """
        Effectue une recherche dans ChromaDB avec une requête textuelle (query_texts) filtrée par segment index (!=ids).
    """
    collection = get_chroma_collection(collection_name)

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
        where = {"segment_index": segment_index}
    )

    return results

def get_with_segment(segment_index, collection_name="document_embeddings"):
    collection = get_chroma_collection(collection_name)
    doc = collection.get(where={"segment_index": segment_index})
    return doc

def get_with_metadatas(metadata_field, metadata, collection_name="document_embeddings"):
    collection = get_chroma_collection(collection_name)
    doc = collection.get(where={metadata_field: metadata})
    return doc

def delete_collection(collection_name="document_embeddings"):
    client.delete_collection(name=collection_name)
    print(f"Collection {collection_name} supprimée")

def check_collection(collection_name="document_embeddings"):
    collection = get_chroma_collection(collection_name)
    count = collection.count()
    print(f"Nombre de documents dans la collection {collection_name}: {count}")
    return count

def delete_in_collection(filter_field="", filter="", collection_name="document_embeddings"):
    collection = get_chroma_collection(collection_name)
    collection.delete(
        where={filter_field: filter}
    )
    print(f"Elements supprimés de {collection_name} avec le filtrage suivant: {filter_field} = {filter}")