import streamlit as st
from database.db import init_db
from ui.components import inject_custom_css, render_sidebar_status
from ui.dashboard_view import render_dashboard
from ui.discover_view import render_discover
from ui.workspace_view import render_workspace
from ui.compare_view import render_compare
from ui.intelligence_view import render_intelligence
from ui.chat_view import render_chat
from ui.library_view import render_library
from ui.settings_view import render_settings

st.set_page_config(
    page_title="RIA — Research Intelligence Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
inject_custom_css()

PAGES = [
    "Home / Dashboard",
    "Discover",
    "Research Workspace",
    "Compare",
    "Research Intelligence",
    "AI Research Assistant",
    "My Library",
    "Settings"
]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Home / Dashboard"

def navigate_to(page_name: str):
    if page_name in PAGES:
        st.session_state.nav_page = page_name
        st.rerun()

st.sidebar.markdown("## RIA")
st.sidebar.caption("Research Intelligence Assistant")

selected_page = st.sidebar.radio(
    "Workflow Navigation",
    PAGES,
    index=PAGES.index(st.session_state.nav_page)
)

if selected_page != st.session_state.nav_page:
    st.session_state.nav_page = selected_page
    st.rerun()

st.sidebar.markdown("---")
render_sidebar_status()

page = st.session_state.nav_page

if page == "Home / Dashboard":
    render_dashboard(navigate_to)
elif page == "Discover":
    render_discover(navigate_to)
elif page == "Research Workspace":
    render_workspace()
elif page == "Compare":
    render_compare()
elif page == "Research Intelligence":
    render_intelligence()
elif page == "AI Research Assistant":
    render_chat()
elif page == "My Library":
    render_library(navigate_to)
elif page == "Settings":
    render_settings()
