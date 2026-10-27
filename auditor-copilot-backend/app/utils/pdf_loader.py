from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    TextLoader
)
import tempfile
import os

def load_document(file_bytes: bytes, filename: str):
    suffix = filename.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if suffix == "pdf":
            loader = PyPDFLoader(tmp_path)
        elif suffix in ["docx", "doc"]:
            loader = UnstructuredWordDocumentLoader(tmp_path)
        elif suffix in ["xlsx", "xls"]:
            loader = UnstructuredExcelLoader(tmp_path)
        elif suffix == "csv":
            loader = CSVLoader(tmp_path)
        elif suffix == "txt":
            loader = TextLoader(tmp_path, encoding="utf-8")
        else:
            raise ValueError("Unsupported file type")

        return loader.load()

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

"""
Utility for loading and parsing document files (PDF, Word, Excel, CSV, TXT) into text chunks.
"""

# load_document saves the uploaded file to a temp file, loads it with the appropriate loader, and returns parsed content.
