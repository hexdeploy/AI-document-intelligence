# app/services/parser.py
import fitz  # PyMuPDF
from fastapi import HTTPException

class DocumentParser:
    @staticmethod
    def parse_pdf(file_bytes: bytes) -> tuple[str, int]:
        """
        Parses raw PDF bytes, extracts all text, and tracks total pages.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
            full_text = ""
            
            for page in doc:
                full_text += page.get_text() + "\n"
                
            return full_text.strip(), total_pages
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

    @staticmethod
    def parse_txt(file_bytes: bytes) -> tuple[str, int]:
        """
        Parses raw text files. Decodes bytes and defaults page count to 1.
        """
        try:
            text = file_bytes.decode("utf-8")
            return text.strip(), 1
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process text file: {str(e)}")