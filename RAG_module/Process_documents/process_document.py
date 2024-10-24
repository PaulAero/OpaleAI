# process_document.py
from pathlib import Path
from RAG_module.Process_documents.text_cleaning_and_segmentation import extract_and_segment_txt, extract_and_segment_pdf

from RAG_module.Process_documents.vectorization_and_storage import (
    vectorize_and_store_in_chroma,
    check_collection,
    search_in_chroma,
    delete_collection,
    delete_in_collection
)

from datetime import datetime

import os

# Renvoie le chemin absolu du dossier d'entrée.
def get_path(directory):
    # Récupère le chemin du répertoire parent du fichier en cours
    current_file_path = Path(__file__).resolve().parent
    # Construit le chemin vers le dossier
    my_documents_dir = current_file_path.parent / directory
    return my_documents_dir

# process pour vectoriser un document
def process_and_store_documents(directory, filename, url="", show_indexation=False, collection_name="document_embeddings"):
    file_path = os.path.join(directory, filename)

    if not os.path.exists(file_path):
        print(f"Fichier {filename} non trouvé dans le répertoire {directory}.")
        return

    metadatas = []

    # Vérifier si c'est un fichier texte ou PDF
    if filename.endswith(".txt"):
        # Traiter les fichiers texte
        print(f"Traitement du fichier texte : {filename}")
        segments = extract_and_segment_txt(file_path)
    elif filename.endswith(".pdf"):
        # Traiter les fichiers PDF
        print(f"Traitement du fichier PDF : {filename}")
        segments = extract_and_segment_pdf(file_path)
    else:
        print(f"Fichier ignoré : {filename} (type non supporté)")
        return

    # Récupération de la date au format iso YYYY-MM-DDTHH:MM:SS.ssssss
    current_time = datetime.utcnow().isoformat()

    # Créer des métadonnées pour chaque segment
    print("Création des métadonnées pour chaque segment...")
    for i, segment in enumerate(segments):
        metadata = {
            "file": filename,
            "source": file_path,
            "last_updated": current_time,
            "url": url,
            "segment_index": i
        }
        metadatas.append(metadata)
    print("Création des métadonnées terminée")

    # Indexer les segments et les métadonnées dans ChromaDB
    if segments:
        print(f"Indexation de {len(segments)} segments dans ChromaDB pour le fichier {filename}...")
        vectorize_and_store_in_chroma(segments, metadatas, show_indexation, collection_name)
        print("Indexation terminée.")
        check_collection(collection_name)
    else:
        print("Aucun segment à indexer.")

# Test
if __name__ == "__main__":
    directory_path = get_path("Process_documents/test_data")

    if check_collection("test_chromaDB")> 0:
        # Supprimer l'ancienne BDD
        delete_collection("test_chromaDB")

    # Traiter et stocker les documents dans ChromaDB
    process_and_store_documents(directory_path, "sample.pdf", url="", show_indexation=True, collection_name="test_chromaDB")

    # Test de recherche
    query = "Caractéristiques chat persan."
    results = search_in_chroma(query, n_results=2, collection_name="test_chromaDB")
    print(f"Résultat de la recherche, {query}: {results}")

    # Vérification du nombre de documents dans la collection
    # hors de la fonction process_and_store_documents
    print(f"\nVérification du nombre de documents dans la collection "
          f"hors de la fonction process_and_store_documents")
    check_collection("test_chromaDB")