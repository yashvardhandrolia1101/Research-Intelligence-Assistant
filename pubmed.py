import time
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple
from core.models import Paper
from core.exceptions import SourceError
from config.settings import PUBMED_BASE_URL, PUBMED_TOOL, PUBMED_EMAIL

class PubMedClient:
    _last_request_time = 0.0
    _min_interval = 0.35  # Respect NCBI 3 requests/sec unauthenticated rate limit

    @classmethod
    def _throttle(cls):
        elapsed = time.time() - cls._last_request_time
        if elapsed < cls._min_interval:
            time.sleep(cls._min_interval - elapsed)
        cls._last_request_time = time.time()

    @classmethod
    def _request_with_retry(cls, url: str, params: dict, timeout: int = 12, retries: int = 2) -> requests.Response:
        last_err = None
        for attempt in range(retries + 1):
            try:
                cls._throttle()
                resp = requests.get(url, params=params, timeout=timeout)
                if resp.status_code == 429:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                last_err = e
                if attempt < retries:
                    time.sleep(0.8 * (attempt + 1))
        raise SourceError(f"PubMed network/API error after {retries + 1} attempts: {str(last_err)}")

    @classmethod
    def search(
        cls,
        query: str,
        max_results: int = 10,
        offset: int = 0,
        sort: str = "relevance",
        min_date: Optional[str] = None,
        max_date: Optional[str] = None
    ) -> Tuple[List[str], int]:
        if not query or not query.strip():
            return [], 0

        search_url = f"{PUBMED_BASE_URL}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query.strip(),
            "retmax": max(1, min(max_results, 100)),
            "retstart": max(0, offset),
            "retmode": "json",
            "sort": "pub_date" if sort == "date" else "relevance",
            "tool": PUBMED_TOOL,
            "email": PUBMED_EMAIL,
        }
        if min_date and max_date:
            params["datetype"] = "pdat"
            params["mindate"] = min_date
            params["maxdate"] = max_date

        response = cls._request_with_retry(search_url, params)
        try:
            data = response.json()
            esearch = data.get("esearchresult", {})
            id_list = esearch.get("idlist", [])
            total_count = int(esearch.get("count", len(id_list)))
            return id_list, total_count
        except Exception as e:
            raise SourceError(f"Malformed JSON response from PubMed ESearch: {str(e)}")

    @classmethod
    def fetch_details(cls, pmids: List[str]) -> List[Paper]:
        if not pmids:
            return []

        unique_pmids = list(dict.fromkeys([str(p).strip() for p in pmids if str(p).strip()]))
        fetch_url = f"{PUBMED_BASE_URL}efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(unique_pmids),
            "retmode": "xml",
            "tool": PUBMED_TOOL,
            "email": PUBMED_EMAIL,
        }
        response = cls._request_with_retry(fetch_url, params, timeout=18)
        return cls._parse_pubmed_xml(response.text)

    @staticmethod
    def _extract_text(element: Optional[ET.Element]) -> str:
        if element is None:
            return ""
        return "".join(element.itertext()).strip()

    @classmethod
    def _parse_pubmed_xml(cls, xml_content: str) -> List[Paper]:
        if not xml_content or not xml_content.strip():
            return []
        papers: List[Paper] = []
        seen_pmids = set()

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise SourceError(f"Malformed XML returned by PubMed EFetch: {str(e)}")

        for article in root.findall(".//PubmedArticle"):
            pmid = cls._extract_text(article.find(".//MedlineCitation/PMID"))
            if pmid and pmid in seen_pmids:
                continue
            if pmid:
                seen_pmids.add(pmid)

            title = cls._extract_text(article.find(".//Article/ArticleTitle")) or "Untitled Publication"
            if title.endswith("."):
                title = title[:-1].strip()

            authors = []
            for author in article.findall(".//Article/AuthorList/Author"):
                fore = cls._extract_text(author.find("ForeName"))
                last = cls._extract_text(author.find("LastName"))
                collective = cls._extract_text(author.find("CollectiveName"))
                if fore and last:
                    authors.append(f"{fore} {last}")
                elif last:
                    authors.append(last)
                elif collective:
                    authors.append(collective)

            journal = (
                cls._extract_text(article.find(".//Article/Journal/Title"))
                or cls._extract_text(article.find(".//MedlineJournalInfo/MedlineTA"))
                or "Unknown Journal"
            )

            pub_date_elem = article.find(".//Article/Journal/JournalIssue/PubDate")
            year = cls._extract_text(pub_date_elem.find("Year")) if pub_date_elem is not None else ""
            month = cls._extract_text(pub_date_elem.find("Month")) if pub_date_elem is not None else ""
            medline_date = cls._extract_text(pub_date_elem.find("MedlineDate")) if pub_date_elem is not None else ""

            if not year and medline_date:
                year = medline_date[:4]
            pub_date = f"{month} {year}".strip() if (month or year) else (medline_date or "Unknown")

            # Concatenate structured abstract sections accurately
            abstract_parts = []
            for abs_elem in article.findall(".//Article/Abstract/AbstractText"):
                label = abs_elem.attrib.get("Label")
                section_text = cls._extract_text(abs_elem)
                if section_text:
                    if label:
                        abstract_parts.append(f"{label}: {section_text}")
                    else:
                        abstract_parts.append(section_text)
            abstract = "".join(abstract_parts) if abstract_parts else None

            doi = None
            for id_elem in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
                if id_elem.attrib.get("IdType") == "doi":
                    doi = cls._extract_text(id_elem)
                    break

            pub_types = [
                cls._extract_text(pt)
                for pt in article.findall(".//Article/PublicationTypeList/PublicationType")
                if cls._extract_text(pt)
            ]
            pub_type_str = ", ".join(pub_types[:2]) if pub_types else "Journal Article"

            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else (f"https://doi.org/{doi}" if doi else None)

            papers.append(Paper(
                pmid=pmid or None,
                doi=doi or None,
                title=title,
                authors=authors,
                journal=journal,
                publication_year=year or None,
                publication_date=pub_date,
                abstract=abstract,
                publication_type=pub_type_str,
                source="PubMed",
                url=url,
                raw_metadata={"publication_types": pub_types}
            ))

        return papers
