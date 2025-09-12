from retrievers.chroma_retriever import chroma_retrieve


if __name__ == "__main__" :
    results  = chroma_retrieve("What are the symptoms of diabetes?", k=3)
    if not results:
        print("No results found.")
    else:
        for res in results:
            print(f"[{res['source'].upper()}] {res['title']}")
            print(res['text'][:300], "...\n")