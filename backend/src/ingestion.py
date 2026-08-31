import os
import glob
import logging
from typing import List

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

try:
    from langchain_core.embeddings import Embeddings
except ImportError:
    from langchain.embeddings.base import Embeddings

from langchain_community.vectorstores import Chroma
import chromadb.utils.embedding_functions as ef

try:
    from backend.src.config import (
        DATA_DIR,
        VECTOR_DB_DIR,
        EMBEDDING_PROVIDER,
        GOOGLE_API_KEY,
        GEMINI_EMBEDDING_MODEL,
        OPENAI_API_KEY,
        OPENAI_EMBEDDING_MODEL,
        CHUNK_SIZE,
        CHUNK_OVERLAP,
    )
except ImportError:
    from src.config import (
        DATA_DIR,
        VECTOR_DB_DIR,
        EMBEDDING_PROVIDER,
        GOOGLE_API_KEY,
        GEMINI_EMBEDDING_MODEL,
        OPENAI_API_KEY,
        OPENAI_EMBEDDING_MODEL,
        CHUNK_SIZE,
        CHUNK_OVERLAP,
    )


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class LocalMiniLMEmbeddings(Embeddings):
    """Offline, multilingual-capable local embeddings wrapper using Chroma Default ONNX model."""

    def __init__(self):
        self.ef = ef.DefaultEmbeddingFunction()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.ef(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.ef([text])[0]


def get_embedding_function() -> Embeddings:
    """Instantiate the configured embedding function with cross-lingual multilingual support."""
    if (EMBEDDING_PROVIDER == "gemini" or GOOGLE_API_KEY) and GOOGLE_API_KEY:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            emb_model = GEMINI_EMBEDDING_MODEL if GEMINI_EMBEDDING_MODEL else "models/text-embedding-004"
            logger.info(f"Using Google Gemini Multilingual Embeddings ({emb_model})")
            return GoogleGenerativeAIEmbeddings(
                model=emb_model,
                google_api_key=GOOGLE_API_KEY,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini embeddings ({e}), falling back to local embeddings.")
            return LocalMiniLMEmbeddings()

    elif EMBEDDING_PROVIDER == "openai" and OPENAI_API_KEY:
        try:
            from langchain_openai import OpenAIEmbeddings
            logger.info(f"Using OpenAI Embeddings ({OPENAI_EMBEDDING_MODEL})")
            return OpenAIEmbeddings(
                openai_api_key=OPENAI_API_KEY,
                model=OPENAI_EMBEDDING_MODEL,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI embeddings ({e}), falling back to local.")
            return LocalMiniLMEmbeddings()

    else:
        logger.info("Using local multilingual embeddings.")
        return LocalMiniLMEmbeddings()


def load_documents(data_dir: str = str(DATA_DIR)) -> List[Document]:
    """Load markdown and text business documents from the specified data directory."""
    documents: List[Document] = []
    supported_patterns = [os.path.join(data_dir, "*.md"), os.path.join(data_dir, "*.txt")]

    file_paths = []
    for pattern in supported_patterns:
        file_paths.extend(glob.glob(pattern))

    if not file_paths:
        logger.warning(f"No documents found in directory: {data_dir}")
        return documents

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                filename = os.path.basename(file_path)
                doc = Document(
                    page_content=content,
                    metadata={"source": filename, "file_path": file_path},
                )
                documents.append(doc)
                logger.info(f"Loaded business document: {filename} ({len(content)} characters)")
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")

    return documents


def split_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Document]:
    """Split documents into semantic overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks with overlap={chunk_overlap}.")
    return chunks


def ingest_data() -> Chroma:
    """Ingest documents, compute embeddings, and persist them into ChromaDB."""
    logger.info(f"Starting document ingestion from {DATA_DIR}...")
    docs = load_documents(str(DATA_DIR))
    if not docs:
        raise ValueError(f"No documents found in {DATA_DIR} to ingest.")

    chunks = split_documents(docs)
    embeddings = get_embedding_function()

    logger.info(f"Persisting vector database to {VECTOR_DB_DIR}...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
    )
    logger.info("Ingestion completed successfully!")
    return vector_store


if __name__ == "__main__":
    ingest_data()
