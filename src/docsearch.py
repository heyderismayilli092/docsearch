from rank_bm25 import BM25Okapi
import docdatabase
import os


# bm25 algorithm loading
def load_bm25(db_path):
    if not os.path.exists(db_path):
        raise BaseException(f"database not found: {db_path}")

    conn, cur = docdatabase.init_storage(db_path)  # connection database

    cur.execute("SELECT source_name, source_type, page_number, line_start, line_end, chunk FROM documents")  # reading database
    rows = cur.fetchall()

    if not rows:
        raise BaseException("database empty")

    corpus = [r[5].lower().split() for r in rows]
    bm25 = BM25Okapi(corpus)  # creating bm25 model
    return conn, rows, bm25



# search with BM25
def bm25_search(db_path, query, top_k):
    conn, rows, bm25 = load_bm25(db_path)

    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)  # the relevance scores of each query to each document are calculated

    ranked = sorted(
        zip(scores, rows),
        key=lambda x: x[0],
        reverse=True
    )[:top_k]

    results = []

    for score, row in ranked:
        if score <= 0:
            continue

        src, stype, page, ls, le, chunk = row

        results.append({
            "source": src,
            "type": stype,
            "page": page,
            "line_start": ls,
            "line_end": le,
            "score": float(score),
            "chunk": chunk
        })

    conn.close()

    return {
        "query": query,
        "results": results
    }

