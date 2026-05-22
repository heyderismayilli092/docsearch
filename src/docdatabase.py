import sqlite3
import uuid


# ----------------------------------------
def insert_row(cur, source, stype, page, l_start, l_end, chunk):
    cur.execute("""
        INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),  # unique 128-bit number is generated for this chunk
        source,  # source file path or name
        stype,  # source file type
        page,  # page num
        l_start,  # line start
        l_end,  # line end
        chunk  # chunk text
    ))


# ----------------------------------------
def init_storage(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        source_name TEXT,
        source_type TEXT,
        page_number INTEGER,
        line_start INTEGER,
        line_end INTEGER,
        chunk TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS indexed_files (
        source_name TEXT PRIMARY KEY,
        file_hash TEXT
    )
    """)

    conn.commit()

    return conn, cur

