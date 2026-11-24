import json
from typing import List, Optional, Dict, Any
from database.db import get_db_connection
from config.settings import DB_PATH
from core.models import Paper

class Repository:
    @staticmethod
    def _deserialize_paper(row: dict) -> dict:
        d = dict(row)
        try:
            d["authors"] = json.loads(d["authors"]) if d.get("authors") else []
        except Exception:
            d["authors"] = []
        try:
            d["raw_metadata"] = json.loads(d["raw_metadata"]) if d.get("raw_metadata") else {}
        except Exception:
            d["raw_metadata"] = {}
        return d

    @staticmethod
    def save_paper(paper: Paper, db_path=DB_PATH) -> int:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            if paper.pmid:
                cursor.execute("SELECT id FROM papers WHERE pmid = ?", (paper.pmid,))
                existing = cursor.fetchone()
                if existing:
                    return existing["id"]
            else:
                cursor.execute("SELECT id FROM papers WHERE title = ?", (paper.title,))
                existing = cursor.fetchone()
                if existing:
                    return existing["id"]

            cursor.execute("""
                INSERT INTO papers (
                    pmid, doi, title, authors, journal, publication_year,
                    publication_date, abstract, publication_type, source, url, raw_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.pmid,
                paper.doi,
                paper.title,
                json.dumps(paper.authors),
                paper.journal,
                paper.publication_year,
                paper.publication_date,
                paper.abstract,
                paper.publication_type,
                paper.source,
                paper.url,
                json.dumps(paper.raw_metadata),
            ))
            return cursor.lastrowid

    @staticmethod
    def get_all_papers(db_path=DB_PATH) -> List[Dict[str, Any]]:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM papers ORDER BY created_at DESC")
            return [Repository._deserialize_paper(row) for row in cursor.fetchall()]

    @staticmethod
    def get_paper_by_id(paper_id: int, db_path=DB_PATH) -> Optional[Dict[str, Any]]:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
            row = cursor.fetchone()
            return Repository._deserialize_paper(row) if row else None

    @staticmethod
    def delete_paper(paper_id: int, db_path=DB_PATH):
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))

    @staticmethod
    def create_collection(name: str, description: str = "", db_path=DB_PATH) -> int:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM collections WHERE name = ?", (name,))
            existing = cursor.fetchone()
            if existing:
                return existing["id"]
            cursor.execute("INSERT INTO collections (name, description) VALUES (?, ?)", (name, description))
            return cursor.lastrowid

    @staticmethod
    def get_collections(db_path=DB_PATH) -> List[Dict[str, Any]]:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, COUNT(cp.paper_id) as paper_count
                FROM collections c
                LEFT JOIN collection_papers cp ON c.id = cp.collection_id
                GROUP BY c.id
                ORDER BY c.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def add_paper_to_collection(collection_id: int, paper_id: int, db_path=DB_PATH):
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO collection_papers (collection_id, paper_id) VALUES (?, ?)",
                (collection_id, paper_id)
            )

    @staticmethod
    def get_papers_in_collection(collection_id: int, db_path=DB_PATH) -> List[Dict[str, Any]]:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.* FROM papers p
                INNER JOIN collection_papers cp ON p.id = cp.paper_id
                WHERE cp.collection_id = ?
                ORDER BY p.created_at DESC
            """, (collection_id,))
            return [Repository._deserialize_paper(row) for row in cursor.fetchall()]

    @staticmethod
    def save_note(paper_id: Optional[int], title: str, content: str, db_path=DB_PATH) -> int:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (paper_id, title, content) VALUES (?, ?, ?)",
                (paper_id, title, content)
            )
            return cursor.lastrowid

    @staticmethod
    def get_notes(db_path=DB_PATH) -> List[Dict[str, Any]]:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.*, p.title as paper_title
                FROM notes n
                LEFT JOIN papers p ON n.paper_id = p.id
                ORDER BY n.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def save_analysis(analysis_type: str, title: str, data: dict, paper_id: Optional[int] = None, db_path=DB_PATH) -> int:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO saved_analyses (paper_id, analysis_type, title, data) VALUES (?, ?, ?, ?)",
                (paper_id, analysis_type, title, json.dumps(data))
            )
            return cursor.lastrowid

    @staticmethod
    def get_saved_analyses(analysis_type: Optional[str] = None, db_path=DB_PATH) -> List[Dict[str, Any]]:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            if analysis_type:
                cursor.execute(
                    "SELECT * FROM saved_analyses WHERE analysis_type = ? ORDER BY created_at DESC",
                    (analysis_type,)
                )
            else:
                cursor.execute("SELECT * FROM saved_analyses ORDER BY created_at DESC")
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                try:
                    d["data"] = json.loads(d["data"])
                except Exception:
                    d["data"] = {}
                results.append(d)
            return results
