import sqlite3
import uuid
import os
import threading

_local = threading.local()

# ----------------------------------------
# Database creation function
def create_database(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # 'documents' table
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

    # 'unporcessables' table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS unprocessables (
        source_name TEXT,
        file_hash TEXT
    )
    """)

    # 'indexed_files' table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS indexed_files (
        source_name TEXT,
        file_hash TEXT
    )
    """)

    conn.commit()
    conn.close()


# ----------------------------------------
# Function for writing data to the 'documents' table in the database
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
# Function for writing data to the 'unprocessables' table in the database
def unprocessables(cur, source_name, file_hash):
    cur.execute("""INSERT INTO unprocessables VALUES (?, ?)""",
        (source_name, file_hash)
    )


# ----------------------------------------
# Function for writing data to the 'indexed_files' table in the database
def indexed_files(cur, source_name, file_hash):
    cur.execute("""INSERT INTO indexed_files VALUES (?, ?)""",
        (source_name, file_hash)
    )


# ----------------------------------------
# Function that establishes a connection to the database
def get_conn(db):
    # it reduces connection costs by opening it only once with each function call
    if not hasattr(_local, "conn"):  # it checks whether this thread has been created before
        _local.conn = sqlite3.connect(db)

    conn = _local.conn  # this thread-specific link is obtained
    cur = conn.cursor()

    return conn, cur


# ----------------------------------------
# Shows the total number of processed files in the database
def totalfiles(db):
  conn, cur = get_conn(db)
  output_num = cur.execute("SELECT COUNT(source_name) FROM indexed_files;").fetchone()[0]
  return output_num


# ----------------------------------------
# A function that deletes information from the database associated with a file that has been removed from the system
def removefile(db):
    conn, cur = get_conn(db)
    #  a list is obtained of all files that the software has passed through, whether processed or unprocessed
    prcfiles = cur.execute("""
        SELECT source_name FROM indexed_files
        UNION ALL
        SELECT source_name FROM unprocessables;
    """).fetchall()

    # if a file that exists in the database does not exist on the computer, it is removed from the database
    for prcfile in [r[0] for r in prcfiles]:
        if not os.path.exists(prcfile):
            cur.execute("DELETE FROM documents WHERE source_name = ?", (prcfile,))
            cur.execute("DELETE FROM indexed_files WHERE source_name = ?", (prcfile,))
            cur.execute("DELETE FROM unprocessables WHERE source_name = ?", (prcfile,))
    conn.commit()

