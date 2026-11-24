# RIA — Research Intelligence Assistant

**RIA (Research Intelligence Assistant)** is a modular, AI-powered scientific literature intelligence and research productivity platform built with Python and Streamlit. Designed for researchers, undergraduate/graduate students, and academic communities, RIA bridges the gap between searching raw academic databases and deeply understanding scientific literature.

---

## Overview

Reading and synthesizing academic papers is slow, fragmented, and repetitive—requiring researchers to switch between search engines, dense PDFs, note-taking apps, and generic AI chat tools. RIA unifies this entire process into a single interactive workspace powered by the **PubMed E-utilities API** and configurable **Large Language Model (LLM)** backends.

### Core Research Workflow
**Discover → Retrieve → Understand → Analyse → Compare → Investigate → Organise → Explore**

---

## Key Features

- **PubMed Literature Search & Retrieval:** Query scientific papers directly from PubMed and retrieve clean metadata including titles, authors, journals, publication years, and abstracts.
- **AI-Assisted Paper Comprehension:** Generate structured summaries, plain-English explanations, and concise study notes from complex scientific text.
- **Critical Analysis & Gap Identification:** Highlight methodological limitations, unanswered questions, and promising directions for future research.
- **Multi-Paper Synthesis & Organization:** Keep retrieved papers, insights, and research notes organized in one continuous workflow.
- **Provider-Agnostic AI Architecture:** Seamlessly switch between OpenAI-compatible cloud inference endpoints (such as Groq) and local models (such as Ollama) via environment variables or the in-app **Settings** tab without modifying application code.

---

## Architecture & Tech Stack

- **User Interface:** Streamlit (`app.py`) — interactive browser-based research workspace and session state management.
- **AI Provider Layer:** Modular Python API client (`ai/provider.py`) supporting OpenAI-compatible REST endpoints and local inference servers.
- **Literature Data Pipeline:** PubMed E-utilities API (`requests`, `xml.etree.ElementTree`, `json`) for automated search and metadata parsing.
- **Testing:** `pytest` suite for core component verification.

---

## Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
Configure environment variables: 
  cp .env.example .env
(Add your OPENAI_API_KEY and optional OPENAI_BASE_URL in .env, in your terminal environment, or directly inside the app's Settings tab.)
Run the application:
 streamlit run app.py
