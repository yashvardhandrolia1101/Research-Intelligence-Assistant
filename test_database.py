from database.db import init_db
from database.repository import Repository
from core.models import Paper

def test_database_persistence_and_collections(tmp_path):
    test_db = tmp_path / "test_ria.db"
    init_db(test_db)

    p = Paper(
        pmid="11223344",
        doi="10.1000/test",
        title="Thermodynamic Modeling of Enzyme Kinetics",
        authors=["Y. Drolia", "B. Reddy"],
        journal="Journal of Physical Chemistry",
        publication_year="2026",
        publication_date="2026",
        abstract="We evaluate activation barriers across catalytic pathways."
    )
    pid = Repository.save_paper(p, db_path=test_db)
    assert pid > 0

    # Duplicate save should return same ID without duplicating row
    pid_dup = Repository.save_paper(p, db_path=test_db)
    assert pid_dup == pid
    assert len(Repository.get_all_papers(db_path=test_db)) == 1

    cid = Repository.create_collection("Biochem", "Enzyme papers", db_path=test_db)
    Repository.add_paper_to_collection(cid, pid, db_path=test_db)
    col_papers = Repository.get_papers_in_collection(cid, db_path=test_db)
    assert len(col_papers) == 1
    assert col_papers[0]["pmid"] == "11223344"

    nid = Repository.save_note(pid, "Key takeaway", "Check Arrhenius pre-exponential factor.", db_path=test_db)
    assert nid > 0
    assert len(Repository.get_notes(db_path=test_db)) == 1
