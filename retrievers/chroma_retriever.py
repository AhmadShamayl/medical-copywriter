import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv



load_dotenv()

CHROMA_PERSIST_DIR = "vectorstore/chroma_db"
CHROMA_COLLECTION = "medical_chunks"
CHUNKS_DIR = "data/chunks/"


client = chromadb.PersistentClient(path = CHROMA_PERSIST_DIR)

class LangchainEmbeddingAdapter(embedding_functions.EmbeddingFunction):
    def __init__(self, lc_embedding):
        self.lc_embedding = lc_embedding

    def __call__(self, texts: List[str]) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        return self.lc_embedding.embed_documents(texts)


lc_embedding = GoogleGenerativeAIEmbeddings(
    model = "models/text-embedding-004",
    google_api_key= os.getenv("GOOGLE_API_KEY")
)

embedding_fn = LangchainEmbeddingAdapter(lc_embedding)

collection = client.get_or_create_collection (
    name = CHROMA_COLLECTION, 
    embedding_function = embedding_fn
)


def _ingest_chunks():
    print("[CHROMA] Ingesting local chunks ...")
    docs , metadatas, ids = [] , [] , []

    for fname in os.listdir(CHUNKS_DIR) :
        if not fname.endswith("_chunks.json"):
            continue

        path = os.path.join(CHUNKS_DIR, fname)
        with open(path, 'r' , encoding = "utf-8") as f:
            chunks = json.load(f)

        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            docs.append(chunk["text"])
            metadatas.append({
                "doc_id" : chunk["doc_id"],
                "title" : chunk["title"],
                "source_file" : chunk["source_file"],
                "content_type" : chunk['content_type']
            })
    if not docs:
        print(f"[CHROMA] No chunks found to ingest.")
        return
    
    BATCH_SIZE = 4000
    for i in range (0, len(docs) , BATCH_SIZE):
        batch_docs = docs[i:i+BATCH_SIZE]
        batch_metadatas = metadatas[i:i+BATCH_SIZE]
        batch_ids = ids[i:i+BATCH_SIZE]
        collection.add(documents = batch_docs, metadatas = batch_metadatas , ids = batch_ids)
        print(f"[CHROMA] Ingested Batch {i//BATCH_SIZE+1} with {len(batch_docs)} chunks.")
    
    print(f"[CHROMA] Ingestion complete. Total chunks ingested: {len(docs)}")



def chroma_retrieve(query: str, k: int = 5) -> List[Dict[str, Any]]:
    try:
        results = collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        if not results or not results.get("documents") or not results["documents"][0]:
            print("[CHROMA] No results found. Attempting ingestion...")
            _ingest_chunks()

            results = collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )

        if not results or not results.get("documents") or not results["documents"][0]:
            print("[CHROMA] Still no results after ingestion.")
            return []


        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            output.append({
                "source": "chroma",
                "title": meta.get("title", "Unknown"),
                "doc_id": meta.get("doc_id"),
                "text": doc,
                "distance": dist
            })

        return output

    except Exception as e:
        print(f"[CHROMA ERROR] {e}")
        return []

