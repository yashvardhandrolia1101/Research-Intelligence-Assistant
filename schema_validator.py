import json
import re
from typing import Dict, Any

class SchemaValidator:
    @staticmethod
    def extract_and_parse_json(ai_response: str) -> Dict[str, Any]:
        if not ai_response or not ai_response.strip():
            return {"error": "Empty response from AI provider."}

        cleaned = ai_response.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        brace_start = cleaned.find("{")
        brace_end = cleaned.rfind("}")
        if brace_start != -1 and brace_end > brace_start:
            try:
                return json.loads(cleaned[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass

        return {"raw_response": cleaned, "parse_warning": "Model output was not strict JSON; displaying raw response."}
