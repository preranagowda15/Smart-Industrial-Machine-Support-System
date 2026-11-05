import sqlite3

conn = sqlite3.connect("vector_db/vectors.db")
rows = conn.execute("SELECT id, document_id, metadata_json FROM passages WHERE document_id = 'HP'").fetchall()
print(f"Found {len(rows)} rows with document_id='HP'")
for r in rows[:3]:
    print(r)

# Delete these stale/corrupt rows with document_id='HP'
conn.execute("DELETE FROM passages WHERE document_id = 'HP'")
conn.commit()
print("Deleted stale 'HP' rows.")

rows_after = conn.execute("SELECT DISTINCT document_id, COUNT(*) FROM passages GROUP BY document_id").fetchall()
print("Current document groups:", rows_after)

