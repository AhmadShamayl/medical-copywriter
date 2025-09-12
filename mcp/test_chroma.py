from mcp.orchestrator import mcp_retrieve

if __name__ == "__main__":
    query = "diabetic retinopathy treatment"
    results = mcp_retrieve(query, sources=["chroma"], max_results=3)

    if not results:
        print("No results found in Chroma.")
    else:
        for r in results:
            print(f"[{r.get('source','?').upper()}] {r.get('title','Unknown')}")
            print(r.get('text', '')[:300], "...\n")
