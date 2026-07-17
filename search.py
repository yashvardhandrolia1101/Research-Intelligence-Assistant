import requests

def search_papers(topic):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={topic}&retmode=json"
    response = requests.get(url)
    if response.status_code != 200:
        print("Search failed.")
        return None
    data = response.json()
    return data["esearchresult"]["idlist"]