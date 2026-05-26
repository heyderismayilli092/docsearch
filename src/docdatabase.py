import sqlite3
import uuid
import threading

_local = threading.local()

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
def create_database(db):
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
    conn.close()


# ----------------------------------------
def get_conn(db):
    # it reduces connection costs by opening it only once with each function call
    if not hasattr(_local, "conn"):  # it checks whether this thread has been created before
        _local.conn = sqlite3.connect(db)

    conn = _local.conn  # this thread-specific link is obtained
    cur = conn.cursor()

    return conn, cur


# ----------------------------------------
def totalfiles(db):
  conn, cur = get_conn(db)
  output_num = cur.execute("SELECT COUNT(DISTINCT source_name) FROM documents;").fetchone()[0]
  try:
    return output_num
  finally:
    conn.close()


