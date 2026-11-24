import streamlit as st
from models import Paper
from repository import Repository
from summarizer import Summarizer
from extractor import Extractor
from simplifier import Simplifier
from markdown_exporter import MarkdownExporter
from pdf_exporter import PDFExporter
from components import render_header

def render_workspace():
    render_header(
        "Research Workspace — Single-Paper Intelligence",
        "Interrogate methodology, extract structured evidence, calibrate explanation depth, and record traceable notes."
    )

    all_papers = Repository.get_all_papers()
    if not all_papers and not st.session_state.get("selected_paper"):
        st.info("No papers available yet. Discover and save a paper first.")
        return

    paper_options = {f"[{p.get('pmid') or p['id']}] {p['title'][:85]}": p for p in all_papers}
    current = st.session_state.get("selected_paper")

    if paper_options:
        default_idx = 0
        if current:
            for i, p in enumerate(paper_options.values()):
                if p["id"] == current.get("id"):
                    default_idx = i
                    break
        chosen_label = st.selectbox("Active Paper in Workspace", list(paper_options.keys()), index=default_idx)
        paper_dict = paper_options[chosen_label]
        st.session_state.selected_paper = paper_dict
    else:
        paper_dict = current

    paper_obj = Paper(**paper_dict)

    st.markdown(f"### {paper_obj.title}")
    st.caption(f"Authors: {', '.join(paper_obj.authors) or 'Not listed'} | Journal: {paper_obj.journal} | Date: {paper_obj.publication_date} | PMID: {paper_obj.pmid or 'N/A'} | DOI: {paper_obj.doi or 'N/A'}")
    st.markdown('<div class="ria-disclaimer">Evidence Transparency: Analysis below is grounded strictly in available source text. Missing methodological details are explicitly flagged.</div>', unsafe_allow_html=True)

    with st.expander("View Full Abstract & Source Metadata", expanded=True):
        st.write(paper_obj.abstract or "No abstract available in source metadata.")

    tab_extract, tab_sum, tab_simp, tab_notes = st.tabs([
        "1. Structured Intelligence Extraction",
        "2. Multi-Level Summarisation",
        "3. Scientific Simplification",
        "4. Notes & Export"
    ])

    with tab_extract:
        if st.button("Extract Structured Intelligence Record", type="primary"):
            with st.spinner("Extracting problem, methodology, variables, findings, and limitations..."):
                try:
                    structured = Extractor.extract_structured(paper_obj)
                    st.session_state[f"struct_{paper_obj.id}"] = structured.model_dump()
                    Repository.save_analysis("structured_extraction", paper_obj.title, structured.model_dump(), paper_obj.id)
                except Exception as e:
                    st.error(str(e))

        s_data = st.session_state.get(f"struct_{paper_obj.id}")
        if s_data:
            st.info(f"Scope Basis: {s_data.get('analysis_scope', 'Abstract-based')}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Research Problem:** {s_data.get('research_problem')}")
                st.markdown(f"**Research Question:** {s_data.get('research_question')}")
                st.markdown(f"**Hypothesis:** {s_data.get('hypothesis')}")
                st.markdown(f"**Methodology:** {s_data.get('methodology')}")
                st.markdown(f"**Dataset / Sample:** {s_data.get('dataset_or_sample')}")
            with c2:
                st.markdown("**Principal Findings:**")
                for item in s_data.get("principal_findings", []):
                    st.markdown(f"- {item}")
                st.markdown(f"**Statistical Results:** {s_data.get('statistical_results')}")
                st.markdown(f"**Conclusions:** {s_data.get('conclusions')}")
                st.markdown("**Limitations:**")
                for lim in s_data.get("limitations", []):
                    st.markdown(f"- {lim}")
            if s_data.get("explicit_vs_inferred_notes"):
                st.caption(f"Epistemic Audit: {s_data['explicit_vs_inferred_notes']}")

    with tab_sum:
        depth = st.selectbox("Summary Depth Mode", ["Executive", "Detailed", "Beginner", "Undergraduate", "Technical"])
        if st.button("Generate Calibrated Summary", type="primary"):
            with st.spinner(f"Generating {depth} summary..."):
                try:
                    res = Summarizer.summarize_paper(paper_obj, depth=depth)
                    st.session_state[f"sum_{paper_obj.id}"] = res
                    Repository.save_analysis(f"summary_{depth.lower()}", paper_obj.title, res, paper_obj.id)
                except Exception as e:
                    st.error(str(e))

        sum_data = st.session_state.get(f"sum_{paper_obj.id}")
        if sum_data:
            if "raw_response" in sum_data:
                st.write(sum_data["raw_response"])
            else:
                st.caption(f"Basis: {sum_data.get('source_basis', 'Abstract-only')}")
                st.markdown(f"**Executive Summary:** {sum_data.get('executive_summary', '')}")
                st.markdown(f"**Detailed Explanation:** {sum_data.get('detailed_explanation', '')}")
                st.markdown(f"**Methodology Overview:** {sum_data.get('methodology_overview', '')}")
                if sum_data.get("key_findings"):
                    st.markdown("**Key Findings:**")
                    for kf in sum_data["key_findings"]:
                        st.markdown(f"- {kf}")
                if sum_data.get("missing_information"):
                    st.warning("Missing Information: " + "; ".join(sum_data["missing_information"]))

    with tab_simp:
        passage = st.text_area("Passage or Concept to Explain", value=paper_obj.abstract or "", height=140)
        level = st.selectbox("Explanation Style", [
            "Beginner-friendly", "High-school level", "Undergraduate level",
            "Advanced technical", "Analogy-based", "Step-by-step"
        ])
        if st.button("Explain Passage", type="primary"):
            with st.spinner("Generating scientifically faithful explanation..."):
                try:
                    explanation = Simplifier.simplify_passage(passage, level=level)
                    st.session_state[f"simp_{paper_obj.id}"] = explanation
                except Exception as e:
                    st.error(str(e))

        if st.session_state.get(f"simp_{paper_obj.id}"):
            st.markdown(st.session_state[f"simp_{paper_obj.id}"])

    with tab_notes:
        with st.form("note_form"):
            n_title = st.text_input("Note Title", value=f"Notes on {paper_obj.title[:50]}")
            n_body = st.text_area("Research Note Content", height=130)
            if st.form_submit_button("Save Research Note"):
                if n_body.strip():
                    Repository.save_note(paper_obj.id, n_title.strip(), n_body.strip())
                    st.success("Note saved to persistent SQLite library.")

        st.markdown("---")
        st.subheader("Export Paper Report")
        export_sections = {
            "Bibliographic Metadata": f"Authors: {', '.join(paper_obj.authors)}\nJournal: {paper_obj.journal}\nDate: {paper_obj.publication_date}\nPMID: {paper_obj.pmid}\nDOI: {paper_obj.doi}",
            "Abstract": paper_obj.abstract or "Not available.",
            "Structured Intelligence": st.session_state.get(f"struct_{paper_obj.id}", "Not yet generated."),
            "Summary": st.session_state.get(f"sum_{paper_obj.id}", "Not yet generated.")
        }
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            md_str = MarkdownExporter.generate_markdown(paper_obj.title, export_sections)
            st.download_button("Download Markdown (.md)", md_str, file_name=f"RIA_Paper_{paper_obj.pmid or paper_obj.id}.md", mime="text/markdown")
        with col_e2:
            pdf_bytes = PDFExporter.generate_report_pdf(paper_obj.title, export_sections)
            st.download_button("Download PDF Report (.pdf)", pdf_bytes, file_name=f"RIA_Paper_{paper_obj.pmid or paper_obj.id}.pdf", mime="application/pdf")
