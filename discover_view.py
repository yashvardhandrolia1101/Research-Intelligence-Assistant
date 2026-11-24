import streamlit as st
from search_engine import SearchEngine
from repository import Repository
from components import render_header

def render_discover(navigate_callback):
    render_header(
        "Discover Scientific Literature",
        "Query PubMed / NCBI E-utilities with structured filters, query diagnostics, and one-click library ingestion."
    )

    default_q = st.session_state.pop("pending_search", "") or st.session_state.get("last_query", "")

    with st.form("pubmed_search_form"):
        col1, col2, col3 = st.columns([0.55, 0.25, 0.20])
        with col1:
            query = st.text_input("Keywords, Boolean Query, PMID, or DOI", value=default_q, placeholder="e.g., ecological gentrification OR urban wetlands")
        with col2:
            sort_by = st.selectbox("Sort Order", ["relevance", "date"], format_func=lambda x: "Relevance" if x == "relevance" else "Newest First")
        with col3:
            max_results = st.selectbox("Results per Page", [10, 20, 30, 50], index=0)

        with st.expander("Advanced Filters (Author, Journal, Year Range, Publication Type)"):
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                author = st.text_input("Author Name")
            with f2:
                journal = st.text_input("Journal Name")
            with f3:
                pub_type = st.selectbox("Publication Type", ["All", "Journal Article", "Review", "Systematic Review", "Meta-Analysis", "Clinical Trial"])
            with f4:
                exact_phrase = st.checkbox("Exact Phrase Match")

            y1, y2 = st.columns(2)
            with y1:
                use_years = st.checkbox("Filter by Publication Year Range")
            with y2:
                year_range = st.slider("Years", 1990, 2026, (2015, 2026), disabled=not use_years)

        submitted = st.form_submit_button("Run Discovery Search", type="primary")

    if submitted and query.strip():
        st.session_state.last_query = query.strip()
        st.session_state.search_offset = 0
        with st.spinner("Retrieving records from PubMed E-utilities..."):
            try:
                res = SearchEngine.search_literature(
                    query=query.strip(),
                    max_results=max_results,
                    offset=0,
                    sort=sort_by,
                    min_year=year_range[0] if use_years else None,
                    max_year=year_range[1] if use_years else None,
                    author=author,
                    journal=journal,
                    pub_type=pub_type,
                    exact_phrase=exact_phrase
                )
                st.session_state.search_data = res
            except Exception as e:
                st.error(f"Retrieval Error: {str(e)}")

    search_data = st.session_state.get("search_data")
    if search_data:
        papers = search_data.get("papers", [])
        total = search_data.get("total_count", 0)
        diag = search_data.get("diagnostics", {})

        st.markdown(f"**Effective Query:** `{search_data.get('effective_query')}` — **{total:,}** total matches in PubMed (showing {len(papers)}).")

        if diag:
            with st.expander(f"Search Intelligence Diagnostics: {diag.get('scope_status', 'Balanced')}", expanded=(total == 0 or total > 5000)):
                st.write(diag.get("explanation", ""))
                for sug in diag.get("suggestions", []):
                    st.markdown(f"- **Suggested Refinement:** `{sug['query']}` — *{sug['reason']}*")

        if not papers:
            st.warning("No records matched this query. Try broadening terms or checking spelling.")
            return

        collections = Repository.get_collections()
        col_map = {c["name"]: c["id"] for c in collections}

        for idx, paper in enumerate(papers):
            with st.container(border=True):
                top_l, top_r = st.columns([0.78, 0.22])
                with top_l:
                    st.markdown(f"#### {idx + 1}. {paper.title}")
                    authors_str = ", ".join(paper.authors[:5]) + (" et al." if len(paper.authors) > 5 else "") if paper.authors else "Authors not listed"
                    st.caption(f"{authors_str} | **{paper.journal}** | {paper.publication_date} | Type: {paper.publication_type}")
                    id_line = f"PMID: `{paper.pmid or 'N/A'}` • DOI: `{paper.doi or 'N/A'}`"
                    if paper.url:
                        id_line += f" • [View on PubMed]({paper.url})"
                    st.markdown(id_line)
                    if paper.abstract:
                        st.write(paper.abstract[:420] + ("..." if len(paper.abstract) > 420 else ""))
                    else:
                        st.warning("No abstract available in PubMed record.")

                with top_r:
                    if st.button("Save to Library", key=f"disc_save_{idx}", use_container_width=True):
                        pid = Repository.save_paper(paper)
                        st.toast(f"Saved to Library (ID #{pid})")
                    if st.button("Analyse Paper", key=f"disc_ana_{idx}", type="primary", use_container_width=True):
                        pid = Repository.save_paper(paper)
                        saved = Repository.get_paper_by_id(pid)
                        st.session_state.selected_paper = saved
                        navigate_callback("Research Workspace")
                    if col_map:
                        target_col = st.selectbox("Add to Collection", ["Select..."] + list(col_map.keys()), key=f"disc_col_{idx}", label_visibility="collapsed")
                        if target_col != "Select...":
                            pid = Repository.save_paper(paper)
                            Repository.add_paper_to_collection(col_map[target_col], pid)
                            st.toast(f"Added to '{target_col}'")
