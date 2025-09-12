import os
from mcp.orchestrator import mcp_retrieve
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv ()

client = OpenAI (api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_PATH = "prompts/reAct_prompt.txt"


def load_prompt() -> str:
    with open(PROMPT_PATH, "r" , encoding="utf-8") as f:
        return f.read()
    

def generate_answer(query: str, sources = ['chroms', 'pubmed' , 'web'] , max_results = 5) -> str:
    retrieved_docs = mcp_retrieve(query, sources=sources , max_results= max_results)

    if not retrieved_docs:
        return "No relevant information found"
    
    context_parts = []
    for doc in retrieved_docs:
        title = doc.get('title' , "Unknown")
        text = doc.get('text' , "")
        context_parts.append(f"Title: {title}\n{text}\n")

    context = "\n\n".join(context_parts)

    base_prompt = load_prompt ()
    full_prompt = base_prompt.format(query=query, context = context)

    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-0125" , 
        messages= [{'role' : 'user' , "content" : full_prompt}],
        temperature= 0.2
    )

    return response.choices[0].message.content
