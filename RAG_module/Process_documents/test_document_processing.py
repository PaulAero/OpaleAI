import unittest
import uuid

from RAG_module.Process_documents.text_cleaning_and_segmentation import extract_and_segment_pdf, extract_and_segment_txt
from RAG_module.Process_documents.vectorization_and_storage import vectorize_and_store_in_chroma, search_in_chroma, \
    get_chroma_collection, client, check_collection, delete_collection, get_with_segment, get_with_metadatas, delete_in_collection

class TestDocumentProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("setUpClass...")
        # Tenter de supprimer la collection et ignorer l'erreur si elle n'existe pas
        try:
            # client.delete_collection(name="document_embeddings")
            # client.delete_collection(name="test_chromaDB")
            delete_collection("test_chromaDB")
        except ValueError as e:
            if "does not exist" in str(e):
                pass  # Ignorer l'erreur si la collection n'existe pas
            else:
                raise  # Relancer l'erreur si c'est une autre erreur

        # Indexer les documents nécessaires aux tests
        segments = ["Texte à vectoriser.", "Un autre texte."]
        metadata = [
            {"segment_index": 1, "title": "Doc1", "source": "fichier texte"},
            {"segment_index": 2, "title": "Doc2", "source": "fichier texte"}
        ]
        show_indexation = True
        vectorize_and_store_in_chroma(segments, metadata, show_indexation, "test_chromaDB")
        check_collection("test_chromaDB")

    def test_clean_and_segment_txt(self):
        print("\nTest du nettoyage et segmentation d'un fichier texte brut")
        # Test du nettoyage et segmentation d'un fichier texte brut
        test_file_path = "test_data/sample.txt"
        segments = extract_and_segment_txt(test_file_path)
        self.assertTrue(len(segments) > 0)
        self.assertTrue(all(len(seg) > 20 for seg in segments))

    def test_clean_and_segment_pdf(self):
        print("\nTest du nettoyage et segmentation d'un PDF")
        # Test du nettoyage et segmentation d'un PDF
        test_file_path = "test_data/sample.pdf"
        segments = extract_and_segment_pdf(test_file_path)
        self.assertTrue(len(segments) > 0)
        self.assertTrue(all(len(seg) > 20 for seg in segments))

    def test_vectorize_and_store_in_chroma(self):
        segments = ["Ceci est un test.", "Un autre test.", "Encore un test"]
        metadata = [
            {"segment_index": 3, "title": "Doc3", "source": "fichier texte"},
            {"segment_index": 4, "title": "Doc3", "source": "fichier texte"},
            {"segment_index": 5, "title": "Doc4", "source": "fichier texte"}
        ]
        vectorize_and_store_in_chroma(segments, metadata, True, "test_chromaDB")

        # Obtenir la collection avec la fonction d'embedding
        collection = get_chroma_collection("test_chromaDB")

        results = collection.get(include=['documents', 'metadatas'])
        self.assertGreaterEqual(len(results['documents']), 4)

    def test_search_in_chroma(self):
        query = "Texte à vectoriser."
        results = search_in_chroma(query, 2, "test_chromaDB")
        print("\ntest_search_in_chroma:")
        print(f"Query: {query}")
        print(f"Documents trouvés : {results['documents']}")
        print(f"Métadonnées : {results['metadatas']}")
        print(f"Distances : {results['distances']}")
        self.assertGreaterEqual(len(results['documents'][0]), 1)

    def test_get_with_segment(self):
        print(f"\nTest de la recherche par segment...")
        seg_idx = 1
        result = get_with_segment(seg_idx, "test_chromaDB")
        print(f"seg_idx: {seg_idx} résultat de la recherche: {result}")
        self.assertEqual(len(result["ids"]), 1)

    def test_get_with_metadata(self):
        print(f"\nTest de la recherche avec un élément de métadonnées")
        print("get_with_metadatas(title, Doc1, test_chromaDB)")
        result = get_with_metadatas("title", "Doc1", "test_chromaDB")
        print(result)
        self.assertEqual(len(result["ids"]), 1)

    def test_delete_in_collection(self):
        print(f"\nTest de la suppression d'éléments avec un filtre")
        item_in_collection = check_collection("test_chromaDB")
        delete_in_collection(filter_field="title", filter="Doc2", collection_name="test_chromaDB")
        new_item_in_collection = check_collection("test_chromaDB")
        delta = item_in_collection - new_item_in_collection
        self.assertEqual(delta, 1)

if __name__ == '__main__':
    unittest.main()
