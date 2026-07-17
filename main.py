import xml.etree.ElementTree as ET
from search import search_papers
from fetch import fetch_papers
from display import display_titles, display_details
print("=" * 50)
print("        Research Intelligence Assistant")
print("=" * 50)
topic = input("Enter a research topic: ")
id_list = search_papers(topic)
if id_list is None:
    exit()
print("\nPaper IDs:")
print(id_list)
top_papers = id_list[:10]
paper_ids = ",".join(top_papers)
print("\nTop 10 PMIDs:")
print(top_papers)
root = fetch_papers(paper_ids)
if root is None:
    exit()
print("\nRoot Tag:")
print(root.tag)
articles = root.findall(".//PubmedArticle")
display_titles(articles)
choice = int(input("\nChoose a paper (1-10): "))
if choice < 1 or choice > len(articles):
    print("Invalid choice.")
    exit()
selected_article = articles[choice - 1]
display_details(selected_article)