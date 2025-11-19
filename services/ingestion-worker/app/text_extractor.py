# FILE: services/ingestion-worker/app/text_extractor.py

from PyPDF2 import PdfReader
from docx import Document
import io
import logging

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from various document formats."""

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """
        Extract text from PDF file.

        Args:
            file_bytes: PDF file as bytes

        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        """
        Extract text from DOCX file.

        Args:
            file_bytes: DOCX file as bytes

        Returns:
            Extracted text content
        """
        try:
            doc = Document(io.BytesIO(file_bytes))
            text_parts = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise

    @staticmethod
    def extract_from_txt(file_bytes: bytes) -> str:
        """
        Extract text from TXT/MD file.

        Args:
            file_bytes: Text file as bytes

        Returns:
            Extracted text content
        """
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            return file_bytes.decode('latin-1')

    @staticmethod
    def extract_text(file_bytes: bytes, file_extension: str) -> str:
        """
        Extract text based on file extension.

        Args:
            file_bytes: File content as bytes
            file_extension: File extension (pdf, docx, txt, md, etc.)

        Returns:
            Extracted text content
        """
        ext = file_extension.lower()

        if ext == 'pdf':
            return TextExtractor.extract_from_pdf(file_bytes)
        elif ext in ['docx', 'doc']:
            return TextExtractor.extract_from_docx(file_bytes)
        elif ext in ['txt', 'md']:
            return TextExtractor.extract_from_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
