from typing import List
from provider import AIProvider
from schema_validator import SchemaValidator
from prompts import GAP_ANALYZER_PROMPT
from models import Paper

class GapAnalyzer:
    @staticmethod
    def analyze_gaps(papers: List[Paper]) -> dict:
        summaries = []
        for p in papers:
            summaries.append(
                f"- Title: {p.title} (PMID: {p.pmid or 'N/A'}, Year: {p.publication_year or 'N/A'})\n"
                f"  Abstract: {p.abstract or 'No abstract available.'}"
            )
        prompt = GAP_ANALYZER_PROMPT.format(papers_summary="\n\n".join(summaries))
        raw = AIProvider.generate(prompt)
        parsed = SchemaValidator.extract_and_parse_json(raw)
        parsed.setdefault(
            "collection_caveat",
            "Note: Identified gaps reflect only the retrieved collection and require broader literature verification."
        )
        return parsed
