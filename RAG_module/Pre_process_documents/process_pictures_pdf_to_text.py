import fitz  # PyMuPDF
import os
import tempfile
import requests
import base64
import json

from context_enrichment import extract_title, extract_context_text, prompt_title
from query_picture_description import query_ollama_picture_pipeline


def process_pdf_to_text(pdf_path, output_text_path):
    print(f"PDF path: {pdf_path}")
    # Create a temporary directory to save images
    temp_dir = tempfile.mkdtemp()
    custom_promt = ""
    last_titles = None  # None pour qu'on aille pas chercher le dernier titre lors la première itération

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    full_text = ""

    # Process each page individually
    for page_number in range(len(pdf_document)):
        try:
            print(f"Processing page {page_number + 1}/{len(pdf_document)}...")
            page = pdf_document[page_number]

            # Extract images from the current page
            image_list = page.get_images(full=True)
            print(f"Found {len(image_list)} images on page {page_number + 1}")


            if len(image_list)<3:
                # Obtenir les blocs de texte (renvoie une liste de rectangles et leur contenu textuel)
                page_text_blocks = page.get_text("blocks")
                # print(f"\nprocess_pdf_to_text/page_text_blocks = page.get_text(blocks) effectué") # debug

                # Mettre à jour les titres actuels en fonction de la page et récupérer le prompt des titres
                # print(f"process_pdf_to_text appel extract_title pour mise à jour des titres") # debug
                titles = extract_title(page, last_titles)
                last_titles = titles
                print(
                    f"process_pdf_to_text/titles: {titles} (titres récupérés via context_enrichment/extract_title)\n")  # debug

                # Insert image placeholders
                for img_index, img in enumerate(image_list):
                    # Get image coordinates
                    xref = img[0]
                    image_rect = page.get_image_rects(xref)[0]  # Get the first occurrence of the image
                    img_x0, img_y0, img_x1, img_y1 = image_rect

                    # Find the closest text block to the image
                    closest_block_index = -1
                    min_distance = float('inf')

                    for i, block in enumerate(page_text_blocks):
                        # Extract only relevant elements: coordinates and text
                        block_x0, block_y0, block_x1, block_y1, block_text = block[0], block[1], block[2], block[3], block[
                            4]
                        # Calculate the distance between the image and the text block
                        distance = abs(block_y0 - img_y0)
                        if distance < min_distance:
                            min_distance = distance
                            closest_block_index = i

                    # Insert the placeholder into the closest text block
                    if closest_block_index != -1:
                        block = page_text_blocks[closest_block_index]
                        # Replace the block tuple with updated text content
                        page_text_blocks[closest_block_index] = (
                            block[0], block[1], block[2], block[3],
                            block[4] + f"\n[IMAGE_{img_index + 1}]\n",
                            block[5], block[6]  # Include the rest of the original elements
                        )

                # Combine text blocks to create the full page text
                page_text = ""
                for block in page_text_blocks:
                    page_text += block[4] + "\n"

                # Process images and replace placeholders with descriptions
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_data = base_image["image"]
                    image_ext = base_image["ext"]

                    # Save the image temporarily
                    image_filename = f"image_page{page_number + 1}_{img_index + 1}.{image_ext}"
                    image_filepath = os.path.join(temp_dir, image_filename)
                    with open(image_filepath, "wb") as image_file:
                        image_file.write(image_data)

                    # Extract context text for this image
                    # print(f"process_pdf_to_text/Img index envoyé à extract_context_text: {img_index}") debug
                    context_text = extract_context_text(page_text_blocks, img_index)
                    # print(f"Envoie de titles:{titles} à prompt_title")
                    prompt_titles = prompt_title(titles)
                    # print(f"\nContext envoyé à Ollama: {context_text}")
                    # print(f"Titres envoyés à Ollama: {prompt_titles}\n")

                    # Get description from Ollama with enriched context
                    print(f"    Querying Ollama for image {img_index + 1} on page {page_number + 1}...")
                    description = query_ollama_picture_pipeline(image_filepath, prompt_titles, context_text, custom_promt,
                                                        True)  # Passer le contexte et les titres
                    # print(f"    Description: {description}\n#############################")

                    # Replace the placeholder in the text with the description
                    page_text = page_text.replace(f"[IMAGE_{img_index + 1}]", description, 1)
            else:
                # Convertir la page en image (ici à une résolution de 2.0 x 2.0)
                pix = page.get_pixmap(matrix=fitz.Matrix(7.0, 7.0))
                print(f"Conversion de la page {page_number+1} en image...")
                with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_file:
                    pix.save(temp_file.name)
                    temp_image_path = temp_file.name  # Chemin du fichier temporaire
                    print(f"    Querying Ollama for page {page_number + 1}...")
                    description = query_ollama_picture_pipeline(temp_image_path)
                    page_text = description
            # Add the page text to the full text
            full_text += page_text + "\n\n"

        except Exception as e:
            print(f"Exception occurred while processing page {page_number + 1}: {e}")
            continue

    # Save the full text to a file
    with open(output_text_path, "w") as text_file:
        text_file.write(full_text)

    pdf_document.close()
    print(f"Processed text saved at {output_text_path}")


# Example usage
if __name__ == "__main__":
    # test sur chat.pdf
    '''pdf_path = "test_data/chat.pdf"
    output_text_path = "test_data/chat_clean.txt"
    process_pdf_to_text(pdf_path, output_text_path)'''

    # test sur une partie de doc @Opale
    pdf_path = "test_data/output_test_pages_1_5.pdf"
    output_text_path = "test_data/output_test_pages_1_5_clean.txt"
    process_pdf_to_text(pdf_path, output_text_path)