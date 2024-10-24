# text_cleaning_and_segmentation.py

import re
import spacy
import fitz
from oauthlib.uri_validate import segment

def clean_and_segment_text(text):
    '''
    Nettoie et segmente le texte en phrases ou paragraphes avec spaCy.
    :param text: Texte brut à nettoyer et segmenter.
    :return: Liste de segments de texte nettoyés.
    '''
    text = text.strip()

    # Segmentation par paragraphe
    # print(f"\n Extrait du texte brut: {[text[600000:608000]]}\n")
    segments = text.split(". \n")
    segments = [segment + '. ' for segment in segments if segment]

    combined_segments = []
    current_segment = ""
    min_length = 1000

    for segment in segments:
        if len(segment) < min_length:
            # Si le segment est trop court, on le combine avec le segment en cours
            current_segment += " " + segment
        else:
            if current_segment:
                # Si on a un segment combiné en attente, on l'ajoute à la liste
                combined_segments.append(current_segment.strip())
                current_segment = ""
            combined_segments.append(segment.strip())

    # Ajouter le dernier segment combiné s'il reste quelque chose
    if current_segment:
        combined_segments.append(current_segment.strip())

    return combined_segments

def extract_and_segment_pdf(file_path):
    # dans cette fonction, on pourra mettre des conditions pour récupérer différemment le contenu d'un pdf en fonction de sa nature par exemple
    # norme, tutoriel...
    text = ""
    doc = fitz.open(file_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    print(f"Extract text from:\nfile path {file_path}\nlen(text): {len(text)}")
    return clean_and_segment_text(text)

def extract_and_segment_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # print(f"file path {file_path})")
    print(f"Extract text from:\nfile path {file_path}\nlen(text): {len(text)}")
    return clean_and_segment_text(text)
