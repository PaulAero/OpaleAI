# module pour mettre à jour la base de données chromaDB selon les documents de l'utilisateur
import os
import time
import threading
from pathlib import Path  # Import de Path pour gérer les chemins
from RAG_module.Process_documents.process_document import get_path, process_and_store_documents
from RAG_module.Process_documents.vectorization_and_storage import get_with_metadatas, delete_in_collection

# Retourne un dictionnaire contenant les noms de fichiers et leurs dates de dernière modification.
def get_files_with_timestamps(directory):
    directory = Path(directory)  # S'assurer que directory est un objet Path
    files = {f.name: f.stat().st_mtime for f in directory.iterdir() if f.is_file()}
    return files

# Surveille les changements dans un dossier (nouveaux fichiers, fichiers modifiés ou supprimés).
def monitor_directory(directory, interval=20, test_mode=False):
    directory = Path(directory)  # S'assurer que directory est un objet Path
    print(f"Surveillance du dossier : {directory}")
    previous_files = get_files_with_timestamps(directory)
    iterations = 0

    while True:
        time.sleep(interval)  # Attendre l'intervalle spécifié
        current_files = get_files_with_timestamps(directory)

        if test_mode == True:
            # Afficher les fichiers actuels et précédents
            print(f"\nFichiers précédents : {list(previous_files.keys())}")
            print(f"Fichiers actuels : {list(current_files.keys())}")
            collection_name = "test_chromaDB"
        else:
            collection_name = "document_embeddings"

        # Vérifier les nouveaux fichiers
        new_files = [f for f in current_files if f not in previous_files]
        if new_files:
            for file in new_files:
                print(f"Nouveau fichier détecté : {file}")
                # on vectorise dans la base documentaire par défaut chromaDB
                process_and_store_documents(str(directory), file, url="", show_indexation=False, collection_name=collection_name)

        # Vérifier les fichiers modifiés
        modified_files = [f for f in current_files if f in previous_files and current_files[f] > previous_files[f]]
        if modified_files:
            for file in modified_files:
                print(f"Fichier modifié détecté : {file}")
                # supprimé les anciens vecteurs puis revectoriser
                delete_in_collection(filter_field="file", filter=file, collection_name=collection_name)
                process_and_store_documents(str(directory), file, url="", show_indexation=False, collection_name=collection_name)

        # Vérifier les fichiers supprimés
        deleted_files = [f for f in previous_files if f not in current_files]
        if deleted_files:
            for file in deleted_files:
                print(f"Fichier supprimé détecté : {file}")
                delete_in_collection(filter_field="file", filter=file, collection_name=collection_name)

        # Mettre à jour l'état des fichiers
        previous_files = current_files

        # Si on est en mode test, limiter à 10 itérations
        if test_mode:
            iterations += 1
            if iterations >= 5:
                break

# Fonction de test pour créer, modifier et supprimer un fichier
def test_monitor():
    path_to_watch = Path("test_data")  # Utilisation de Path pour gérer les chemins
    try:
        # S'assurer que le dossier existe
        if not path_to_watch.exists():
            path_to_watch.mkdir()

        # Démarrer la surveillance en mode test (test_mode=True)
        monitor_thread = threading.Thread(target=monitor_directory, args=(path_to_watch, 2, True))
        monitor_thread.start()

        time.sleep(3)  # S'assurer que la surveillance a démarré

        # Créer un fichier dans le dossier surveillé
        test_file = path_to_watch / "test_monitor.txt"
        with test_file.open("w") as f:
            f.write("Fichier de test")
        print(f"\nFichier de test créé : {test_file}")

        time.sleep(3)  # Laisser le temps à la surveillance de détecter le fichier

        # Modifier le fichier pour déclencher une détection de modification
        with test_file.open("a") as f:
            f.write("\nModification du fichier.")
        print(f"\nFichier de test modifié : {test_file}")

        time.sleep(3)  # Laisser le temps à la surveillance de détecter la modification

        # Supprimer le fichier
        test_file.unlink()
        print(f"\nFichier de test supprimé : {test_file}")

        time.sleep(3)  # Laisser le temps à la surveillance de détecter la suppression

        monitor_thread.join()  # Attendre la fin du thread de surveillance
        print("Test terminé.")

    except Exception as e:
        print(f"Erreur durant la surveillance du dossier {path_to_watch}")
        print(e)