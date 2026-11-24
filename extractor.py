from ai.provider import AIProvider
from ai.schema_validator import SchemaValidator
from config.prompts import EXTRACT_STRUCTURED_PROMPT
from core.models import Paper, StructuredAnalysis

class Extractor:
    @staticmethod
    def extract_structured(paper: Paper) -> StructuredAnalysis:
        if not paper.abstract:
            return StructuredAnalysis(
                analysis_scope="Metadata-only (Abstract unavailable)",
                explicit_vs_inferred_notes="No abstract or full text was available from PubMed; methodological extraction could not be performed."
            )
        prompt = EXTRACT_STRUCTURED_PROMPT.format(title=paper.title, text=paper.abstract)
        raw = AIProvider.generate(prompt)
        data = SchemaValidator.extract_and_parse_json(raw)
        if "raw_response" in data:
            return StructuredAnalysis(
                analysis_scope="Abstract-based (Unstructured fallback)",
                research_problem=data["raw_response"],
                explicit_vs_inferred_notes="Model returned unstructured text."
            )
        return StructuredAnalysis(**{
            k: v for k, v in data.items() if k in StructuredAnalysis.model_fields
        })
