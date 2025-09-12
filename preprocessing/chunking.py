import os
import re
import json
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
key = os.getenv("GOOGLE_API_KEY")

CLEANED_DIR = "data/cleaned/"
CHUNKS_DIR = "data/chunks/"
os.makedirs(CHUNKS_DIR, exist_ok=True)

embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004" , google_api_key= key)


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]



def semantic_chunking(text: str, max_words: int = 500, sim_threshold: float = 0.6) -> List[str]:
    sentences = split_sentences(text)
    if not sentences:
        return []

    sentence_embeddings = embedding_model.embed_documents(sentences)
    sentence_embeddings = np.array(sentence_embeddings)

    chunks, current, current_len = [], [], 0

    for i, sent in enumerate(sentences):
        words = sent.split()
        wlen = len(words)

        if current_len + wlen > max_words:
            chunks.append(" ".join(current))
            current, current_len = [], 0

        elif current and i > 0:
            sim = cosine_similarity(
                [sentence_embeddings[i]], [sentence_embeddings[i - 1]]
            )[0][0]
            if sim < sim_threshold:
                chunks.append(" ".join(current))
                current, current_len = [], 0

        current.append(sent)
        current_len += wlen

    if current:
        chunks.append(" ".join(current))

    return chunks
def process_file (filepath: str) -> List[Dict]:
    filename = os.path.basename(filepath)
    doc_id = filename.replace(".txt" , "")
    title = re.sub (r"[_\-]+" , " ", doc_id  ).title()

    with open (filepath, 'r' , encoding="utf-8") as f:
        text = f.read()

    chunks = semantic_chunking(text)
    processed_chunks = []

    for i, chunk in enumerate(chunks , start=1):
        chunk_id = f"{doc_id}_{i:04d}"
        metadata = {
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "title": title,
            "source_file": "local_txt",
            "content_type" : "text_book",
            "text": chunk
         }
        processed_chunks.append(metadata)
    
    return processed_chunks

def run_chunking():
    for fnme in os.listdir(CLEANED_DIR):
        if fnme.lower().endswith(".txt"):
            filepath = os.path.join(CLEANED_DIR, fnme)
            print(f"Chunking file: {fnme}")
            try:
                chunks = process_file(filepath)
                output_path = os.path.join(CHUNKS_DIR, f"{fnme.replace('.txt', '_chunks.json')}")
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    json.dump(chunks, out_f, ensure_ascii=False, indent=2)
                print(f"Saved {len(chunks)} chunks to {output_path}")
            except Exception as e:
                print(f"Failed to process {fnme}: {e}")



if __name__ == "__main__":
    run_chunking()