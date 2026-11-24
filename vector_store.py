import math
import re
from collections import Counter
from typing import List, Dict, Any

class LocalTFIDFVectorStore:
    """Deterministic TF-IDF cosine similarity store requiring zero external heavyweight model downloads."""
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.doc_freqs: Counter = Counter()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [w for w in re.findall(r'[a-z0-9]+', text.lower()) if len(w) > 2]

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        for chunk in chunks:
            tokens = self._tokenize(chunk["text"])
            tf = Counter(tokens)
            for term in set(tokens):
                self.doc_freqs[term] += 1
            self.chunks.append({**chunk, "_tf": tf, "_len": len(tokens)})

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return self.chunks[:top_k]

        q_tf = Counter(q_tokens)
        n_docs = len(self.chunks)
        scored = []

        for chunk in self.chunks:
            dot = 0.0
            norm_q = 0.0
            norm_d = 0.0
            for term, q_count in q_tf.items():
                idf = math.log((n_docs + 1) / (self.doc_freqs.get(term, 0) + 1)) + 1.0
                wq = q_count * idf
                wd = chunk["_tf"].get(term, 0) * idf
                dot += wq * wd
                norm_q += wq * wq

            for term, d_count in chunk["_tf"].items():
                idf = math.log((n_docs + 1) / (self.doc_freqs.get(term, 0) + 1)) + 1.0
                wd = d_count * idf
                norm_d += wd * wd

            denom = math.sqrt(norm_q) * math.sqrt(norm_d)
            score = (dot / denom) if denom > 0 else 0.0
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, c in scored[:top_k]:
            clean_chunk = {k: v for k, v in c.items() if not k.startswith("_")}
            clean_chunk["relevance_score"] = round(score, 4)
            results.append(clean_chunk)
        return results
