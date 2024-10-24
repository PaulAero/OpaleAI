import csv
import os
import subprocess
from web_module.arborescence_scraper import scrape_arborescence_website


def scan_web_list(file_path, test_mode=False):
    """
    Récupère la liste des sites à scanner depuis un fichier CSV et lance le scraping pour chacun.

    Args:
        file_path (str): Chemin vers le fichier CSV contenant les URLs et les profondeurs.
    """
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 1:
                url = row[0]
                # Vérifier si la profondeur est spécifiée dans la deuxième colonne
                if len(row) >= 2 and row[1].isdigit():
                    depth = int(row[1])
                else:
                    depth = 2  # Profondeur par défaut

                if test_mode == True:
                    print(f"Scraping de {url} avec une profondeur de {depth} (simulé).")
                else:
                    # Appeler la fonction de scraping pour chaque URL
                    scrape_arborescence_website(url, max_depth=depth)


def add_website(url, file_path, depth=2):
    """
    Ajoute un site à la liste des sites à scraper en l'ajoutant au fichier CSV.

    Args:
        url (str): L'URL du site à ajouter.
        file_path (str): Chemin vers le fichier CSV contenant les sites.
        depth (int, optional): Profondeur de scraping. Par défaut à 2.
    """
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([url, str(depth)])
    print(f"Site ajouté : {url} avec une profondeur de {depth}")


def delete_web_site(root_url, file_path):
    """
    Supprime toutes les pages liées à un site en supprimant les entrées correspondantes dans le fichier CSV.

    Args:
        root_url (str): L'URL racine du site à supprimer.
        file_path (str): Chemin vers le fichier CSV contenant les sites.
    """
    temp_file = file_path + '.tmp'
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile_in, \
            open(temp_file, 'w', newline='', encoding='utf-8') as csvfile_out:
        reader = csv.reader(csvfile_in)
        writer = csv.writer(csvfile_out)
        for row in reader:
            if len(row) >= 1:
                url = row[0]
                # Exclure les URLs qui commencent par root_url
                if not url.startswith(root_url):
                    writer.writerow(row)
    os.replace(temp_file, file_path)
    print(f"Toutes les pages liées à {root_url} ont été supprimées.")


def delete_web_page(url_to_delete, file_path):
    """
    Supprime une page web spécifique de la liste en supprimant l'entrée correspondante dans le fichier CSV.

    Args:
        url_to_delete (str): L'URL de la page à supprimer.
        file_path (str): Chemin vers le fichier CSV contenant les sites.
    """
    temp_file = file_path + '.tmp'
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile_in, \
            open(temp_file, 'w', newline='', encoding='utf-8') as csvfile_out:
        reader = csv.reader(csvfile_in)
        writer = csv.writer(csvfile_out)
        for row in reader:
            if len(row) >= 1:
                url = row[0]
                # Exclure l'URL qui correspond exactement à url_to_delete
                if url != url_to_delete:
                    writer.writerow(row)
    os.replace(temp_file, file_path)
    print(f"La page {url_to_delete} a été supprimée de la liste.")

# Fonctions de test
def test_functions():
    # Chemin du fichier CSV de test
    test_csv_file = 'test_websites_list.csv'

    # 1. Création d'un petit fichier CSV pour les tests
    # Si le fichier existe déjà, on le supprime pour un test propre
    if os.path.exists(test_csv_file):
        os.remove(test_csv_file)

    print("=== Test de add_website ===")
    # Ajout de sites au fichier CSV de test
    add_website('https://example.com', test_csv_file, depth=2)
    add_website('https://example.org', test_csv_file, depth=3)
    add_website('https://example.com/page', test_csv_file, depth=1)

    # Affichage du contenu du fichier CSV après les ajouts
    with open(test_csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        print("\nContenu du fichier CSV après ajout :")
        reader = csv.reader(csvfile)
        for row in reader:
            print(row)

    print("\n=== Test de scan_web_list ===")
    # Appel de la fonction scan_web_list (ici on peut commenter l'appel à scrape_arborescence_website pour éviter un vrai scraping)
    scan_web_list(test_csv_file, test_mode=True)
    print("Fonction scan_web_list exécutée (scraping simulé).")

    print("\n=== Test de delete_web_page ===")
    # Suppression d'une page spécifique
    delete_web_page('https://example.com/page', test_csv_file)

    # Affichage du contenu du fichier CSV après suppression de la page
    with open(test_csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        print("Contenu du fichier CSV après suppression de la page :")
        reader = csv.reader(csvfile)
        for row in reader:
            print(row)

    print("\n=== Test de delete_web_site ===")
    # Suppression de toutes les pages liées à 'https://example.com'
    delete_web_site('https://example.com', test_csv_file)

    # Affichage du contenu du fichier CSV après suppression du site
    with open(test_csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        print("Contenu du fichier CSV après suppression du site :")
        reader = csv.reader(csvfile)
        for row in reader:
            print(row)

    # Nettoyage du fichier CSV de test
    if os.path.exists(test_csv_file):
        os.remove(test_csv_file)
    print("\nTests terminés. Fichier de test supprimé.")


if __name__ == "__main__":
    test_functions()