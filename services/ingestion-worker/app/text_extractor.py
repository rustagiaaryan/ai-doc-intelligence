# FILE: services/ingestion-worker/app/text_extractor.py

import fitz  # PyMuPDF
from docx import Document
import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from various document formats."""

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """
        Extract text from PDF file (simple mode without positioning).

        Args:
            file_bytes: PDF file as bytes

        Returns:
            Extracted text content
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []

            for page in doc:
                text = page.get_text()
                if text:
                    text_parts.append(text)

            doc.close()
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    @staticmethod
    def extract_from_pdf_with_positions(file_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF file with positioning data for highlighting.

        Args:
            file_bytes: PDF file as bytes

        Returns:
            Dictionary containing:
            - text: Full extracted text
            - pages: List of page data with text blocks and positions
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text_parts = []
            pages_data = []

            for page_num, page in enumerate(doc):
                # Extract text blocks with positions
                blocks = page.get_text("dict")["blocks"]
                page_text_parts = []
                text_blocks = []

                for block in blocks:
                    if block["type"] == 0:  # Text block
                        block_text = ""
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                block_text += span.get("text", "")
                            block_text += "\n"

                        block_text = block_text.strip()
                        if block_text:
                            page_text_parts.append(block_text)

                            # Store block position data
                            bbox = block["bbox"]  # [x0, y0, x1, y1]
                            text_blocks.append({
                                "text": block_text,
                                "bbox": {
                                    "x0": bbox[0],
                                    "y0": bbox[1],
                                    "x1": bbox[2],
                                    "y1": bbox[3]
                                },
                                "page": page_num
                            })

                page_text = "\n\n".join(page_text_parts)
                full_text_parts.append(page_text)

                pages_data.append({
                    "page_number": page_num,
                    "text": page_text,
                    "blocks": text_blocks,
                    "width": page.rect.width,
                    "height": page.rect.height
                })

            doc.close()

            return {
                "text": "\n\n".join(full_text_parts),
                "pages": pages_data,
                "total_pages": len(pages_data)
            }
        except Exception as e:
            logger.error(f"Error extracting text with positions from PDF: {e}")
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
