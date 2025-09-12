from mcp.rag_pipeline import generate_answer

query = "What are the latest treatment methods for diabetic retinopathy?"
answer = generate_answer(query, sources=["chroma", "pubmed"], max_results=3)

print("💬 Answer:\n", answer)
