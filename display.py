def display_titles(articles):
    print("\n" + "=" * 60)
    print("Top Research Papers")
    print("=" * 60)
    for i, article in enumerate(articles, start=1):
        title = article.find(".//ArticleTitle")
        if title is not None:
            print(f"{i}. {title.text}")
        else:
            print(f"{i}. Title not available")
    print("=" * 60)
def display_details(article):
    print("\n" + "=" * 60)
    print("Research Paper Details")
    print("=" * 60)
    title = article.find(".//ArticleTitle")
    print("\nTitle:")
    if title is not None:
        print(title.text)
    else:
        print("Title not available.")
    authors = article.findall(".//Author")
    print("\nAuthors:")
    for author in authors:
        first_name = author.find("ForeName")
        last_name = author.find("LastName")
        if first_name is not None and last_name is not None:
            print(first_name.text, last_name.text)
    journal = article.find(".//Title")
    print("\nJournal:")
    if journal is not None:
        print(journal.text)
    else:
        print("Journal not available.")
    year = article.find(".//PubDate/Year")
    print("\nPublication Year:")
    if year is not None:
        print(year.text)
    else:
        print("Publication year not available.")
    abstract = article.find(".//AbstractText")
    print("\nAbstract:")
    if abstract is not None:
        print(abstract.text)
    else:
        print("No abstract available.")