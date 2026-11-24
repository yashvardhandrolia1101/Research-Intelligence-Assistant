import re
from collections import Counter
from typing import List, Dict, Any

STOPWORDS = {
    "the", "and", "of", "to", "in", "a", "for", "with", "on", "as", "are", "is",
    "by", "that", "from", "this", "an", "be", "or", "at", "were", "was", "which",
    "study", "results", "using", "based", "analysis", "between", "effects", "effect"
}

class RecommendationEngine:
    @staticmethod
    def generate_recommendations(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not papers:
            return {
                "recommended_queries": [
                    {"query": "systematic review AND methodology", "reason": "Starter query to explore structured evidence syntheses."}
                ],
                "dominant_themes": [],
                "suggested_next_steps": [
                    "Search PubMed in the Discover tab to build an initial working corpus of 5-10 papers.",
                    "Save key papers to your Library to unlock cross-paper comparison and gap detection."
                ]
            }

        word_counts = Counter()
        for p in papers:
            text = f"{p.get('title', '')} {p.get('abstract', '')}".lower()
            tokens = [w for w in re.findall(r'[a-z]{4,}', text) if w not in STOPWORDS]
            word_counts.update(tokens)

        top_terms = [term for term, _ in word_counts.most_common(6)]
        queries = []
        if len(top_terms) >= 2:
            queries.append({
                "query": f"{top_terms[0]} AND {top_terms[1]} AND (review[pt] OR meta-analysis[pt])",
                "reason": f"Synthesizes high-level evidence connecting your top corpus keywords ('{top_terms[0]}' and '{top_terms[1]}')."
            })
        if len(top_terms) >= 3:
            queries.append({
                "query": f"{top_terms[0]} AND ({top_terms[2]} OR limitations)",
                "reason": f"Explores secondary mechanisms and constraints around '{top_terms[2]}'."
            })

        return {
            "recommended_queries": queries,
            "dominant_themes": top_terms,
            "suggested_next_steps": [
                f"Compare methodological designs across your {len(papers)} saved papers in the Compare tab.",
                "Run the Research Gap Intelligence engine to extract underexplored variables.",
                "Export an annotated Markdown or CSV synthesis report for your research notes."
            ]
        }
