# RIA — Research Intelligence Assistant

**RIA (Research Intelligence Assistant)** is a modular, AI-powered scientific literature intelligence and research productivity platform designed for researchers, undergraduate/graduate students, and academic communities.

## Workflow
**Discover → Retrieve → Understand → Analyse → Compare → Investigate → Organise → Explore**

## Quick Start
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
3. (Optional) Start Ollama locally (`ollama serve` and `ollama pull llama3`) or add your OpenAI API key in `.env` or inside the application Settings tab.
4. Launch RIA:
   ```bash
   streamlit run app.py
   ```
5. Run automated tests:
   ```bash
   pytest tests/
   ```
