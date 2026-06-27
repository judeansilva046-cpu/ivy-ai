"""
Standalone document ingestion script
Run this to ingest documents from the documents/ directory
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.loader import DocumentLoader
from app.rag.chunker import TextChunker
from app.rag.indexer import get_document_indexer
from app.utils.logger import setup_logger
from config.settings import get_settings

logger = setup_logger(__name__)
settings = get_settings()


def ingest_all_documents():
    """Ingest all documents from documents directory"""
    try:
        logger.info("Starting document ingestion...")

        # Load documents
        docs_path = Path(settings.DOCUMENTS_PATH).resolve()
        logger.info(f"Loading documents from: {docs_path}")

        documents = DocumentLoader.load_from_directory(str(docs_path))

        if not documents:
            logger.warning(f"No documents found in {docs_path}")
            return False

        logger.info(f"✓ Loaded {len(documents)} documents")

        # Chunk documents
        chunker = TextChunker()
        chunked_documents = chunker.chunk_documents(documents)
        logger.info(f"✓ Created {len(chunked_documents)} chunks")

        # Index documents
        indexer = get_document_indexer()
        result = indexer.reindex_all(chunked_documents)

        if result["success"]:
            logger.info(f"✓ Indexed {result['count']} chunks successfully")
            logger.info("Document ingestion completed successfully!")
            return True
        else:
            logger.error("Failed to index documents")
            return False

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest documents into Jarvis AI")
    parser.add_argument(
        "--path",
        type=str,
        help="Path to documents directory",
        default=None
    )

    args = parser.parse_args()

    if args.path:
        # Custom path
        try:
            documents = DocumentLoader.load_from_directory(args.path)
            if not documents:
                logger.warning(f"No documents found in {args.path}")
                return

            chunker = TextChunker()
            chunked_documents = chunker.chunk_documents(documents)

            indexer = get_document_indexer()
            result = indexer.reindex_all(chunked_documents)

            if result["success"]:
                logger.info(f"✓ Indexed {result['count']} chunks from {args.path}")
            else:
                logger.error("Failed to index documents")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
    else:
        # Default path
        success = ingest_all_documents()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
