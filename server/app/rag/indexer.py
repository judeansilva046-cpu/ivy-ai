"""
Index documents into vector store
"""
from typing import List, Dict, Any
from app.database.qdrant import get_qdrant_store
from app.services.embeddings import get_embedding_service
from app.utils.logger import setup_logger
from app.utils.errors import RAGException

logger = setup_logger(__name__)


class DocumentIndexer:
    """Index documents into vector store"""

    def __init__(self):
        """Initialize indexer"""
        self.vector_store = get_qdrant_store()
        self.embedding_service = get_embedding_service()

    def index_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Index documents into vector store"""
        try:
            if not documents:
                logger.warning("No documents provided to index")
                return {"success": False, "count": 0}

            vectors = []
            metadata_list = []
            point_ids = []

            # Generate embeddings and prepare for indexing
            for idx, doc in enumerate(documents):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})

                if not content:
                    logger.warning(f"Skipping document with empty content")
                    continue

                # Generate embedding
                embedding = self.embedding_service.get_embedding(content)

                # Prepare metadata
                metadata["chunk_content"] = content

                vectors.append(embedding)
                metadata_list.append(metadata)
                point_ids.append(idx)

            if not vectors:
                logger.warning("No vectors to index")
                return {"success": False, "count": 0}

            # Index vectors
            indexed_ids = self.vector_store.add_vectors(
                vectors=vectors,
                metadata=metadata_list,
                ids=point_ids
            )

            logger.info(f"Indexed {len(indexed_ids)} documents")

            return {
                "success": True,
                "count": len(indexed_ids),
                "ids": indexed_ids
            }

        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            raise RAGException(f"Document indexing failed: {str(e)}")

    def index_single_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Index a single document"""
        try:
            return self.index_documents([document])
        except Exception as e:
            logger.error(f"Error indexing single document: {str(e)}")
            raise RAGException(f"Single document indexing failed: {str(e)}")

    def reindex_all(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Clear and reindex all documents"""
        try:
            # Clear existing collection
            try:
                self.vector_store.delete_collection()
                logger.info("Deleted existing collection")
            except:
                pass

            # Create new collection
            self.vector_store.create_collection()

            # Index documents
            return self.index_documents(documents)

        except Exception as e:
            logger.error(f"Error reindexing all documents: {str(e)}")
            raise RAGException(f"Reindexing failed: {str(e)}")


# Global instance
_document_indexer = None


def get_document_indexer() -> DocumentIndexer:
    """Get or create document indexer instance"""
    global _document_indexer
    if _document_indexer is None:
        _document_indexer = DocumentIndexer()
    return _document_indexer
