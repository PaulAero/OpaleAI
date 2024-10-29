# Introduction

The goal is to build a basic chatbot to assist French users of the Op\@le software. This is a discovery project for me regarding RAG architecture, and I am not a professional developer. The project should operate with minimal cost and be locally viable. Therefore, Ollama is preferred for its ease of use and scalability (it is easy to change the model used).

Contact: Paulaero on Discord if you want. The GitHub repository link will be available soon.

# Current Project Architecture

### Processing a User Query

The current pipeline is as follows:
- The user's request is directly sent to ChromaDB to search for semantically similar content in the database (based on cosine distance).
- The top 5 results are sent as context to the LLM.
- The LLM responds, and its response along with the documents used to generate the answer are displayed to the user.

Current Prompt:

```python
prompt = (f"**Generate Response to User Query**\n"  
          f"**Step 1: Parse Context Information**\n"  
          f"Extract and utilize relevant knowledge from the provided context within `<context></context>` XML tags.\n"  
          f"**Step 2: Analyze User Query**\n"  
          f"Carefully read and comprehend the user's query, pinpointing the key concepts, entities, and intent behind the question.\n"  
          f"**Step 3: Determine Response**\n"  
          f"If the answer to the user's query can be directly inferred from the context information, provide a concise and accurate response in the same language as the user's query.\n"  
          f"**Step 4: Handle Uncertainty**\n"  
          f"If the answer is not clear, ask the user for clarification to ensure an accurate response.\n"  
          f"**Step 5: Avoid Context Attribution**\n"  
          f"When formulating your response, do not indicate that the information was derived from the context.\n"  
          f"**Step 6: Respond in User's Language**\n"  
          f"Maintain consistency by ensuring the response is in the same language as the user's query.\n"  
          f"**Step 7: Provide Response**\n"  
          f"Generate a clear and informative response to the user's query, adhering to the guidelines outlined above.\n"  
          f"<context>\n"  
          f"{documents}"  
          f"\n</context>\n"  
          f"User Query: {query}\n")
```

Planned Improvements:
- Reformulate the user's request using an LLM.
- Investigate why the retrieved information for the context is not very relevant (lack of data, no filtering on the maximum distance currently? Should it be added?).
- Revisit the ChromaDB management module as I might not be using it correctly.

