import os
import requests
import xml.etree.ElementTree as ET

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ncbi_key = os.getenv("NCBI_API_KEY")

def search_pubmed(query, max_results=10):
    url = BASE + "esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    }
    if ncbi_key:
        params["api_key"] = ncbi_key

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("esearchresult", {}).get("idlist", [])

def fetch_pubmed(pmids):
    url = BASE + "efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }
    if ncbi_key:
        params["api_key"] = ncbi_key

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text

def parse_pubmed(xml_data):
    root = ET.fromstring(xml_data)
    articles = []   
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        abstract_parts = article.findall(".//AbstractText")
        abstract = ' '.json([a.text for a in abstract_parts if a.text]) if abstract_parts else None
        pmid = article.findtext(".//PMID")

        authors = []
        for author in article.findall(".//Author"):
            last = author.findtext("LastName")
            fore = author.findtext("ForeName")
            if last and fore: 
                authors.append(f"{fore} {last}")

        year = article.findtext(".//PubDate/Year")
        if not year:
            year = article.findtext (".//PubDate/MedlineDate")

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "year": year
        })

    return articles

