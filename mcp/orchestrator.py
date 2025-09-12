from retrievers.pubmed_retriever import pubmed_retrieve
from retrievers.web_retriever import web_retreive   
from retrievers.chroma_retriever import chroma_retrieve


def mcp_retrieve(query, sources= ["pubmed" ,"web" , "chroma"], max_results = 5) -> list[dict]:
    results = []

    if "pubmed" in sources:
        try:
            pubmed_results = pubmed_retrieve(query, max_results =max_results)
            results.extend(pubmed_results)
        except Exception as e:
            print(f"[MCP] PubMed retriever failed: {e}")

    if "web" in sources:
        try:
            web_results = web_retreive(query, max_results = max_results)
            results.extend(web_results)
        except Exception as e:
            print(f"[MCP] Web retriever failed: {e}")

    if "chroma" in sources:
        try:
            chroma_results = chroma_retrieve(query , k = max_results)
            results.extend(chroma_results)
        except Exception as e:
            print(f"[MCP] Chroma retriever failed: {e}")

    return results

def mcp_human_review(text: str, decision: str = "pending") -> dict:
    return {
        "doci_id" : "human_review",
        "title" : "Human Review Result",
        "text": text,
        "source" : "human",
        "year" : None,
        "authors" : [],
        "url" : None,
        "status": decision
    }

if __name__ == "__main__":
    "will be defining"

