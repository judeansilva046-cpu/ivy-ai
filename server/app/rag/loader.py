"""
Document loader for PDF files
"""
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
from app.utils.logger import setup_logger
from app.utils.errors import DocumentException

logger = setup_logger(__name__)


class DocumentLoader:
    """Load documents from various formats"""

    @staticmethod
    def load_pdf(file_path: str) -> Dict[str, Any]:
        """Load PDF file and extract text"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise DocumentException(f"File not found: {file_path}")

            if not file_path.suffix.lower() == ".pdf":
                raise DocumentException(f"Not a PDF file: {file_path}")

            reader = PdfReader(file_path)
            text = ""
            metadata = {
                "filename": file_path.name,
                "filepath": str(file_path),
                "pages": len(reader.pages),
                "source": "pdf"
            }

            # Extract text from all pages
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n[Page {page_num + 1}]\n{page_text}"

            # Extract document metadata
            if reader.metadata:
                if reader.metadata.get("/Title"):
                    metadata["title"] = reader.metadata.get("/Title")
                if reader.metadata.get("/Author"):
                    metadata["author"] = reader.metadata.get("/Author")
                if reader.metadata.get("/Subject"):
                    metadata["subject"] = reader.metadata.get("/Subject")

            logger.info(f"Loaded PDF: {file_path.name} ({len(reader.pages)} pages)")

            return {
                "content": text.strip(),
                "metadata": metadata
            }

        except DocumentException:
            raise
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise DocumentException(f"PDF loading failed: {str(e)}")

    @staticmethod
    def load_text(file_path: str) -> Dict[str, Any]:
        """Load text file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise DocumentException(f"File not found: {file_path}")

            content = file_path.read_text(encoding="utf-8")

            metadata = {
                "filename": file_path.name,
                "filepath": str(file_path),
                "source": "text"
            }

            logger.info(f"Loaded text file: {file_path.name}")

            return {
                "content": content,
                "metadata": metadata
            }

        except DocumentException:
            raise
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise DocumentException(f"Text file loading failed: {str(e)}")

    @staticmethod
    def load_from_directory(directory: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Load all documents from directory"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                raise DocumentException(f"Directory not found: {directory}")

            if file_types is None:
                file_types = [".pdf", ".txt"]

            documents = []
            file_types = [ft.lower() if ft.startswith(".") else f".{ft.lower()}" for ft in file_types]

            for file_path in dir_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in file_types:
                    try:
                        if file_path.suffix.lower() == ".pdf":
                            doc = DocumentLoader.load_pdf(str(file_path))
                        elif file_path.suffix.lower() == ".txt":
                            doc = DocumentLoader.load_text(str(file_path))
                        else:
                            continue

                        documents.append(doc)
                    except DocumentException as e:
                        logger.warning(f"Skipping file {file_path.name}: {str(e)}")
                        continue

            logger.info(f"Loaded {len(documents)} documents from {directory}")
            return documents

        except DocumentException:
            raise
        except Exception as e:
            logger.error(f"Error loading from directory {directory}: {str(e)}")
            raise DocumentException(f"Directory loading failed: {str(e)}")
