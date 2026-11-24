from sources.pubmed import PubMedClient

def test_parse_pubmed_xml_complete_and_missing_fields():
    sample_xml = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>39000111</PMID>
                <Article>
                    <Journal><Title>Environmental Science &amp; Policy</Title><JournalIssue><PubDate><Year>2025</Year><Month>Oct</Month></PubDate></JournalIssue></Journal>
                    <ArticleTitle>Co-governance in Urban Lake Restoration.</ArticleTitle>
                    <Abstract>
                        <AbstractText Label="BACKGROUND">Urban lakes face eutrophication.</AbstractText>
                        <AbstractText Label="RESULTS">Co-governed lakes reduced BOD by 75%.</AbstractText>
                    </Abstract>
                    <AuthorList>
                        <Author><LastName>Sharma</LastName><ForeName>A</ForeName></Author>
                    </AuthorList>
                    <PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList>
                </Article>
            </MedlineCitation>
            <PubmedData>
                <ArticleIdList><ArticleId IdType="doi">10.1016/j.envsci.2025.01</ArticleId></ArticleIdList>
            </PubmedData>
        </PubmedArticle>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>39000222</PMID>
                <Article>
                    <ArticleTitle>Paper Without Abstract or Authors</ArticleTitle>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    papers = PubMedClient._parse_pubmed_xml(sample_xml)
    assert len(papers) == 2

    p1 = papers[0]
    assert p1.pmid == "39000111"
    assert p1.title == "Co-governance in Urban Lake Restoration"
    assert p1.authors == ["A Sharma"]
    assert p1.doi == "10.1016/j.envsci.2025.01"
    assert "BACKGROUND: Urban lakes face eutrophication." in p1.abstract

    p2 = papers[1]
    assert p2.pmid == "39000222"
    assert p2.abstract is None
    assert p2.authors == []
