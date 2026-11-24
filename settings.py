import os
from pathlib import Path
from dotenv import load_dotenv

try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()


def _get_config(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    if st is not None:
        try:
            if key in st.secrets and st.secrets[key]:
                return str(st.secrets[key])
        except Exception:
            pass
    return default


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "ria_library.db"

DEFAULT_AI_PROVIDER = _get_config("RIA_AI_PROVIDER", "openai")
OLLAMA_BASE_URL = _get_config("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = _get_config("OLLAMA_MODEL", "llama3")
OPENAI_API_KEY = _get_config("OPENAI_API_KEY", "")
OPENAI_BASE_URL = _get_config("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
OPENAI_MODEL = _get_config("OPENAI_MODEL", "llama-3.3-70b-versatile")

PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
PUBMED_TOOL = "RIA_ResearchIntelligenceAssistant"
PUBMED_EMAIL = _get_config("PUBMED_EMAIL", "researcher@ria.local")
