import pandas as pd
from typing import List, Dict, Any

class CSVExporter:
    @staticmethod
    def generate_csv(papers: List[Dict[str, Any]]) -> str:
        if not papers:
            return ""
        export_rows = []
        for p in papers:
            authors = p.get("authors", [])
            if isinstance(authors, list):
                authors = "; ".join(authors)
            export_rows.append({
                "PMID": p.get("pmid", ""),
                "DOI": p.get("doi", ""),
                "Title": p.get("title", ""),
                "Authors": authors,
                "Journal": p.get("journal", ""),
                "Year": p.get("publication_year", ""),
                "Publication_Date": p.get("publication_date", ""),
                "Type": p.get("publication_type", ""),
                "URL": p.get("url", ""),
                "Abstract": p.get("abstract", "")
            })
        return pd.DataFrame(export_rows).to_csv(index=False)
