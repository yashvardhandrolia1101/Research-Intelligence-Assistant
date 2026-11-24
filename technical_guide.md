# RIA — Founder's Technical Architecture & Engineering Guide

## 1. Why This Architecture Was Chosen
RIA is engineered around **separation of concerns** and **epistemic accountability**:
- **Deterministic vs. Probabilistic Split:** Search, XML parsing, SQLite storage, TF-IDF chunk retrieval, and file exports are 100% deterministic Python. Large Language Models (LLMs) are isolated inside `ai/` and `intelligence/` behind strict JSON schemas and epistemic guardrails so that an AI failure or offline model never corrupts your research database.
- **Local-First Ownership:** SQLite (`data/ria_library.db`) and Ollama keep all user research libraries, notes, and inference local by default—zero mandatory API bills or cloud vendor lock-in.

## 2. End-to-End Data Flow
1. **Discovery (`discovery/search_engine.py` → `sources/pubmed.py`):**
   - Builds structured PubMed Boolean queries (`[Author]`, `[Journal]`, `[Publication Type]`).
   - Calls NCBI `esearch.fcgi` (throttled to <=3 req/sec) to retrieve PMIDs, then `efetch.fcgi` to stream XML records.
   - `_parse_pubmed_xml()` extracts structured abstract sections, authors, DOIs, and publication dates into validated `Paper` Pydantic models.
2. **Persistence (`database/db.py` & `database/repository.py`):**
   - Stores papers, collections (`collection_papers` many-to-many join table), user notes, and JSON-serialized AI analyses in SQLite with foreign-key integrity.
3. **Single-Paper & Cross-Paper Intelligence (`intelligence/`):**
   - `Extractor`, `Summarizer`, `Simplifier`, `Comparator`, `GapAnalyzer`, and `QuestionGenerator` format domain-specific prompts from `config/prompts.py`, invoke `AIProvider.generate()`, and validate JSON responses via `SchemaValidator`.
4. **RAG-Grounded Research Chat (`processing/chunker.py` → `rag/vector_store.py` → `rag/retriever.py`):**
   - Splits abstracts into sentence-aligned ~450-character chunks.
   - `LocalTFIDFVectorStore` computes term frequency–inverse document frequency (TF-IDF) cosine similarity against the user's question to retrieve top-k passages with source citations before calling the LLM.
5. **User Interface (`ui/` & `app.py`):**
   - `app.py` manages multipage state and routes cleanly to modular views in `ui/`.

## 3. What You Built vs. External Dependencies
- **Your Software Engineering:** The entire multi-stage research workflow, PubMed E-utilities ingestion pipeline, query scope diagnostics, relational SQLite schema, TF-IDF passage retriever, prompt schemas, JSON fallback parser, and multi-format export suite.
- **External Services / Models:** PubMed/NCBI E-utilities provides the bibliographic metadata; local Ollama models (e.g., Llama 3, Mistral) or OpenAI models provide natural language synthesis when invoked by your orchestration layer.
