# Troubleshooting & Known Limitations

## Common Issues
- **Ollama Offline Warning:** If the sidebar says `AI Engine: Ollama offline`, run `ollama serve` in a separate terminal or switch to `openai` in the **Settings** page with your API key. Deterministic features (PubMed Search, Library, Notes, Analytics, CSV/PDF Exports) work even without an AI model connected.
- **Abstract-Only Scope:** PubMed E-utilities provides full metadata and abstracts for millions of biomedical and interdisciplinary papers, but full-text PDFs behind publisher paywalls are never bypassed. RIA explicitly labels analyses as abstract-based when full text is absent.
