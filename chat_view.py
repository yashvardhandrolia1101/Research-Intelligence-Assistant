import streamlit as st
from models import Paper
from repository import Repository
from retriever import RAGRetriever
from components import render_header

def render_chat():
    render_header(
        "AI Research Assistant (RAG-Grounded)",
        "Ask questions grounded in passage-level retrieval from your saved scientific literature."
    )

    papers = Repository.get_all_papers()
    collections = Repository.get_collections()

    c1, c2 = st.columns([0.75, 0.25])
    with c1:
        scope_opts = ["All Saved Library Papers"] + [f"Collection: {c['name']}" for c in collections]
        scope = st.selectbox("Grounding Literature Scope", scope_opts)
    with c2:
        st.write("")
        st.write("")
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if scope == "All Saved Library Papers":
        active_papers = [Paper(**p) for p in papers]
    else:
        col_name = scope.replace("Collection: ", "", 1)
        col_id = next((c["id"] for c in collections if c["name"] == col_name), None)
        active_papers = [Paper(**p) for p in (Repository.get_papers_in_collection(col_id) if col_id else [])]

    st.caption(f"Indexing **{len(active_papers)}** papers for passage-level retrieval.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("passages"):
                with st.expander("View Retrieved Evidence Passages"):
                    for p in msg["passages"]:
                        st.markdown(f"**{p['title']}** (PMID: {p.get('pmid') or 'N/A'} | Score: {p['relevance_score']})")
                        st.caption(p["text"])

    prompt = st.chat_input("Ask a question about methodologies, findings, limitations, or comparisons...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant passages and synthesizing grounded response..."):
                try:
                    result = RAGRetriever.answer_with_rag(prompt, active_papers, st.session_state.chat_history)
                    st.write(result["answer"])
                    if result["passages"]:
                        with st.expander("View Retrieved Evidence Passages"):
                            for p in result["passages"]:
                                st.markdown(f"**{p['title']}** (PMID: {p.get('pmid') or 'N/A'} | Score: {p['relevance_score']})")
                                st.caption(p["text"])
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "passages": result["passages"]
                    })
                except Exception as e:
                    st.error(str(e))
