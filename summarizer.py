from ai.provider import AIProvider
from ai.schema_validator import SchemaValidator
from config.prompts import SUMMARIZE_PROMPT
from core.models import Paper

class Summarizer:
    @staticmethod
    def summarize_paper(paper: Paper, depth: str = "Executive") -> dict:
        if not paper.abstract:
            return {
                "source_basis": "Metadata-only (No abstract available)",
                "executive_summary": f"Title: {paper.title}. No abstract was provided by the source database; full text must be consulted before drawing conclusions.",
                "missing_information": ["Abstract text", "Methodology", "Results", "Limitations"]
            }
        prompt = SUMMARIZE_PROMPT.format(title=paper.title, depth=depth, text=paper.abstract)
        raw = AIProvider.generate(prompt)
        parsed = SchemaValidator.extract_and_parse_json(raw)
        parsed.setdefault("source_basis", "Abstract-only analysis")
        return parsed
