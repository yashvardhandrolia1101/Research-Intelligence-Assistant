from unittest.mock import patch
from ai.provider import AIProvider
from ai.schema_validator import SchemaValidator
from intelligence.summarizer import Summarizer
from core.models import Paper

def test_schema_validator_handles_fenced_json():
    raw = 'Here is the analysis:\n```json\n{"executive_summary": "Valid summary", "key_findings": ["A"]}\n```'
    parsed = SchemaValidator.extract_and_parse_json(raw)
    assert parsed["executive_summary"] == "Valid summary"
    assert parsed["key_findings"] == ["A"]

def test_summarizer_handles_missing_abstract_without_hallucinating():
    paper = Paper(title="Paper With Missing Abstract", abstract=None)
    res = Summarizer.summarize_paper(paper)
    assert "No abstract" in res["source_basis"]
    assert "Abstract text" in res["missing_information"]

@patch("ai.provider.AIProvider.generate")
def test_summarizer_with_mocked_ai(mock_gen):
    mock_gen.return_value = '{"source_basis": "Abstract-only analysis", "executive_summary": "Demonstrates catalytic efficiency."}'
    paper = Paper(title="Catalysis Study", abstract="Catalyst X improved yield by 40%.")
    res = Summarizer.summarize_paper(paper)
    assert res["executive_summary"] == "Demonstrates catalytic efficiency."