Additional Information:
- I chose the Mistral-Nemo model ([https://ollama.com/library/mistral-nemo](https://ollama.com/library/mistral-nemo)) because it offers a large contextual window. However, perhaps with a better context, a larger model with less context might also work.

## Data Processing in RAG

The RAG data pipeline is as follows:
- For standards and other pdf/txt/md documents with little information in image form, these are divided into chunks of 1000 and vectorized (currently using `SentenceTransformer('all-mpnet-base-v2')`).
- PDF tutorials with annotated screenshots go through the following pipeline:
	- A 300 dpi screenshot of each page is taken and sent to the Llava model (13b) to obtain a text transcription of the information on the page.
	- The Llava response is saved to a file and then vectorized.
- Relevant information from forums and other sites also has a dedicated pipeline:
	  - Scraping is done on a list of sites and parts of their tree structure.
	  - Pages are cleaned and divided into chunks.
	  - For each chunk, an LLM is used to extract relevant information.
	  - The responses are saved and vectorized.

Current Data Processing Limitations:
- The descriptions obtained using Llava are completely unusable as the model clearly invents procedures.
- The embedding seems not to work well due to the mixing of French and English in the model responses during data preprocessing.

Example of Language Mixing:

```text
https://blogacabdx.ac-bordeaux.fr/opalefaq/2022/04/07/liste-des-depense-pour-joindre-a-un-or/ 
**Summary:** 
The conversation outlines the steps to retrieve and export spending data for joining a TR (Transversal Recette) at the Académie de Bordeaux. It involves navigating through specific menus, selecting 'DEPENSES', then 'Restitutions' and 'Situation des dépenses engagées'. After filtering transactions, clicking on 'Transactions liées' leads to 'Consultation budgétaire du réalisé comptable'. The final step is exporting the results in .xls format for justifying receipts.

**Key Takeaways:**
1. To access spending data: DEPENSES > Restitutions > Situation des dépenses engagées.
2. Filter transactions, click on 'Transactions liées', then export as .xls for receipt justification.
```

I also have documents entirely in French (e.g., standards in pdf format).

Prompt for Llava:

```python
prompt = (f"""This page is from a French tutorial PDF for the Op@le software. Your task is to translate the visual instructions into a precise, step-by-step guide by focusing on the main, actionable information." 
   Focus on Key Actions: Describe only the primary steps the user needs to perform, such as where to click, fields to fill, or selections to make in the software. 
   Highlight Important Visual Cues: Include any highlighted annotations, especially those in red or boxed text, as these often contain critical information. 
   Omit Minor Details: Skip any visual or text elements that aren’t directly relevant to the main instruction flow, avoiding any unnecessary descriptions that don’t add to the user’s understanding of the main tasks. 
   List Format: Use bullet points or numbered lists to make steps easy to follow. 
   Translate Key Terms: Translate critical terms, such as action buttons or section titles, to enhance clarity, while avoiding the addition of unshown information.
The objective is to convey a concise, clear instructional flow that enables the user to follow along without distraction from minor details.""")
encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
```

Prompt for scraping:

```python
template = ("You are tasked with summarizing the following conversation content: {dom_content}. " 
            "Please follow these instructions carefully: \n\n" 
            "1. **Summarize:** Provide a concise summary of the key points of the conversation. "
            "2. **Key Takeaways:** Highlight the main ideas or takeaways from the discussion. Explains what the user need to remember from this conversation."
            "3. **No Extra Content:** Do not include any additional comments or explanations in your response."
            "4. **Contextual Information**: you're part of a parsing pipeline for RAG don't be distracted by any off-topic advertisement. {context}")
```

# Past Architecture

Previously, I attempted segmentation using Spacy (see below), but the resulting segments were too short to be useful.

```python
# Load a spaCy model for sentence segmentation 
nlp = spacy.load('fr_dep_news_trf')  # I also tried other models
max_length = 2500000 # subsequently create a separation of the text if it exceeds this length
nlp.max_length = max_length # Note: about 1 GB for 100,000 characters

def clean_and_segment_text(text):
   text = text.strip() 
   # Use spaCy to segment the text   
   doc_spacy = nlp(text)
   segments = [sent.text.strip() for sent in doc_spacy.sents if len(sent.text.strip()) > 20]
   return segments
```

# Current Issues

Main issues to be resolved:
- The data contained in the RAG is not relevant enough due to the inability to transcribe tutorials into text. Processing this data with the OpenAI API (although paid) is an option. However, the minimum quality necessary to achieve satisfactory results should be assessed. When sending a tutorial file in a normal ChatGPT 4.0 conversation, it correctly extracts the relevant information.
- How to improve the RAG retrieval module. The main lead seems to be related to embedding choice, but managing the French-English mix is challenging.

# Tree of this Project

```bash
.
├── __init__.py
├── log_RAG.txt
├── main.py
├── RAG_module
│   ├── Documents
│   │   ├── [https___www.intendancezone.net_spip.php_article1185][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_article1186][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_article1193][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_page=plan][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_rubrique10][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_rubrique34][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_rubrique4][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_rubrique61][depth1].txt
│   │   ├── [https___www.intendancezone.net_spip.php_rubrique72][depth1].txt
│   │   ├── M9-6_Opale-dec20.pdf
│   │   └── output_test_pages_1_5.pdf
│   │   └── ...
│   ├── __init__.py
│   ├── Pre_process_documents
│   │   ├── context_enrichment.py
│   │   ├── process_pictures_pdf_to_text.py
│   │   ├── __pycache__
│   │   │   ├── context_enrichment.cpython-312.pyc
│   │   │   └── query_picture_description.cpython-312.pyc
│   │   ├── query_picture_description.py
│   │   └── test_data
│   │       ├── chat_clean.txt
│   │       ├── chat.pdf
│   │       ├── output_test_pages_1_5_clean.txt
│   │       └── output_test_pages_1_5.pdf
│   ├── Process_documents
│   │   ├── auto_update.py
│   │   ├── __init__.py
│   │   ├── process_document.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── process_document.cpython-312.pyc
│   │   │   ├── test_document_processing.cpython-312.pyc
│   │   │   ├── text_cleaning_and_segmentation.cpython-312.pyc
│   │   │   └── vectorization_and_storage.cpython-312.pyc
│   │   ├── test_data
│   │   │   ├── extrait_txt_brut_M9_6.txt
│   │   │   ├── sample.pdf
│   │   │   └── sample.txt
│   │   ├── test_document_processing.py
│   │   ├── text_cleaning_and_segmentation.py
│   │   └── vectorization_and_storage.py
│   ├── __pycache__
│   │   └── __init__.cpython-312.pyc
│   ├── Retrieve_generation
│   │   ├── generation.py
│   │   ├── log_RAG.txt
│   │   ├── __pycache__
│   │   │   ├── generation.cpython-312.pyc
│   │   │   ├── RAG_pipeline.cpython-312.pyc
│   │   │   └── retrieve.cpython-312.pyc
│   │   ├── RAG_pipeline.py
│   │   └── retrieve.py
│   └── test_framework
│       ├── test_chromaDB.py
│       ├── test_ollama.py
│       └── test_spacy_gpu.py
├── requirements.txt
├── user_interface_OpaleAI.py
├── user_personal_documents
└── web_module
   ├── arborescence_scraper.py
   ├── cleaned_content.txt
   ├── geckodriver
   ├── html_page_source.txt
   ├── __init__.py
   ├── manage_scraping.py
   ├── parse_for_RAG.py
   ├── parse.py
   ├── __pycache__
   │   ├── arborescence_scraper.cpython-312.pyc
   │   ├── __init__.cpython-312.pyc
   │   ├── manage_scraping.cpython-312.pyc
   │   ├── parse.cpython-312.pyc
   │   └── parse_for_RAG.cpython-312.pyc
   ├── scraper.py
   ├── store_LLM_interaction.txt
   └── website_list.csv

16 directories, 498 files
```

# Annexes

#### Hardware Information:

- **Hardware Model:**                         Micro-Star International Co., Ltd. MS-7D75
- **Memory:**                                 64.0 GiB
- **Processor:**                              AMD Ryzen™ 9 7900X × 24
- **Graphics Card:**                          NVIDIA GeForce RTX™ 4070 Ti SUPER
- **Disk Capacity:**                          1.0 TB

#### Software Information:

- **Firmware Version:**                       1.D0
- **OS Name:**                                Ubuntu 24.04.1 LTS
- **OS Build:**                               (null)
- **OS Type:**                                64-bit
- **GNOME Version:**                          46
- **Windowing System:**                       X11
- **Kernel Version:**                         Linux 6.8.0-47-generic

Python version used: 3.12 in a virtual environment.

#### ChromaDB Management Module:

```python
# vectorization_and_storage.py 
import chromadb 
import uuid 
import os 

from sentence_transformers import SentenceTransformer 
from chromadb.config import Settings 
from typing import List 

# Get the absolute path of the project root directory 
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
persist_directory = os.path.join(project_root, ".chromadb")

print(f"ChromaDB persistence directory: {persist_directory}")

# Initialize ChromaDB client with absolute path 
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
   Retrieve ChromaDB collection by providing the embedding function.
   """
   return client.get_or_create_collection( 
       name=collection_name, 
       embedding_function=embedding_function 
   )

# Store segments and metadata in ChromaDB.
def vectorize_and_store_in_chroma(segments, metadatas, show_indexation=False, collection_name="document_embeddings"): 
   collection = get_chroma_collection(collection_name)

   # Generate unique IDs (UUID) for each segment 
   ids = [str(uuid.uuid4()) for _ in segments]

   # Add documents to ChromaDB without providing embeddings 
   collection.add( 
       ids=ids, 
       documents=segments, 
       metadatas=metadatas 
   )

   if show_indexation == True: 
       # Check collection content after addition 
       stored_documents = collection.get(include=['documents', 'metadatas']) 
       print("\nIndexing") 
       print(f"Indexed documents: {stored_documents['documents']}") 
       print(f"Indexed metadata: {stored_documents['metadatas']}")

def search_in_chroma(query, n_results=2, collection_name="document_embeddings"): 
   """ 
   Perform search in ChromaDB with a textual query (query_texts).
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
       Perform search in ChromaDB with a textual query (query_texts) filtered by segment index (!=ids).
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
   print(f"Collection {collection_name} deleted")

def check_collection(collection_name="document_embeddings"): 
   collection = get_chroma_collection(collection_name) 
   count = collection.count() 
   print(f"Number of documents in collection {collection_name}: {count}") 
   return count

def delete_in_collection(filter_field="", filter="", collection_name="document_embeddings"): 
   collection = get_chroma_collection(collection_name) 
   collection.delete( 
       where={filter_field: filter} 
   ) 
   print(f"Elements deleted from {collection_name} with filter: {filter_field} = {filter}")
```

#### Pipeline to process a document

```python
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

# Returns the absolute path of the input folder.
def get_path(directory): 
   # Retrieve the parent directory of the current file 
   current_file_path = Path(__file__).resolve().parent 
   # Build the path to the folder 
   my_documents_dir = current_file_path.parent / directory 
   return my_documents_dir

# process to vectorize a document
def process_and_store_documents(directory, filename, url="", show_indexation=False, collection_name="document_embeddings"): 
   file_path = os.path.join(directory, filename)

   if not os.path.exists(file_path): 
       print(f"File {filename} not found in directory {directory}.") 
       return

   metadatas = []

   # Check if it is a text or PDF file 
   if filename.endswith(".txt"): 
       # Process text files 
       print(f"Processing text file: {filename}") 
       segments = extract_and_segment_txt(file_path) 
   elif filename.endswith(".pdf"): 
       # Process PDF files 
       print(f"Processing PDF file: {filename}") 
       segments = extract_and_segment_pdf(file_path) 
   else: 
       print(f"File ignored: {filename} (unsupported type)") 
       return

   # Retrieve the date in ISO format YYYY-MM-DDTHH:MM:SS.ssssss 
   current_time = datetime.utcnow().isoformat()

   # Delete data if it is a modification of a document 
   try: 
       delete_in_collection(filter_field="file", filter=filename, collection_name=collection_name) 
       print("Old document deleted") 
   except Exception as e: 
       print(f"Error during deletion {e}")

   # Create metadata for each segment 
   print("Creating metadata for each segment...") 
   for i, segment in enumerate(segments): 
       metadata = { 
           "file": filename, 
           "source": file_path, 
           "last_updated": current_time, 
           "url": url, 
           "segment_index": i 
       } 
       metadatas.append(metadata) 
   print("Metadata creation completed")

   # Index segments and metadata in ChromaDB 
   if segments: 
       print(f"Indexing {len(segments)} segments in ChromaDB for file {filename}...") 
       vectorize_and_store_in_chroma(segments, metadatas, show_indexation, collection_name) 
       print("Indexing completed.") 
       check_collection(collection_name) 
   else: 
       print("No segments to index.")

# Test 
if __name__ == "__main__": 
   directory_path = get_path("Process_documents/test_data")

   if check_collection("test_chromaDB") > 0: 
       # Delete the old database 
       delete_collection("test_chromaDB")

   # Process and store documents in ChromaDB 
   process_and_store_documents(directory_path, "sample.pdf", url="", show_indexation=True, collection_name="test_chromaDB")

   # Search test 
   query = "Caractéristiques chat persan." 
   results = search_in_chroma(query, n_results=2, collection_name="test_chromaDB") 
   print(f"Search result, {query}: {results}")

   # Check the number of documents in the collection 
   # outside of the process_and_store_documents function 
   print(f"\nChecking the number of documents in the collection " 
         f"outside of the process_and_store_documents function") 
   check_collection("test_chromaDB")
```

Llava associated function :

```python
def describe_image(image_path, output_folder= "output_description"): 
   # Load and encode the image as base64 
   with open(image_path, "rb") as image_file: 
       encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

   prompt=(f"""This page is from a French tutorial PDF for the Op@le software. Your task is to translate the visual instructions into a precise, step-by-step guide by focusing on the main, actionable information."
   Focus on Key Actions: Describe only the primary steps the user needs to perform, such as where to click, fields to fill, or selections to make in the software.
   Highlight Important Visual Cues: Include any highlighted annotations, especially those in red or boxed text, as these often contain critical information.
   Omit Minor Details: Skip any visual or text elements that aren’t directly relevant to the main instruction flow, avoiding any unnecessary descriptions that don’t add to the user’s understanding of the main tasks.
   List Format: Use bullet points or numbered lists to make steps easy to follow.
   Translate Key Terms: Translate critical terms, such as action buttons or section titles, to enhance clarity, while avoiding the addition of unshown information.
The objective is to convey a concise, clear instructional flow that enables the user to follow along without distraction from minor details.""")

   # Prepare the payload for the request 
   payload = { 
       "model": "llava:34b", 
       "prompt": prompt, 
       "stream": False, 
       "images": [encoded_image] 
   }

   # Make the POST request to the local server 
   response = requests.post("http://localhost:11434/api/generate", json=payload)

   # Check if the request was successful 
   if response.status_code == 200: 
       response_data = response.json() 
       description = response_data.get("response") 
       print("Description:", description)

       # Ensure the output directory exists 
       if not os.path.exists(output_folder): 
           os.makedirs(output_folder)

       # Save the description to a Markdown file 
       picture_name = image_path.split('/')[-1][:-4] 
       md_name = f"description_{picture_name}.md" 
       md_file_path = os.path.join(output_folder, md_name) 
       with open(md_file_path, "w", encoding="utf-8") as md_file: 
           md_file.write("# Image Description\n\n") 
           md_file.write(description)

       return description 
   else: 
       print(f"Request failed with status code: {response.status_code}") 
       return ""
```

