import pandas as pd
import streamlit as st
from models import Paper
from repository import Repository
from comparator import Comparator
from markdown_exporter import MarkdownExporter
from components import render_header

def render_compare():
    render_header(
        "Cross-Paper Comparison Engine",
        "Evaluate convergence, divergence, methodological differences, and complementarity across multiple studies."
    )

    papers = Repository.get_all_papers()
    if len(papers) < 2:
        st.warning("Save at least 2 papers to your Library to run a cross-paper comparison.")
        return

    paper_map = {f"[{p.get('pmid') or p['id']}] {p['title'][:80]}": p for p in papers}
    selected_labels = st.multiselect("Select 2 to 5 Papers to Compare", list(paper_map.keys()), max_selections=5)

    if len(selected_labels) >= 2 and st.button("Run Comparative Synthesis", type="primary"):
        selected_objs = [Paper(**paper_map[lbl]) for lbl in selected_labels]
        with st.spinner("Comparing methodologies, findings, and limitations across selected papers..."):
            try:
                comp = Comparator.compare_papers(selected_objs)
                st.session_state.last_comparison = comp
                Repository.save_analysis("comparison", f"Comparison ({len(selected_objs)} papers)", comp)
            except Exception as e:
                st.error(str(e))

    comp = st.session_state.get("last_comparison")
    if comp:
        if "raw_response" in comp:
            st.write(comp["raw_response"])
            return

        if comp.get("comparison_matrix"):
            st.subheader("Structured Comparison Matrix")
            st.dataframe(pd.DataFrame(comp["comparison_matrix"]), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Convergence (Shared Findings)")
            for item in comp.get("convergence", []):
                st.markdown(f"- {item}")
            st.markdown("#### Methodological Differences")
            for item in comp.get("methodological_differences", []):
                st.markdown(f"- {item}")
        with c2:
            st.markdown("#### Divergence (Differing Outcomes)")
            for item in comp.get("divergence", []):
                st.markdown(f"- {item}")
            st.markdown("#### Complementarity & Unresolved Questions")
            for item in comp.get("complementarity", []) + comp.get("unresolved_questions", []):
                st.markdown(f"- {item}")

        if comp.get("written_synthesis"):
            st.subheader("Comparative Synthesis")
            st.write(comp["written_synthesis"])

        md_out = MarkdownExporter.generate_markdown("Cross-Paper Comparison Report", comp)
        st.download_button("Export Comparison (.md)", md_out, file_name="RIA_Comparison_Report.md", mime="text/markdown")
