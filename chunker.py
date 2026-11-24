import re
from typing import List, Dict, Any
from core.models import Paper

class DocumentChunker:
    @staticmethod
    def chunk_paper(paper: Paper, max_chars: int = 450) -> List[Dict[str, Any]]:
        if not paper.abstract:
            return []
        sentences = re.split(r'(?<=[.!?])\s+', paper.abstract.strip())
        chunks = []
        current = ""
        chunk_idx = 0

        for sent in sentences:
            if len(current) + len(sent) + 1 <= max_chars:
                current = f"{current} {sent}".strip()
            else:
                if current:
                    chunks.append({
                        "chunk_id": f"{paper.pmid or paper.title[:20]}_c{chunk_idx}",
                        "pmid": paper.pmid,
                        "title": paper.title,
                        "year": paper.publication_year,
                        "text": current
                    })
                    chunk_idx += 1
                current = sent

        if current:
            chunks.append({
                "chunk_id": f"{paper.pmid or paper.title[:20]}_c{chunk_idx}",
                "pmid": paper.pmid,
                "title": paper.title,
                "year": paper.publication_year,
                "text": current
            })
        return chunks
