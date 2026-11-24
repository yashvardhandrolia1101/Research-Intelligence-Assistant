from collections import Counter
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.express as px

class ResearchVisualizer:
    @staticmethod
    def publications_by_year(papers: List[Dict[str, Any]]):
        years = [str(p.get("publication_year")) for p in papers if p.get("publication_year")]
        if not years:
            return None
        counts = Counter(years)
        df = pd.DataFrame(sorted(counts.items()), columns=["Year", "Publications"])
        fig = px.bar(
            df, x="Year", y="Publications",
            title="Publications by Year (Retrieved / Saved Corpus)",
            template="plotly_white",
            color_discrete_sequence=["#1E3A8A"]
        )
        fig.update_layout(margin=dict(l=20, r=20, t=45, b=20), height=320)
        return fig

    @staticmethod
    def journal_distribution(papers: List[Dict[str, Any]]):
        journals = [p.get("journal") for p in papers if p.get("journal")]
        if not journals:
            return None
        counts = Counter(journals).most_common(8)
        df = pd.DataFrame(counts, columns=["Journal", "Count"])
        fig = px.bar(
            df, x="Count", y="Journal", orientation="h",
            title="Top Journals in Corpus",
            template="plotly_white",
            color_discrete_sequence=["#0F766E"]
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=20, r=20, t=45, b=20), height=320)
        return fig

    @staticmethod
    def top_authors(papers: List[Dict[str, Any]]):
        authors = []
        for p in papers:
            a_list = p.get("authors", [])
            if isinstance(a_list, list):
                authors.extend(a_list)
        if not authors:
            return None
        counts = Counter(authors).most_common(10)
        df = pd.DataFrame(counts, columns=["Author", "Appearances"])
        fig = px.bar(
            df, x="Appearances", y="Author", orientation="h",
            title="Most Frequent Authors in Corpus",
            template="plotly_white",
            color_discrete_sequence=["#334155"]
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=20, r=20, t=45, b=20), height=320)
        return fig
