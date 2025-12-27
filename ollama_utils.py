import requests

def ask_ollama(context, query):
    prompt = f"""You are a helpful AI assistant answering questions about a PDF.

    Use the context below to craft a clear, detailed answer.
    - Do not just repeat the context word-for-word.
    - If the context is short or incomplete, use general knowledge to elaborate.
    - Write in a natural, explanatory tone.

    Context:
    {context}

    Question: {query}

    Answer (detailed):"""

    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False} 
    )
    api_data = response.json()
    text_answer = api_data.get("response", "").strip()
    return text_answer
