import streamlit as st
from provider import AIProvider

def inject_custom_css():
    st.markdown("""
        <style>
        .ria-banner {
            border-bottom: 1px solid #E2E8F0;
            padding-bottom: 0.75rem;
            margin-bottom: 1.25rem;
        }
        .ria-title {
            font-size: 1.65rem;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.02em;
            margin: 0;
        }
        .ria-subtitle {
            font-size: 0.9rem;
            color: #475569;
            margin-top: 0.2rem;
        }
        .ria-disclaimer {
            background-color: #F8FAFC;
            border-left: 3px solid #1E3A8A;
            padding: 0.6rem 0.9rem;
            font-size: 0.82rem;
            color: #334155;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header(section_title: str, description: str):
    st.markdown(f"""
        <div class="ria-banner">
            <div class="ria-title">{section_title}</div>
            <div class="ria-subtitle">{description}</div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar_status():
    ok, msg = AIProvider.get_status()
    if ok:
        st.sidebar.success(f"AI Engine: {msg}")
    else:
        st.sidebar.warning(f"AI Engine: {msg}")
    st.sidebar.caption("Scientific Literature Tool — Not for medical diagnosis.")
