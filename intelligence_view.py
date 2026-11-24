import streamlit as st
from core.models import Paper
from database.repository import Repository
from intelligence.gap_analyzer import GapAnalyzer
from intelligence.question_generator import QuestionGenerator
from exports.markdown_exporter import MarkdownExporter
from ui.components import render_header

def render_intelligence():
    render_header(
        "Research Gap Intelligence & Question Formulation",
        "Identify underexplored variables, methodological limitations, and verifiable next-step research questions."
    )

    papers = Repository.get_all_papers()
    collections = Repository.get_collections()

    scope_options = ["All Saved Library Papers"] + [f"Collection: {c['name']}" for c in collections]
    scope = st.selectbox("Target Literature Corpus", scope_options)

    if scope == "All Saved Library Papers":
        target_papers = papers
    else:
        col_name = scope.replace("Collection: ", "", 1)
        col_id = next((c["id"] for c in collections if c["name"] == col_name), None)
        target_papers = Repository.get_papers_in_collection(col_id) if col_id else []

    st.caption(f"Selected corpus size: **{len(target_papers)}** papers.")

    tab_gaps, tab_qgen = st.tabs(["Research Gap Intelligence Engine", "Research Question Generator"])

    with tab_gaps:
        st.markdown('<div class="ria-disclaimer">Scientific Integrity Standard: Gaps identified below represent underexplored directions within your retrieved corpus, not absolute claims of global novelty.</div>', unsafe_allow_html=True)
        if not target_papers:
            st.info("Add papers to this corpus first.")
        elif st.button("Detect Potential Research Gaps", type="primary"):
            with st.spinner("Analyzing limitations, conflicting results, and underexplored variables..."):
                try:
                    p_objs = [Paper(**p) for p in target_papers[:15]]
                    gaps = GapAnalyzer.analyze_gaps(p_objs)
                    st.session_state.last_gaps = gaps
                    Repository.save_analysis("gap_analysis", f"Gap Analysis ({scope})", gaps)
                except Exception as e:
                    st.error(str(e))

        gaps_data = st.session_state.get("last_gaps")
        if gaps_data:
            if "raw_response" in gaps_data:
                st.write(gaps_data["raw_response"])
            else:
                st.warning(gaps_data.get("collection_caveat", ""))
                for g in gaps_data.get("gaps", []):
                    with st.container(border=True):
                        st.markdown(f"#### {g.get('title')} (`{g.get('category', 'Gap')}`)")
                        st.write(g.get("description", ""))
                        st.markdown(f"**Why It Matters:** {g.get('why_it_matters', '')}")
                        st.markdown(f"**Supporting Papers:** {', '.join(g.get('supporting_papers', []))}")
                        st.markdown(f"**Evidence Basis:** {g.get('evidence_type', '')} | **Uncertainty:** {g.get('uncertainty_level', 'Medium')}")
                        st.markdown(f"**Proposed Research Question:** *{g.get('proposed_research_question', '')}*")
                        st.markdown(f"**Suggested Methodology:** {g.get('suggested_methodology', '')}")
                        if g.get("verification_search_query"):
                            st.code(f"Novelty Verification Query: {g['verification_search_query']}")

                md_gap = MarkdownExporter.generate_markdown("Research Gap Intelligence Report", gaps_data)
                st.download_button("Export Gap Analysis (.md)", md_gap, file_name="RIA_Gap_Analysis.md", mime="text/markdown")

    with tab_qgen:
        topic = st.text_input("Research Topic or Focus Area", placeholder="e.g., Civic co-governance in urban lake restoration")
        if st.button("Generate Research Questions", type="primary") and topic.strip():
            with st.spinner("Formulating categorized research questions..."):
                try:
                    p_objs = [Paper(**p) for p in target_papers[:10]]
                    q_res = QuestionGenerator.generate_questions(topic.strip(), p_objs)
                    st.session_state.last_questions = q_res
                except Exception as e:
                    st.error(str(e))

        q_data = st.session_state.get("last_questions")
        if q_data:
            if "raw_response" in q_data:
                st.write(q_data["raw_response"])
            else:
                for q in q_data.get("questions", []):
                    with st.container(border=True):
                        st.markdown(f"**[{q.get('category', 'Research')}] {q.get('question', '')}**")
                        st.markdown(f"- **Literature Link:** {q.get('literature_link', '')}")
                        st.markdown(f"- **Motivation & Evidence:** {q.get('motivation_and_evidence', '')}")
                        st.markdown(f"- **Missing Info Needed:** {q.get('missing_information_needed', '')}")
                        st.markdown(f"- **Potential Approach:** {q.get('potential_approach', '')}")
