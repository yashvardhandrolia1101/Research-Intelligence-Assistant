from typing import List
from ai.provider import AIProvider
from ai.schema_validator import SchemaValidator
from config.prompts import COMPARE_PAPERS_PROMPT
from core.models import Paper

class Comparator:
    @staticmethod
    def compare_papers(papers: List[Paper]) -> dict:
        blocks = []
        for idx, p in enumerate(papers, 1):
            blocks.append(
                f"[Paper {idx}] Title: {p.title} | PMID: {p.pmid or 'N/A'} | Year: {p.publication_year or 'N/A'}\n"
                f"Abstract: {p.abstract or 'No abstract available.'}"
            )
        prompt = COMPARE_PAPERS_PROMPT.format(papers_data="\n\n---\n\n".join(blocks))
        raw = AIProvider.generate(prompt)
        return SchemaValidator.extract_and_parse_json(raw)
