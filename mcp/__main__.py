from mcp.orchestrator import mcp_retrieve


def main():
    print("Running MCP Package...")


if __name__ == "__main__":
    main()
    query = "latest treatment for diabetic retinopathy"
    results = mcp_retrieve(query, sources=["pubmed"], max_results=5)
    for r in results:
        print(f"[{r['source'].upper()}] {r['title']} ({r['year']})")
        print(f"Authors: {', '.join(r['authors'])}")
        print(f"Link: {r['url']}")
        print(r['text'][:300], "...\n")
    