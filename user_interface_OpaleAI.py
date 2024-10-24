# user_interface_OpaleAI.py

import streamlit as st
import os
import time

from RAG_module.Retrieve_generation.RAG_pipeline import rag_pipeline
from RAG_module.Process_documents.vectorization_and_storage import check_collection, delete_collection, project_root
from RAG_module.Process_documents.process_document import process_and_store_documents, get_path

from web_module.arborescence_scraper import scrape_arborescence_website
from web_module.manage_scraping import scan_web_list, add_website

# Titre de l'application
st.title("OpaleAI")

project_root = os.path.abspath(os.path.dirname(__file__))
print(f"Project root: {project_root}")

# --- Bloc 1 ---

# Champ de saisie pour la requête utilisateur
user_query = st.text_input("Entrez votre requête :", "")

# Bouton pour soumettre la requête
if st.button("Envoyer"):
    if user_query:
        response = rag_pipeline(user_query, model="mistral-nemo", n_results=5, show_full_prompt=False)
        # Afficher la réponse
        st.write("Réponse :", response)
    else:
        st.error("Veuillez entrer une requête valide.")

st.header("Manage collection")
# Bouton pour supprimer la collection et traiter les fichiers du répertoire Documents
if st.button("Delete all the collection and process from Documents directory"):
    delete_collection() # On supprime la collection
    st.write("Collection complètement supprimée.")

    directory = "/home/pi-project-admin/PycharmProjects/OpaleAI/RAG_module/Documents"
    st.write(f"Traitement des fichiers du dossier {directory} en cours...")

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            # Exemple de nom de fichier issu de site web: [example.com][depth0].txt
            if filename.startswith("[") and "][" in filename:
                # Extraire l'URL du nom de fichier
                url = filename.split("][")[0][1:]  # Supprimer le '[' initial
            else:
                url = ""
            # Appeler la fonction pour traiter et stocker les documents
            process_and_store_documents(directory, filename, url)
    st.success("La collection a été supprimée et les documents ont été traités.")

# Bouton pour lancer le scraping de la liste de sites web
if st.button("Process arborescence scraping of the website list"):
    file_path = os.path.join(project_root, "web_module/website_list.csv")
    scan_web_list(file_path)
    st.success("Le scraping de la liste de sites web a été effectué.")

# Espace à droite pour afficher diverses informations
with st.sidebar:
    st.header("Informations")

    if st.button("Update"):
        segments_in_collection = check_collection()
        st.write("Segments dans la collection :", segments_in_collection)

# --- Bloc 2 ---

st.header("Ajouter un site à scraper et mettre à jour la base de données")

# Champ de saisie pour l'URL du site à scraper
url_to_scrape = st.text_input("Entrez l'URL du site à scraper :", "")

# Champ pour spécifier la profondeur de l'arborescence
depth = st.number_input("Profondeur de l'arborescence :", min_value=0, max_value=10, value=1)

# Bouton pour lancer le scraping
if st.button("Scraper le site"):
    # Vérifier que l'URL n'est pas vide
    if url_to_scrape:

        # on enregistre l'url dans notre list
        file_path = get_path("web_module/")
        with open(file_path / "website_list.csv", "a") as web_list:
            web_list.write(url_to_scrape)
            web_list.write(',')
            web_list.write(depth)
            web_list.write(',\n') # à améliorer pour gére les doublons dans la liste

        scrape_arborescence_website(url_to_scrape, max_depth=depth)
        st.success(f"Le site {url_to_scrape} a été ajouté à la base de données avec une profondeur de {depth}.")
    else:
        st.error("Veuillez entrer une URL valide.")

# --- Bloc 3 : Ajout de document ---
st.header("Ajouter un document à la collection")

# Permettre à l'utilisateur de télécharger un fichier
uploaded_file = st.file_uploader("Choisissez un fichier", type=["pdf", "txt"])

# Bouton pour enregistrer le fichier
if st.button("Enregistrer le fichier"):
    if uploaded_file is not None:
        save_directory = os.path.join(project_root, "/RAG_module/Documents")

        # Définir le chemin complet du fichier
        file_path = os.path.join(save_directory, uploaded_file.name)
        print(f"file_path: {file_path}")

        # Enregistrer le fichier dans le dossier défini
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        process_and_store_documents(save_directory, uploaded_file.name)

        st.success(f"Le fichier {uploaded_file.name} a été enregistré avec succès dans {save_directory}.")
    else:
        st.error("Veuillez sélectionner un fichier à télécharger.")


# pour lancer le programme
# streamlit run user_interface_OpaleAI.py
