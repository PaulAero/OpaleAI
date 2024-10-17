from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = (
    "You are tasked with summarizing the following conversation content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Summarize:** Provide a concise summary of the key points of the conversation. "
    "2. **Key Takeaways:** Highlight the main ideas or takeaways from the discussion. Explains what the user need to remember from this conversation."
    "3. **No Extra Content:** Do not include any additional, comments, or explanations in your response."
    "4. **Contextual Information**: you're part of a parsing pipeline for RAG don't be distracted by any off-topic advertisement. {context}"
)

model = OllamaLLM(model="mistral-nemo")

def parse_for_RAG_with_ollama(dom_chunks):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []
    context = ""

    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "context": context}
        )

        print(f"Parsed batch: {i} of {len(dom_chunks)}")
        #print(dom_chunks)
        parsed_results.append(response)

        context = (f"Additional context: the full text is too long to be sent at once. "
                   f"You have already reviewed part of the text and answered this: '{"\n".join(parsed_results)}'. "
                   f"Now, continue based on the new content provided. "
                   f"If you have nothing new to add, please respond with ''.")

    return "\n".join(parsed_results)
