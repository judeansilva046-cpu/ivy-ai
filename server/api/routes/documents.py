"""
Document ingestion routes
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Optional
from pathlib import Path
from app.rag.loader import DocumentLoader
from app.rag.chunker import TextChunker
from app.rag.indexer import get_document_indexer
from app.utils.logger import setup_logger
from app.utils.errors import DocumentException, RAGException
from config.settings import get_settings

logger = setup_logger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])
settings = get_settings()


@router.post("/ingest")
async def ingest_documents(directory: Optional[str] = None):
    """Ingest documents from directory"""
    try:
        if not directory:
            directory = settings.DOCUMENTS_PATH

        logger.info(f"Starting document ingestion from: {directory}")

        # Load documents
        documents = DocumentLoader.load_from_directory(directory)

        if not documents:
            raise DocumentException(f"No documents found in {directory}")

        logger.info(f"Loaded {len(documents)} documents")

        # Chunk documents
        chunker = TextChunker()
        chunked_documents = chunker.chunk_documents(documents)

        logger.info(f"Created {len(chunked_documents)} chunks")

        # Index documents
        indexer = get_document_indexer()
        result = indexer.index_documents(chunked_documents)

        if not result["success"]:
            raise RAGException("Failed to index documents")

        return {
            "success": True,
            "message": f"Ingested {len(documents)} documents",
            "documents_loaded": len(documents),
            "chunks_created": len(chunked_documents),
            "chunks_indexed": result["count"],
            "indexed_ids": result["ids"]
        }

    except (DocumentException, RAGException) as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest a single document"""
    try:
        if not file.filename.endswith(".pdf"):
            raise DocumentException("Only PDF files are supported")

        # Save uploaded file
        uploads_path = Path(settings.UPLOADS_PATH)
        uploads_path.mkdir(exist_ok=True)

        file_path = uploads_path / file.filename

        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"Uploaded file: {file.filename}")

        # Load and process
        document = DocumentLoader.load_pdf(str(file_path))

        # Chunk
        chunker = TextChunker()
        chunked_documents = chunker.chunk_document(document)

        # Index
        indexer = get_document_indexer()
        result = indexer.index_documents(chunked_documents)

        return {
            "success": True,
            "filename": file.filename,
            "chunks_created": len(chunked_documents),
            "chunks_indexed": result["count"]
        }

    except DocumentException as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status")
async def documents_status():
    """Get document index status"""
    try:
        from app.services.vectorstore import get_vectorstore_service

        vectorstore = get_vectorstore_service()
        info = vectorstore.get_info()

        return {
            "status": "ok",
            "vector_store": info
        }

    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
