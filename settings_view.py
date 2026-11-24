import streamlit as st
from ai.provider import AIProvider
from config.settings import DB_PATH
from ui.components import render_header

def render_settings():
    render_header(
        "Settings & AI Provider Configuration",
        "Configure local inference (Ollama) or optional cloud API providers, generation parameters, and local storage."
    )

    cfg = AIProvider._runtime_config

    with st.form("ai_settings_form"):
        provider = st.selectbox("Active AI Provider", ["ollama", "openai"], index=0 if cfg["provider"] == "ollama" else 1)

        st.markdown("#### Local AI Configuration (Ollama — Recommended Default)")
        ollama_url = st.text_input("Ollama Base URL", value=cfg["ollama_url"])
        ollama_model = st.text_input("Local Model Name", value=cfg["ollama_model"], help="Examples: llama3, mistral, qwen2.5:7b, gemma2")

        st.markdown("#### Optional Cloud Provider (OpenAI)")
        openai_key = st.text_input("OpenAI API Key (stored in session memory only)", value=cfg["openai_key"], type="password")
        openai_model = st.text_input("OpenAI Model Name", value=cfg["openai_model"])

        temperature = st.slider("Sampling Temperature (Lower = More Deterministic)", 0.0, 1.0, float(cfg["temperature"]), 0.05)

        if st.form_submit_button("Save & Test AI Configuration", type="primary"):
            AIProvider.configure(
                provider=provider,
                ollama_url=ollama_url,
                ollama_model=ollama_model,
                openai_key=openai_key,
                openai_model=openai_model,
                temperature=temperature
            )
            ok, msg = AIProvider.get_status()
            if ok:
                st.success(f"Configuration saved! Status: {msg}")
            else:
                st.warning(f"Configuration saved, but provider check reported: {msg}")

    st.markdown("---")
    st.subheader("Database & Backup")
    st.caption(f"Local SQLite Database Path: `{DB_PATH}`")
    if DB_PATH.exists():
        st.download_button(
            "Download SQLite Database Backup (.db)",
            data=DB_PATH.read_bytes(),
            file_name="ria_library_backup.db",
            mime="application/octet-stream"
        )
