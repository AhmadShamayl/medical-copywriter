from retrievers.pubmed_retriever import pubmed_retrieve

def mcp_retrieve(query, sources= ["pubmed"], max_results = 5) -> list[dict]:
    results = []

    if "pubmed" in sources:
        try:
            pubmed_results = pubmed_retrieve(query, max_results =max_results)
            results.extend(pubmed_results)
        except Exception as e:
            print(f"[MCP] PubMed retriever failed: {e}")



    return results