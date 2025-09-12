import os
from fastmcp import FastMCP
from typing import List, Dict  , Any
from retrievers.pubmed_retriever import pubmed_retrieve
import chromadb
from chromadb.config import Settings
from retrievers.web_retriever import web_retreive


mcp = FastMCP(
    name = "Medical Copywriter - MCP Server",
    instructions="Provides medical retirevers (PubMed abstracts and CHroma local docs)" 
)



CHROMA_PERSIST_DIR = "vectorstore/chroma_db"
CHROMA_COLLECTION = "medical_chunks"

chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_PERSIST_DIR
))

try:
     chroma_collection = chroma_client.get_collection(name=CHROMA_COLLECTION)
except Exception:
     chroma_collection = None

def _normalize_chroma_results(query: str, query_result: Dict[str, Any] ) -> List[Dict]:
     docs = []
     ids = query_result.get("ids" , [[]])[0]
     docs_text = query_result.get("documents" , [[]])[0]
     metadatas = query_result.get("metadatas" , [[]])[0]

     for _id, text , meta in zip (ids, docs_text , metadatas):
            docs.append({
                 "doc_id" : _id,
                 "title" : meta.get("title") if meta else meta.get("doc_id")if meta else None,
                 "text" : text,
                 "source" : "chroma",
                 "url" :None,
                 "authors" : meta.get("authors", []) if meta else [],
                 "year" : meta.get("publish_year") if meta else None,
                 "metadata" : meta or {}
                })
     return docs

@mcp.tool(name = "pubmed_retrieve" , description = "Search Pubmed and return normalized results. Input: {query: str, max_results: int}")
def pubmed_tool (input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
     query = input_data.get("query" , "")
     max_results = input_data.get("max_results" , 5)
     if not query:
          return []
     try:
          results = pubmed_retrieve(query, max_results=max_results)
          return results
     except Exception as e:
          return [{"error" : str(e)}]


@mcp.tool(name = "chroma_retrieve" , description = "Search Chroma vector store and return normalized results. Input: {query: str, max_results: int}")
def chroma_tool (input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
     if chroma_collection is None:
          return [{"error" : "Chroma collection not available on server"}]

     q = input_data.get("quer" , "")
     k = int(input_data.get("k" , 5))
     if not q:
          return []
     try:
          res = chroma_collection.query(
               query_text = [q],
               n_results = k,
                include = ["documents" , "metadatas" , "ids"]

          )
          normalized  = _normalize_chroma_results(q, res)
          return normalized
     except Exception as e:
          return [{"error" : str(e)}]
     

@mcp.tool(name = "web_retrieve" , description = "Search web and return using Tavily API. Input: {query: str, max_results: int}")
def web_tool(input_data : dict):
     query = input_data.get("query" , "")
     max_results = int(input_data.get("max-results" , 5))
     if not query:
          return []
     try:
          results = web_retreive(query, max_results = max_results)
          return results
     except Exception as e:
          return [{"error" : str(e)}]

     

@mcp.tool(name = "human_review" , description = "Send contetn for human review. Input: {text: str, decision:str (approve/reject/modify)}")
def human_review_tool (input_data: dict) -> dict:
     text = input_data.get("text" , "")
     decision = input_data.get("decision" , "pending")
     
     return {
            "doc_id" : "human_review",
            "title" : "Human Review Result",
            "text" : text,
            "source" : "human",
            "url" :None,
            "authors" : [],
            "year" : None,
            "status" : decision
     }
if __name__ == "__main__":
     mcp.run(transport = "sse" , host = "0.0.0.0",  port = 8000)
