"""
RAG Package initialization.
"""
from rag.embeddings import embedding_manager, EmbeddingManager
from rag.faiss_manager import faiss_manager, FAISSManager
from rag.retriever import knowledge_retriever, KnowledgeRetriever
from rag.document_loader import create_starter_faiss_index

__all__ = [
    "embedding_manager",
    "EmbeddingManager",
    "faiss_manager",
    "FAISSManager",
    "knowledge_retriever",
    "KnowledgeRetriever",
    "create_starter_faiss_index",
]
