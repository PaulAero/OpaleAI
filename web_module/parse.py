from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the user query: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
    "5. **answers in the user's language:** reply in the user's language unless explicitly asked to reply in another language"
    "6. **Contextual Information**: you're part of a parsing pipeline don't be distracted by any off-topic publicity. {context}"
)

model = OllamaLLM(model="llama3.1")


def parse_with_ollama(dom_chunks, parse_description, store_interaction=False):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []
    context = ""

    with open("store_LLM_interaction.txt", 'w') as file:
        pass # on vide le contenu du fichier

    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description, "context": context}
        )

        if store_interaction:
            with open("store_LLM_interaction.txt", "a") as file:
                file.write(f"\nInteraction {i} of {len(dom_chunks)}\n###############################\n"
                           f"INPUT: chunk, {chunk}\n"
                           f"parse_description, {parse_description}\n"
                           f"##############################\nOUTPUT: {response}")

        print(f"Parsed batch: {i} of {len(dom_chunks)}")
        parsed_results.append(response)

        context = (f"Additional context: the full text is too long to be sent at once. "
                   f"You have already reviewed part of the text and answered this: '{"\n".join(parsed_results)}'. "
                   f"Now, continue based on the new content provided. "
                   f"If you have nothing new to add, please respond with ''.")

    return "\n".join(parsed_results)
