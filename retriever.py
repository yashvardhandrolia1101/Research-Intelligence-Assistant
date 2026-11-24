from typing import List, Dict, Any
from models import Paper
from chunker import DocumentChunker
from vector_store import LocalTFIDFVectorStore
from provider import AIProvider
from prompts import CHAT_SYSTEM_PROMPT

class RAGRetriever:
    @staticmethod
    def retrieve_relevant_passages(query: str, papers: List[Paper], top_k: int = 5) -> List[Dict[str, Any]]:
        store = LocalTFIDFVectorStore()
        for p in papers:
            chunks = DocumentChunker.chunk_paper(p)
            store.add_chunks(chunks)
        return store.search(query, top_k=top_k)

    @classmethod
    def answer_with_rag(cls, query: str, papers: List[Paper], chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        passages = cls.retrieve_relevant_passages(query, papers, top_k=5)
        if not passages:
            context_block = "No saved or selected paper passages were available."
        else:
            context_block = "\n\n".join([
                f"[Source: {p['title']} | PMID: {p.get('pmid') or 'N/A'} | Similarity: {p['relevance_score']}]\n{p['text']}"
                for p in passages
            ])

        history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in chat_history[-4:]])
        prompt = (
            f"Retrieved Literature Passages:\n{context_block}\n\n"
            f"Recent Conversation:\n{history_text}\n\n"
            f"User Question: {query}\n\n"
            f"Provide a grounded, citation-backed answer."
        )
        answer = AIProvider.generate(prompt, system_prompt=CHAT_SYSTEM_PROMPT)
        return {
            "answer": answer,
            "passages": passages
        }
