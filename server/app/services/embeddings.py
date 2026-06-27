"""
Embedding generation using OpenAI
"""
from typing import List
from openai import OpenAI
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import EmbeddingException

logger = setup_logger(__name__)
settings = get_settings()


class EmbeddingService:
    """Generate embeddings using OpenAI"""

    def __init__(self):
        """Initialize embedding service"""
        if not settings.OPENAI_API_KEY:
            raise EmbeddingException("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL_EMBEDDINGS
        logger.info(f"EmbeddingService initialized with model: {self.model}")

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            if not text or len(text.strip()) == 0:
                raise EmbeddingException("Empty text provided for embedding")

            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return embedding

        except EmbeddingException:
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise EmbeddingException(f"Embedding generation failed: {str(e)}")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        try:
            if not texts:
                raise EmbeddingException("Empty texts list provided for embeddings")

            # Filter out empty texts
            valid_texts = [t for t in texts if t and len(t.strip()) > 0]

            if not valid_texts:
                raise EmbeddingException("No valid texts in the list")

            response = self.client.embeddings.create(
                input=valid_texts,
                model=self.model
            )

            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except EmbeddingException:
            raise
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise EmbeddingException(f"Embeddings generation failed: {str(e)}")


# Global instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
