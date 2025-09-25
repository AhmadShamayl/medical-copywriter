import os
from mcp.orchestrator import mcp_retrieve
from openai import OpenAI
from dotenv import load_dotenv
from memory.conversation_memory import HybridConversationMemory


load_dotenv ()

client = OpenAI (api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_PATH = "prompts/system_prompt.txt"


def load_prompt() -> str:
    with open(PROMPT_PATH, "r" , encoding="utf-8") as f:
        return f.read()
    

def generate_answer(query: str, sources = ['chroms', 'pubmed' , 'web'] , max_results = 5, memory: HybridConversationMemory = None, memory_context: str = "") -> str:
    if query.strip().lower() in ["reset memory" , "clear memory" , "start new session"]:
        memory.reset_memory()
    retrieved_docs = mcp_retrieve(query, sources=sources , max_results= max_results)

    if not retrieved_docs:
        return "No relevant information found"
    
    context_parts = []
    sources_out = []
    for doc in retrieved_docs:
        title = doc.get("title", "Unknown")
        text = doc.get("text", "")
        context_parts.append(f"Title: {title}\n{text}\n")

        sources_out.append(
            {
                "title": title,
                "snippet": (text[:400]).strip(),
                "source": doc.get("source", "unknown"),
                "url": doc.get("url"),
            }
        )

    memory_context = memory.load_context() if memory else "No previous conversation"
    context = "\n\n".join(context_parts)

    memory_context = memory.load_context()
    system_prompt = load_prompt ()
    user_prompt = (
        f" ---- MEMORY CONTEXT ----\n{memory_context}\n\n"
        f" ---- RETRIEVED CONTEXT ----\n{context_parts}\n\n"
        f" ---- USER QUESTION ----\n{query}"

    )

    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-0125" , 
        messages= [{'role' : 'user' , "content" : system_prompt},
                   {"role" : "user" , "content" : user_prompt}
                   ],
        temperature= 0.2
    )
    answer_text = response.choices[0].message.content
    memory.save_context(query , answer_text)

    return answer_text
