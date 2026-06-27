"""
Qdrant vector store connection and operations
"""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import inspect
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import QdrantException

logger = setup_logger(__name__)
settings = get_settings()


class QdrantVectorStore:
    """Qdrant vector store wrapper"""

    def __init__(self):
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                prefer_grpc=False
            )
            self.collection_name = settings.QDRANT_COLLECTION
            self.vector_size = settings.QDRANT_VECTOR_SIZE
            logger.info(
                f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise QdrantException(f"Qdrant connection failed: {str(e)}")

    def collection_exists(self) -> bool:
        """Check if collection exists"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error(f"Error checking collection: {str(e)}")
            raise QdrantException(f"Collection check failed: {str(e)}")

    def create_collection(self) -> bool:
        """Create vector collection if it doesn't exist"""
        try:
            if self.collection_exists():
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True

            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise QdrantException(f"Collection creation failed: {str(e)}")

    def add_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[int]] = None
    ) -> List[int]:
        """Add vectors to collection"""
        try:
            if not self.collection_exists():
                self.create_collection()

            points = []
            for idx, (vector, meta) in enumerate(zip(vectors, metadata)):
                point_id = ids[idx] if ids else idx
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=meta
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Added {len(points)} vectors to collection")
            return [p.id for p in points]
        except Exception as e:
            logger.error(f"Error adding vectors: {str(e)}")
            raise QdrantException(f"Vector addition failed: {str(e)}")

    def search(
        self,
        vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        try:
            # Use query_points for semantic search (qdrant-client 1.7.0+)
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit,
                score_threshold=score_threshold
            )

            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results.points
            ]
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise QdrantException(f"Vector search failed: {str(e)}")

    def delete_point(self, point_id: int) -> bool:
        """Delete a point from collection"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_id
            )
            logger.info(f"Deleted point {point_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting point: {str(e)}")
            raise QdrantException(f"Point deletion failed: {str(e)}")

    def delete_collection(self) -> bool:
        """Delete entire collection"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise QdrantException(f"Collection deletion failed: {str(e)}")

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": getattr(info, 'vectors_count', info.points_count if hasattr(info, 'points_count') else 0),
                "segments_count": getattr(info, 'segments_count', 0)
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            raise QdrantException(f"Collection info retrieval failed: {str(e)}")


# Global instance
_qdrant_store = None


def get_qdrant_store() -> QdrantVectorStore:
    """Get or create Qdrant store instance"""
    global _qdrant_store
    if _qdrant_store is None:
        _qdrant_store = QdrantVectorStore()
    return _qdrant_store
