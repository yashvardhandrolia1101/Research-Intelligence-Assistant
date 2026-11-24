from typing import List, Optional, Dict, Any
from sources.pubmed import PubMedClient
from core.models import Paper

class SearchEngine:
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def build_pubmed_query(
        cls,
        keyword_query: str,
        author: Optional[str] = None,
        journal: Optional[str] = None,
        pub_type: Optional[str] = None,
        exact_phrase: bool = False
    ) -> str:
        parts = []
        q = keyword_query.strip()
        if q:
            if exact_phrase and not (q.startswith('"') and q.endswith('"')):
                parts.append(f'"{q}"')
            else:
                parts.append(q)
        if author and author.strip():
            parts.append(f"{author.strip()}[Author]")
        if journal and journal.strip():
            parts.append(f'"{journal.strip()}"[Journal]')
        if pub_type and pub_type != "All":
            parts.append(f'"{pub_type}"[Publication Type]')
        return " AND ".join(parts)

    @classmethod
    def search_literature(
        cls,
        query: str,
        max_results: int = 10,
        offset: int = 0,
        sort: str = "relevance",
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        author: Optional[str] = None,
        journal: Optional[str] = None,
        pub_type: Optional[str] = None,
        exact_phrase: bool = False
    ) -> Dict[str, Any]:
        built_query = cls.build_pubmed_query(query, author, journal, pub_type, exact_phrase)
        if not built_query:
            return {"papers": [], "total_count": 0, "effective_query": "", "diagnostics": {}}

        min_date = f"{min_year}/01/01" if min_year else None
        max_date = f"{max_year}/12/31" if max_year else None

        cache_key = f"{built_query}|{max_results}|{offset}|{sort}|{min_date}|{max_date}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        pmids, total_count = PubMedClient.search(
            built_query,
            max_results=max_results,
            offset=offset,
            sort=sort,
            min_date=min_date,
            max_date=max_date
        )
        papers: List[Paper] = PubMedClient.fetch_details(pmids)

        diagnostics = cls.analyze_query_scope(query, total_count)
        result = {
            "papers": papers,
            "total_count": total_count,
            "effective_query": built_query,
            "diagnostics": diagnostics
        }
        cls._cache[cache_key] = result
        return result

    @staticmethod
    def analyze_query_scope(raw_query: str, total_count: int) -> Dict[str, Any]:
        suggestions = []
        scope_status = "Balanced"
        explanation = "The query returned a focused set of literature suitable for synthesis."

        if total_count > 5000:
            scope_status = "Overly Broad"
            explanation = f"Found {total_count:,} records. Adding methodology or outcome constraints will improve signal-to-noise ratio."
            suggestions = [
                {"query": f"({raw_query}) AND (systematic review[pt] OR meta-analysis[pt])", "reason": "Filters to high-level evidence syntheses."},
                {"query": f"({raw_query}) AND (randomized controlled trial[pt])", "reason": "Isolates causal experimental trials."},
                {"query": f"({raw_query}) AND (mechanism OR pathway)", "reason": "Focuses on mechanistic explanations."}
            ]
        elif total_count == 0:
            scope_status = "Overly Narrow / Zero Hits"
            explanation = "No matching records were found in PubMed. Broadening terms or removing strict boolean constraints is recommended."
            tokens = [t for t in raw_query.replace('"', '').split() if t.upper() not in {"AND", "OR", "NOT"} and len(t) > 3]
            if len(tokens) >= 2:
                suggestions.append({
                    "query": " OR ".join(tokens[:3]),
                    "reason": "Replaces strict intersection with broader union across core terms."
                })
        else:
            suggestions = [
                {"query": f"({raw_query}) AND review[pt]", "reason": "Surfaces comprehensive domain overviews."},
                {"query": f"({raw_query}) AND limitations", "reason": "Targets papers explicitly discussing methodological constraints."}
            ]

        return {
            "scope_status": scope_status,
            "explanation": explanation,
            "suggestions": suggestions
        }
