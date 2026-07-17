import requests
import xml.etree.ElementTree as ET
def fetch_papers(paper_ids):
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={paper_ids}&retmode=xml"
    fetch_response = requests.get(fetch_url)
    if fetch_response.status_code != 200:
        print("Failed to fetch papers.")
        return None
    root = ET.fromstring(fetch_response.text)
    return root