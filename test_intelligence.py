from unittest.mock import patch
from core.models import Paper
from rag.retriever import RAGRetriever
from intelligence.comparator import Comparator
from intelligence.gap_analyzer import GapAnalyzer
from exports.pdf_exporter import PDFExporter
from exports.csv_exporter import CSVExporter

def test_rag_passage_retrieval():
    p1 = Paper(pmid="1", title="Jakkur Lake Study", abstract="Wetland bioremediation reduced biological oxygen demand by 90 percent.")
    p2 = Paper(pmid="2", title="Quantum Dots Study", abstract="Cadmium selenide nanocrystals exhibit tunable photoluminescence.")
    passages = RAGRetriever.retrieve_relevant_passages("oxygen demand wetland", [p1, p2], top_k=1)
    assert len(passages) == 1
    assert passages[0]["pmid"] == "1"

@patch("ai.provider.AIProvider.generate")
def test_comparator_and_gap_analyzer(mock_gen):
    mock_gen.return_value = '{"convergence": ["Both examine urban lakes"], "gaps": [{"title": "Longitudinal water sampling"}]}'
    papers = [
        Paper(pmid="1", title="Lake A", abstract="Study A abstract"),
        Paper(pmid="2", title="Lake B", abstract="Study B abstract")
    ]
    comp = Comparator.compare_papers(papers)
    assert "convergence" in comp
    gaps = GapAnalyzer.analyze_gaps(papers)
    assert "collection_caveat" in gaps

def test_exports():
    pdf_bytes = PDFExporter.generate_report_pdf("Test Report", {"Summary": "Sample content"})
    assert pdf_bytes.startswith(b"%PDF")
    csv_text = CSVExporter.generate_csv([{"pmid": "1", "title": "Test", "authors": ["A", "B"]}])
    assert "PMID,DOI,Title" in csv_text
