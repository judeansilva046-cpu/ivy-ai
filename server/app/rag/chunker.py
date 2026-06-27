"""
Text chunking for documents
"""
from typing import List, Dict, Any
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import RAGException

logger = setup_logger(__name__)
settings = get_settings()


class TextChunker:
    """Split documents into chunks with overlap"""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """Initialize chunker with size and overlap parameters"""
        self.chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.RAG_CHUNK_OVERLAP

        if self.chunk_overlap >= self.chunk_size:
            raise RAGException("Chunk overlap must be smaller than chunk size")

        logger.info(
            f"TextChunker initialized with size={self.chunk_size}, overlap={self.chunk_overlap}"
        )

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        try:
            if not text or len(text.strip()) == 0:
                logger.warning("Empty text provided to chunker")
                return []

            chunks = []
            words = text.split()
            current_chunk = []
            current_length = 0

            for word in words:
                word_length = len(word) + 1  # +1 for space

                if current_length + word_length > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunk_text = " ".join(current_chunk)
                    chunks.append(chunk_text)

                    # Create overlap - keep last words
                    overlap_words = int(self.chunk_overlap / 5)  # Average word length ~5 chars
                    current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
                    current_length = sum(len(w) + 1 for w in current_chunk)

                current_chunk.append(word)
                current_length += word_length

            # Add final chunk
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            raise RAGException(f"Text splitting failed: {str(e)}")

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk a document into multiple chunks with metadata"""
        try:
            content = document.get("content", "")
            metadata = document.get("metadata", {})

            chunks = self.split_text(content)
            chunked_documents = []

            for chunk_idx, chunk_text in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = chunk_idx
                chunk_metadata["chunk_total"] = len(chunks)

                chunked_documents.append({
                    "content": chunk_text,
                    "metadata": chunk_metadata
                })

            logger.info(
                f"Chunked document '{metadata.get('filename', 'unknown')}' into {len(chunked_documents)} chunks"
            )
            return chunked_documents

        except Exception as e:
            logger.error(f"Error chunking document: {str(e)}")
            raise RAGException(f"Document chunking failed: {str(e)}")

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk multiple documents"""
        try:
            all_chunks = []

            for document in documents:
                chunks = self.chunk_document(document)
                all_chunks.extend(chunks)

            logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} total chunks")
            return all_chunks

        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            raise RAGException(f"Documents chunking failed: {str(e)}")
