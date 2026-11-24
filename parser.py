import re
from typing import Dict

class TextParser:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def parse_structured_abstract(abstract: str) -> Dict[str, str]:
        if not abstract:
            return {}
        sections = {}
        for line in abstract.split("\n\n"):
            if ":" in line:
                prefix, rest = line.split(":", 1)
                if len(prefix) <= 35 and prefix.replace(" ", "").isalpha():
                    sections[prefix.strip().upper()] = rest.strip()
                    continue
            sections.setdefault("GENERAL", "")
            sections["GENERAL"] = (sections["GENERAL"] + " " + line).strip()
        return sections
