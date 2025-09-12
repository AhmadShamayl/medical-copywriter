import os
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BASE_URL = "https://api.tavily.com/search"

def web_retreive(query: str, max_results: int =5):
    if not TAVILY_API_KEY:
        raise ValueError("Missing TAVILY_API_KEY")
    
    resp = requests.post(
        BASE_URL,
        json = {"api_key": TAVILY_API_KEY, "query": query, "num_results": max_results}
    )

    resp.raise_for_status()
    data = resp.json()

    results = []
    for i , r in enumerate(data.get("results" , [])):
        results.append({
            "doc_id" : f"tavily_{i+1}",
            "title" :  r.get("title") or "No Title",
            "text" : r.get("content") or "",
            "source" : "web",
            "url" : r.get("url"),
            "authors" : [],
            "year" : None
        })
    return results

