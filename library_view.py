import streamlit as st
from repository import Repository
from csv_exporter import CSVExporter
from markdown_exporter import MarkdownExporter
from components import render_header

def render_library(navigate_callback):
    render_header(
        "My Research Library",
        "Persistent SQLite storage for saved publications, thematic collections, research notes, and saved AI analyses."
    )

    tab_papers, tab_cols, tab_notes, tab_analyses = st.tabs([
        "Saved Publications", "Collections", "Research Notes", "Saved AI Analyses"
    ])

    with tab_papers:
        papers = Repository.get_all_papers()
        f1, f2 = st.columns([0.7, 0.3])
        with f1:
            filter_q = st.text_input("Filter Library by Title, Author, or Journal")
        with f2:
            st.write("")
            st.write("")
            if papers:
                csv_str = CSVExporter.generate_csv(papers)
                st.download_button("Export Library CSV", csv_str, file_name="RIA_Library.csv", mime="text/csv", use_container_width=True)

        filtered = [
            p for p in papers
            if not filter_q.strip()
            or filter_q.lower() in p.get("title", "").lower()
            or filter_q.lower() in (p.get("journal") or "").lower()
            or filter_q.lower() in " ".join(p.get("authors", [])).lower()
        ]

        if not filtered:
            st.info("No matching publications found in your library.")
        else:
            for p in filtered:
                with st.container(border=True):
                    c_left, c_right = st.columns([0.8, 0.2])
                    with c_left:
                        st.markdown(f"**{p['title']}**")
                        st.caption(f"{', '.join(p.get('authors', [])[:4])} | {p.get('journal')} | {p.get('publication_date')} | PMID: {p.get('pmid') or 'N/A'}")
                    with c_right:
                        if st.button("Open", key=f"lib_open_{p['id']}", use_container_width=True):
                            st.session_state.selected_paper = p
                            navigate_callback("Research Workspace")
                        if st.button("Delete", key=f"lib_del_{p['id']}", use_container_width=True):
                            Repository.delete_paper(p["id"])
                            st.rerun()

    with tab_cols:
        with st.form("new_collection_form"):
            c_name = st.text_input("New Collection Name", placeholder="e.g., Urban Commons & Water Governance")
            c_desc = st.text_input("Description")
            if st.form_submit_button("Create Collection") and c_name.strip():
                Repository.create_collection(c_name.strip(), c_desc.strip())
                st.success(f"Collection '{c_name.strip()}' created.")
                st.rerun()

        collections = Repository.get_collections()
        for col in collections:
            with st.expander(f"📁 {col['name']} ({col['paper_count']} papers)"):
                st.write(col.get("description") or "No description.")
                col_papers = Repository.get_papers_in_collection(col["id"])
                for cp in col_papers:
                    st.markdown(f"- **{cp['title']}** ({cp.get('publication_year') or 'N/A'})")

    with tab_notes:
        notes = Repository.get_notes()
        if not notes:
            st.info("No saved notes yet.")
        else:
            for n in notes:
                with st.container(border=True):
                    st.markdown(f"**{n['title']}**")
                    if n.get("paper_title"):
                        st.caption(f"Linked Paper: {n['paper_title']} • {n['created_at']}")
                    st.write(n["content"])

    with tab_analyses:
        analyses = Repository.get_saved_analyses()
        if not analyses:
            st.info("No saved AI analyses yet.")
        else:
            for a in analyses:
                with st.expander(f"[{a['analysis_type']}] {a['title']} ({a['created_at']})"):
                    st.json(a["data"])
                    md_a = MarkdownExporter.generate_markdown(a["title"], a["data"])
                    st.download_button("Export Analysis (.md)", md_a, file_name=f"RIA_Analysis_{a['id']}.md", key=f"exp_a_{a['id']}")
