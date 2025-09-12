from mcp.orchestrator import mcp_retrieve

query = "risk factors of diabetic retinopathy"
results = mcp_retrieve(query, sources=["chroma"], max_results=5)

if not results:
    print("No results found.")
else:
    for r in results:
        print(f"[{r['source'].upper()}] {r.get('title','')}")
        print(r['text'][:300], "...\n")
