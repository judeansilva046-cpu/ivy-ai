"""
Custom exceptions for Jarvis AI
"""


class JarvisAIException(Exception):
    """Base exception for Jarvis AI"""
    pass


class DatabaseException(JarvisAIException):
    """Database connection/operation error"""
    pass


class QdrantException(JarvisAIException):
    """Qdrant vector store error"""
    pass


class RedisException(JarvisAIException):
    """Redis cache error"""
    pass


class OpenAIException(JarvisAIException):
    """OpenAI API error"""
    pass


class DocumentException(JarvisAIException):
    """Document processing error"""
    pass


class EmbeddingException(JarvisAIException):
    """Embedding generation error"""
    pass


class RAGException(JarvisAIException):
    """RAG pipeline error"""
    pass


class ChatException(JarvisAIException):
    """Chat service error"""
    pass


class ConfigurationException(JarvisAIException):
    """Configuration error"""
    pass


class ValidationException(JarvisAIException):
    """Validation error"""
    pass


# HTTP Error responses
class HTTPErrorResponse:
    """Standard HTTP error response"""

    @staticmethod
    def error(code: int, message: str, detail: str = None) -> dict:
        return {
            "error": {
                "code": code,
                "message": message,
                "detail": detail
            }
        }

    @staticmethod
    def bad_request(message: str, detail: str = None) -> dict:
        return HTTPErrorResponse.error(400, message, detail)

    @staticmethod
    def not_found(message: str, detail: str = None) -> dict:
        return HTTPErrorResponse.error(404, message, detail)

    @staticmethod
    def internal_error(message: str, detail: str = None) -> dict:
        return HTTPErrorResponse.error(500, message, detail)

    @staticmethod
    def service_unavailable(message: str, detail: str = None) -> dict:
        return HTTPErrorResponse.error(503, message, detail)
