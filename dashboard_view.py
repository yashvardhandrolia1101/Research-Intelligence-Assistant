import streamlit as st
from database.repository import Repository
from recommendations.engine import RecommendationEngine
from analytics.visualizer import ResearchVisualizer
from ui.components import render_header

def render_dashboard(navigate_callback):
    render_header(
        "RIA — Research Intelligence Dashboard",
        "Discover → Retrieve → Understand → Analyse → Compare → Investigate → Organise → Explore"
    )

    papers = Repository.get_all_papers()
    collections = Repository.get_collections()
    notes = Repository.get_notes()
    analyses = Repository.get_saved_analyses()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saved Papers", len(papers))
    c2.metric("Collections", len(collections))
    c3.metric("Research Notes", len(notes))
    c4.metric("Saved AI Analyses", len(analyses))

    st.markdown("---")
    q_col1, q_col2 = st.columns([0.75, 0.25])
    with q_col1:
        quick_q = st.text_input("Quick Literature Search (PubMed)", placeholder="e.g., urban wetland bioremediation, CRISPR base editing...")
    with q_col2:
        st.write("")
        st.write("")
        if st.button("Search Literature", type="primary", use_container_width=True) and quick_q.strip():
            st.session_state.pending_search = quick_q.strip()
            navigate_callback("Discover")

    left, right = st.columns([0.58, 0.42])

    with left:
        st.subheader("Recently Saved Publications")
        if not papers:
            st.info("Your library is currently empty. Use Discover to query PubMed and save papers.")
        else:
            for p in papers[:5]:
                with st.container(border=True):
                    st.markdown(f"**{p['title']}**")
                    st.caption(f"{p.get('journal', 'Unknown Journal')} • {p.get('publication_date', 'N/A')} • PMID: {p.get('pmid') or 'N/A'}")
                    if st.button("Open in Workspace", key=f"dash_open_{p['id']}"):
                        st.session_state.selected_paper = p
                        navigate_callback("Research Workspace")

    with right:
        st.subheader("Suggested Next Steps & Themes")
        recs = RecommendationEngine.generate_recommendations(papers)
        for step in recs["suggested_next_steps"]:
            st.markdown(f"- {step}")
        if recs["dominant_themes"]:
            st.markdown("**Dominant Corpus Keywords:** " + ", ".join([f"`{t}`" for t in recs["dominant_themes"]]))

    if papers:
        st.markdown("---")
        st.subheader("Corpus Analytics")
        ch1, ch2 = st.columns(2)
        with ch1:
            fig_y = ResearchVisualizer.publications_by_year(papers)
            if fig_y:
                st.plotly_chart(fig_y, use_container_width=True)
        with ch2:
            fig_j = ResearchVisualizer.journal_distribution(papers)
            if fig_j:
                st.plotly_chart(fig_j, use_container_width=True)
