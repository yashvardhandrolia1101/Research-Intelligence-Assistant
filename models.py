from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Paper(BaseModel):
    id: Optional[int] = None
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors: List[str] = Field(default_factory=list)
    journal: Optional[str] = None
    publication_year: Optional[str] = None
    publication_date: Optional[str] = None
    abstract: Optional[str] = None
    publication_type: Optional[str] = "Journal Article"
    source: str = "PubMed"
    url: Optional[str] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class StructuredAnalysis(BaseModel):
    analysis_scope: str = "Abstract-based"
    research_problem: str = "Not stated in provided text"
    research_question: str = "Not stated in provided text"
    research_objectives: List[str] = Field(default_factory=list)
    background_context: str = "Not stated in provided text"
    hypothesis: str = "Not stated in provided text"
    methodology: str = "Not stated in provided text"
    experimental_design: str = "Not stated in provided text"
    dataset_or_sample: str = "Not stated in provided text"
    variables_and_measurements: List[str] = Field(default_factory=list)
    principal_findings: List[str] = Field(default_factory=list)
    statistical_results: str = "Not stated in provided text"
    conclusions: str = "Not stated in provided text"
    limitations: List[str] = Field(default_factory=list)
    future_research_directions: List[str] = Field(default_factory=list)
    explicit_vs_inferred_notes: str = ""

class ChatMessage(BaseModel):
    role: str
    content: str
    citations: List[str] = Field(default_factory=list)
