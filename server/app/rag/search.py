"""
Semantic search in vector store
"""
from typing import List, Dict, Any, Optional
from app.database.qdrant import get_qdrant_store
from app.services.embeddings import get_embedding_service
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import RAGException

logger = setup_logger(__name__)
settings = get_settings()


class SemanticSearch:
    """Semantic search using embeddings and vector store"""

    def __init__(self):
        """Initialize search service"""
        self.vector_store = get_qdrant_store()
        self.embedding_service = get_embedding_service()
        self.top_k = settings.RAG_TOP_K
        self.min_score = settings.RAG_MIN_SCORE

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if not query or len(query.strip()) == 0:
                logger.warning("Empty query provided to search")
                return []

            top_k = top_k or self.top_k
            min_score = min_score or self.min_score

            # Generate embedding for query
            query_embedding = self.embedding_service.get_embedding(query)

            # Search in vector store
            results = self.vector_store.search(
                vector=query_embedding,
                limit=top_k,
                score_threshold=min_score
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["id"],
                    "score": result["score"],
                    "content": result["payload"].get("chunk_content", ""),
                    "metadata": {
                        k: v for k, v in result["payload"].items()
                        if k != "chunk_content"
                    }
                })

            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise RAGException(f"Search failed: {str(e)}")

    def search_with_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> str:
        """Search and format results as context string for LLM"""
        try:
            results = self.search(query, top_k, min_score)

            if not results:
                return "Nenhum documento relevante encontrado."

            context_parts = []
            for idx, result in enumerate(results, 1):
                context_parts.append(
                    f"[Documento {idx}] (Confiança: {result['score']:.2f})\n"
                    f"{result['content']}\n"
                )

            return "\n---\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error formatting search context: {str(e)}")
            raise RAGException(f"Context formatting failed: {str(e)}")


# Global instance
_semantic_search = None


def get_semantic_search() -> SemanticSearch:
    """Get or create semantic search instance"""
    global _semantic_search
    if _semantic_search is None:
        _semantic_search = SemanticSearch()
    return _semantic_search
