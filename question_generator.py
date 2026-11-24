from typing import List
from ai.provider import AIProvider
from ai.schema_validator import SchemaValidator
from config.prompts import QUESTION_GEN_PROMPT
from core.models import Paper

class QuestionGenerator:
    @staticmethod
    def generate_questions(topic: str, papers: List[Paper]) -> dict:
        context = "\n".join([
            f"- {p.title} ({p.publication_year or 'N/A'}): {(p.abstract or '')[:250]}..."
            for p in papers
        ]) or "No specific papers selected; rely on general domain framing while noting unverified novelty."
        prompt = QUESTION_GEN_PROMPT.format(topic=topic, context=context)
        raw = AIProvider.generate(prompt)
        return SchemaValidator.extract_and_parse_json(raw)
