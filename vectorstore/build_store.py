import json
import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")

CHUNKS_DIR = "data/chunks/"
DB_DIR = "vectorstore/chroma_db/"

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=key)

def load_chunks():
    all_chunks = []
    for fname in os.listdir(CHUNKS_DIR):
        if fname.endswith("_chunks.json"):
            with open(os.path.join(CHUNKS_DIR, fname), "r", encoding="utf-8") as f:
                file_chunks = json.load(f)
                all_chunks.extend(file_chunks)
    return all_chunks

def build_chroma():
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks for embedding and storage.")
    texts = [chunk['text'] for chunk in chunks]
    metadatas = [
        {
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "chunk_id": chunk["chunk_id"],
            "source_file": chunk["source_file"],
            "content_type" : chunk["content_type"]
        }
        for chunk in chunks
    ]
    ids = [chunk["chunk_id"]for chunk in chunks]

    db = Chroma(
        collection_name="medical_chunks",
        embedding_function=embeddings,
        persist_directory=DB_DIR,
    )

    db.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    db.persist()
    print(f"Chroma vector store built and persisted at {DB_DIR} with {len(texts)} chunks")

if __name__ == "__main__":
    build_chroma()