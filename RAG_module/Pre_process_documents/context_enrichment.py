import fitz  # PyMuPDF


def prompt_title(donnees):
    # Liste pour stocker les parties de la chaîne
    resultats = []

    try:
        # Parcourir chaque clé et liste associée dans le dictionnaire
        for cle, valeur in donnees.items():
            # Vérifier si la liste associée à la clé n'est pas vide
            if valeur:
                # Ajouter l'élément formaté à la liste des résultats
                resultats.append(f"{cle}: {valeur[0]}")

        # Joindre les éléments de la liste des résultats en une seule chaîne
        return ', '.join(resultats)

    except Exception as error:
        print(f"Exception occurred while making prompt title: {error}")
        print(f"Input data prompt_title {donnees}")
        print(f"type input data: {type(donnees)}")
        return ""

def extract_title(page, last_titles=None):

    if last_titles == None:
        # Initialiser un dictionnaire pour stocker les titres
        titles = {
            "Main title": [],
            "Title1": [],
            "Title2": [],
            "Title3": []
        }
    else:
        titles = last_titles
        # print(f"Prise en compte du titres précédent {last_titles}") # debug

    # Parcourir les blocs de texte et identifier les titres
    try:
        for block in page.get_text("dict")["blocks"]:

            # Vérifier si le bloc contient des lignes
            if "lines" in block:

                for line in block["lines"]:

                    for span in line.get('spans', []):

                        try:
                            #print(f"extract_title/span: {span}")
                            font_size = span.get('size', 0)
                            text = span.get('text', '')

                            # Classifier le texte selon la taille de la police
                            if font_size == 28.0:
                                titles["Main title"].append(text)
                            elif font_size == 20.0:
                                titles["Title1"].append(text)
                            elif font_size == 16.0:
                                titles["Title2"].append(text)
                            elif font_size == 14.0:
                                titles["Title3"].append(text)

                        except Exception as error:
                            print(f"line: {line}")
                            print(f"Exception occurred while extracting title elements in span: {error}")
                # debug
                '''for key, value in block.items():
                    if key != "image":
                        print(f"        extract_title/Bolck: key: {key}  value: {value}")'''

    except Exception as e:
        print(f"Exception occurred while extracting title elements: {e}")
        print(f"Titles: {titles}")

    print(f"Sortie extract_title/titles : {titles}") # debug
    return titles


def extract_context_text(page_text_blocks, image_index):
    """
    Extracts contextual text around the image by avoiding blocks that are images to obtain 500 words.
    """
    context_text = ""
    collected_texts = []

    # Debug: Check the structure of page_text_blocks
    '''print(f"Debug: Structure of page_text_blocks:")
    for i, block in enumerate(page_text_blocks):
        print(f"  Block {i}: {block}")
    print(f"\n       Entrée dans la fonction extract_context_text, index image: {image_index}\n")'''

    # Traverse the blocks before the image, in reverse order
    for i in range(image_index + 1, -1, -1):
        block = page_text_blocks[i]  # Extract the block
        block_type = block[6]  # Get the type of the block (assuming it's at index 6)

        # Ignore blocks that are images (block_type == 1)
        if block_type == 1:
            continue

        # Extract the text from the block (located at index 4)
        block_text = block[4].strip()
        # Voir la construction du context
        # print(f"    extract_context_text/block_text: {block_text}\nlen(block_text): {len(block_text)}\niteration i: {i}\n")  # Debug: Print the block text

        # Ignore empty blocks
        if not block_text:
            continue

        # Add the current block's text
        collected_texts.insert(0, block_text)  # Insert at the start to maintain order

        # Stop collecting if we have enough text
        if len(' '.join(collected_texts)) > 500:
            break

    # Combine the collected texts and take the last 500 characters
    if collected_texts:
        context_text = ' '.join(collected_texts)
        context_text = context_text[-500:]  # Limit to the last 500 characters

    if not context_text:
        print("extract_context_text: Aucun texte significatif trouvé avant cette image")

    return context_text

'''def find_correct_title_for_image(page_text_blocks, image_index, current_titles):
    print(f"Entrée de la fonction find_correct_title_for_image: page_text_blocks:{page_text_blocks} image_index: {image_index} current_titles: {current_titles}")
    """
    Trouve la bonne sous-section de la page à laquelle appartient l'image.
    """
    # Obtenir la position de l'image
    image_position_y = page_text_blocks[image_index][1]  # Coordonnée y de l'image

    # Parcourir les titres et leur position pour déterminer à quel niveau appartient l'image
    for block in page_text_blocks:
        block_text = block[4]
        block_y = block[1]
        print(f"find_correct_title_for_image/block {block} in page_text_blocks")

        # Vérifier si le texte du bloc est un titre et si l'image est en dessous de ce titre
        if block_text in current_titles.values() and block_y < image_position_y:
            # Retourner le titre correspondant
            for key, value in current_titles.items():
                if value == block_text:
                    print(f"    find_correct_title_for_image/ if block_text in current_titles.values() and block_y < image_position_y/ if value == block_text OK")
                    print(f"return: {key} {value}")
                    return key, value
            print(f"find_correct_title_for_image/ if block_text in current_titles.values() and block_y < image_position_y OK")

    print(f"find_correct_title_for_image/ None, None : Aucune correspondance trouvée")
    return None, None  # Aucune correspondance trouvée'''