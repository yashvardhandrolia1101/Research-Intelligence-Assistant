from provider import AIProvider
from prompts import SIMPLIFY_PROMPT

class Simplifier:
    @staticmethod
    def simplify_passage(text: str, level: str = "Undergraduate") -> str:
        if not text or not text.strip():
            return "Please provide a passage, abstract, or scientific concept to explain."
        prompt = SIMPLIFY_PROMPT.format(level=level, text=text.strip())
        return AIProvider.generate(prompt)
