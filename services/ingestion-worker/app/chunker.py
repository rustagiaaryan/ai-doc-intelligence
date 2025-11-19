# FILE: services/ingestion-worker/app/chunker.py

from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from app.config import settings


class TextChunker:
    """Chunk text into smaller segments for embedding."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize text chunker.

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        chunks = self.splitter.split_text(text)

        # Limit number of chunks per document
        if len(chunks) > settings.MAX_CHUNKS_PER_DOCUMENT:
            chunks = chunks[:settings.MAX_CHUNKS_PER_DOCUMENT]

        return chunks
