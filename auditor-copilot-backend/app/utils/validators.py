ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "xlsx", "xls", "csv"}

def validate_file(filename: str):
    ext = filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

"""
File validation utility for allowed document types.
"""

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "xlsx", "xls", "csv"}

# validate_file checks if the file extension is allowed, raises ValueError if not.
