import pdfplumber
import hashlib
import docdatabase
import fitz
from PyPDF2 import PdfReader
from pathlib import Path

homefolder = Path.home()
dbpath = homefolder / ".cache" / "docsearch" / "docdatabase.db"


# Retrieve hash byte
def file_hash_bytes(data: bytes):
    return hashlib.sha256(data).hexdigest()

# Useless page filter for BM25
def is_bad_page_fast(page_text):
    return len(page_text.strip()) < 30



# ---- Converting TXT files to text ----
def index_txt_bytes(filename, data):
    conn, cur = docdatabase.get_conn(dbpath)

    TXT_LINES_PER_CHUNK = 10
    TXT_OVERLAP = 2
    lines = data.decode("utf-8", errors="ignore").splitlines()  # data arriving in binaries is being decoded
    i = 0
    while i < len(lines):
        start = i
        end = min(i + TXT_LINES_PER_CHUNK, len(lines))
        # the starting and ending lines are determined based on the increment value and the splitting interval, and that section is selected
        text = "\n".join(lines[start:end]).strip()

        if text:
            docdatabase.insert_row(cur, filename, "txt", None, start + 1, end, text)  # writing to the database
        i += TXT_LINES_PER_CHUNK - TXT_OVERLAP
    conn.commit()


# ---- Converting PDF files to text ----
def index_pdf_bytes(filename, data):
    conn, cur = docdatabase.get_conn(dbpath)

    PDF_CHARS_PER_CHUNK = 800
    PDF_OVERLAP = 200

    tmp_path = "/tmp/tmp_upload.pdf"
    with open(tmp_path, "wb") as f:
        f.write(data)

    fhash = file_hash_bytes(data)  # retrieve file hash value
    extracted_any = False

    # FAST FILTER -- the text-containing pages of the PDF file to be processed are filtered using 'PyMuPDF' software
    doc = fitz.open(tmp_path)
    valid_pages = set()

    for i in range(len(doc)):
        try:
            text = doc[i].get_text("text")
            if not is_bad_page_fast(text):
                valid_pages.add(i + 1)
        except Exception:
            continue

    if len(valid_pages) == 0:
        docdatabase.unprocessables(cur, filename, fhash)  # the unprocessable PDF file is being printed to the relevant table

    # Parse Process
    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page_no, page in enumerate(pdf.pages, start=1):
                # fast skip
                if page_no not in valid_pages:  # if the page is not among the pages to be processed, it is skipped
                    continue

                text = None

                try:
                    text = page.extract_text(x_tolerance=2, y_tolerance=2, layout=True)
                except Exception:
                    pass

                if text and len(text.strip()) >= 20:
                    extracted_any = True
                    i = 0
                    while i < len(text):
                        chunk = text[i:i + PDF_CHARS_PER_CHUNK].strip()
                        if chunk:
                            docdatabase.insert_row(cur, filename, "pdf", page_no, None, None, chunk)
                        i += PDF_CHARS_PER_CHUNK - PDF_OVERLAP

        docdatabase.indexed_files(cur, filename, fhash)  # the file path and hash value are printed to the database
        conn.commit()

    except pdfplumber.utils.exceptions.PdfminerException:
        return True

    return True

