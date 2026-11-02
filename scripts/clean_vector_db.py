import sqlite3
from pathlib import Path

db_path = Path("vector_db/vectors.db")
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("DELETE FROM passages WHERE document_id NOT IN ('HP-OPS-01', 'HP-MNT-01', 'AC-OM-01')")
    conn.commit()
    count = c.execute("SELECT count(*) FROM passages").fetchone()[0]
    print(f"Purged test manuals. Total active official chunks in vector store: {count}")
    conn.close()
