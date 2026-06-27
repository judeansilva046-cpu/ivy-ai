"""
PostgreSQL database connection and operations
"""
from typing import Optional
import psycopg2
from psycopg2 import pool
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import DatabaseException

logger = setup_logger(__name__)
settings = get_settings()


class PostgresDatabase:
    """PostgreSQL database wrapper"""

    def __init__(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,
                20,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB
            )
            logger.info(
                f"Connected to PostgreSQL at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise DatabaseException(f"PostgreSQL connection failed: {str(e)}")

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.connection_pool.getconn()
        except Exception as e:
            logger.error(f"Error getting connection: {str(e)}")
            raise DatabaseException(f"Connection retrieval failed: {str(e)}")

    def return_connection(self, conn):
        """Return connection to the pool"""
        try:
            self.connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection: {str(e)}")

    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute a SELECT query"""
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query, params or ())
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise DatabaseException(f"Query execution failed: {str(e)}")
        finally:
            if conn:
                self.return_connection(conn)

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query, params or ())
            conn.commit()
            rows_affected = cur.rowcount
            cur.close()
            return rows_affected
        except Exception as e:
            logger.error(f"Error executing update: {str(e)}")
            if conn:
                conn.rollback()
            raise DatabaseException(f"Update execution failed: {str(e)}")
        finally:
            if conn:
                self.return_connection(conn)

    def close_all(self):
        """Close all connections in pool"""
        try:
            self.connection_pool.closeall()
            logger.info("Closed all PostgreSQL connections")
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")


# Global instance
_postgres_db = None


def get_postgres_db() -> PostgresDatabase:
    """Get or create PostgreSQL database instance"""
    global _postgres_db
    if _postgres_db is None:
        _postgres_db = PostgresDatabase()
    return _postgres_db
