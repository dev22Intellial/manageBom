import os
from .parsers import XLSXParser, CSVParser, DOCXParser, PDFParser, TXTParser

def get_bom_parser(file_path, original_filename):
    """
    Returns an instance of the appropriate BOM parser based on the original file extension.
    The file_path is the temporary path where the file content is stored.
    """
    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()

    if ext == '.xlsx':
        return XLSXParser()
    elif ext == '.csv':
        return CSVParser()
    elif ext == '.docx':
        return DOCXParser()
    elif ext == '.pdf':
        return PDFParser()
    elif ext == '.txt':
        return TXTParser()
    else:
        raise ValueError(f"Unsupported file type: {ext}")