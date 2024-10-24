import os
import tempfile
import requests
import base64
import json

def query_ollama_picture_pipeline(image_path, titles_prompt=None, context_text=None, custom_prompt="", show_prompt=False, show_answer=False):
    # Encode the image in base64
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construire le prompt avec les titres
    if titles_prompt:
        titles_section = f"This image is part of the section: {titles_prompt}. "
        # print(f"    query_ollama_pipeline/titles_prompt/test titles_prompt: {titles_prompt}")
    else:
        titles_section = ""

    # Construire le contexte avec les 500 derniers caractères
    if context_text:
        context_section = f"The surrounding context of this image includes: '{context_text}'. "
        # print(f"    query_ollama_pipeline/context_text/test context_section: {context_section}")
    else:
        context_section = ""

    # Step 1: Ask to classify the image into predefined categories
    classification_query_payload = {
        "model": "llava:13b",
        "messages": [
            {
                "role": "user",
                "content": ("Please classify this image into one of the following categories: "
                            "'photo', 'diagram', 'table', 'chart', 'logo', or 'other'. Provide only the category name."),
                "images": [image_data]
            }
        ],
        "stream": False
    }
    if show_prompt:
        filtered_data = [{key: value for key, value in message.items() if key != 'images'}
        for message in classification_query_payload["messages"]]
        print(f"Prompt étape 1 classification: \n{filtered_data}\n"
              f"/!\\ Les données de l'image ne sont pas incluses (key != 'images') pour une meilleure lisibilité du prompt")

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps(classification_query_payload)
        )

        if response.status_code == 200:
            response_data = response.json()
            category = response_data.get("message", {}).get("content", "other").strip().lower()

            # Prepare a detailed query based on the identified category
            if category == "diagram":
                specific_query = ("This image is a diagram that illustrates a specific process or concept in detail. "
                                  "1. Identify and list all the main steps, components, or sections included in the diagram. "
                                  "2. Describe how each component interacts or works together to convey the process or concept. Provide a thorough explanation to enhance the understanding of the diagram. "
                                  "Use the format: 'Steps:', 'Components:', 'Interactions:', 'Overall Purpose:'.")
            elif category == "table":
                specific_query = ("This image contains a table with structured data. "
                                  "1. List all the headers and provide a brief explanation of their significance. "
                                  "2. Highlight key values and trends observed in the table. "
                                  "3. Explain in detail what the table is illustrating or summarizing, including any patterns, comparisons, or insights it offers. "
                                  "Use the format: 'Headers:', 'Key Values:', 'Observed Trends:', 'Summary and Insights:'.")
            elif category == "chart":
                specific_query = ("This image presents a chart that visualizes data or trends. "
                                  "1. Describe the axes, their labels, and the data they represent. "
                                  "2. Identify any significant patterns, trends, or anomalies shown in the chart. "
                                  "3. Provide a detailed explanation of what the chart illustrates, the insights it offers, and any conclusions that can be drawn. "
                                  "Use the format: 'Axes and Labels:', 'Trends and Patterns:', 'Detailed Insights:', 'Conclusions:'.")
            elif category == "logo":
                specific_query = ("This image is a logo designed to represent a brand, organization, or concept. "
                                  "1. Describe in detail each visual element (e.g., symbols, colors, shapes) included in the logo. "
                                  "2. Explain the intended meaning, symbolism, or message behind the design. "
                                  "3. Discuss how the logo reflects the identity or values of the entity it represents. "
                                  "Use the format: 'Elements and Design Features:', 'Symbolism and Meaning:', 'Brand Identity and Message:'.")
            elif category == "photo":
                specific_query = ("This image is a photograph capturing a specific moment or scene. "
                                  "1. Provide a detailed description of the key elements (e.g., people, objects, setting) present in the photo. "
                                  "2. Explain the context or story that this photo conveys, including any emotions, themes, or messages it embodies. "
                                  "Use the format: 'Description of Key Elements:', 'Context and Story:', 'Emotions and Themes:'.")
            else:  # for 'other' category
                specific_query = (
                    "Describe this image in detail. Include information about the key elements, colors, objects, setting,"
                    " and any noticeable actions or emotions present. If possible, infer the context or story that this image might be conveying.")

            # Step 2: Detailed query with a focus on meaning
            detailed_query_payload = {
                "model": "llava:34b",
                "messages": [
                    {
                        "role": "user",
                        "content": f"This image is extracted from a PDF document titled {titles_prompt} It appears alongside the following text: {context_text}."+specific_query+custom_prompt,
                        "images": [image_data]
                    }
                ],
                "stream": False
            }

            if show_prompt:
                filtered_data = [{key: value for key, value in message.items() if key != 'images'}
                for message in detailed_query_payload["messages"]]
                print(f"Prompt étape 2 detailed query: \n{filtered_data}\n "
                f"/!\\ Les données de l'image ne sont pas incluses (key != images) pour une meilleure lisibilité du prompt")

            detailed_response = requests.post(
                "http://localhost:11434/api/chat",
                headers={"Content-Type": "application/json"},
                data=json.dumps(detailed_query_payload)
            )

            # Step 3: Check for vague descriptions and ask for more detail if needed
            if detailed_response.status_code == 200:
                detailed_response_data = detailed_response.json()
                detailed_description = detailed_response_data.get("message", {}).get("content", "No detailed description available")

                # If the description seems too vague, ask for more detail
                #if len(detailed_description) < 50 or "appears to be" in detailed_description.lower():
                if len(detailed_description) < 50:
                    print(f"     Unsatisfactory detailed description:\n{detailed_description}")
                    print("     Ollama process again...")
                    refinement_query = ("The description seems incomplete. Can you provide more specific details about the purpose and meaning of this image?")
                    refinement_payload = {
                        "model": "llava:34b",
                        "messages": [
                            {
                                "role": "user",
                                "content": titles_prompt + context_text + refinement_query,
                                "images": [image_data]
                            }
                        ],
                        "stream": False
                    }
                    refined_response = requests.post(
                        "http://localhost:11434/api/chat",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(refinement_payload)
                    )

                    if refined_response.status_code == 200:
                        refined_response_data = refined_response.json()
                        refined_description = refined_response_data.get("message", {}).get("content", "No further detail available")
                        return refined_description

                return detailed_description
            else:
                return "[Error in detailed description query]"

        else:
            return "[Error in classification query]"
    except Exception as e:
        print(f"Exception while querying Ollama: {e}")
        return "[Exception occurred]"