# test_orchestrator.py
from mcp.orchestrator import mcp_retrieve, mcp_human_review

if __name__ == "__main__":
    query = "latest WHO guidelines on hypertension"
    results = mcp_retrieve(query, sources=["pubmed", "web"], max_results=3)

    for r in results:
        print(f"[{r['source'].upper()}] {r['title']}")
        print(r['text'][:200], "...\n")

    # HITL Example
    review = mcp_human_review("Draft medical copy about hypertension", decision="approve")
    print("HITL Review:", review)
