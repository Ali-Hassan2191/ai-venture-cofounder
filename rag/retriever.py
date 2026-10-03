"""
Semantic Retrieval Engine for RAG.
Retrieves relevant startup, market, competitor, and financial benchmarks from FAISS index.
Supplies compact, high-signal context to CrewAI agents without wasting output/input tokens.
"""
import logging
from typing import List, Dict, Any
from rag.faiss_manager import faiss_manager, FAISSManager
from rag.embeddings import embedding_manager, EmbeddingManager

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """
    Retrieves semantic context for agent prompts.
    """

    def __init__(
        self,
        manager: FAISSManager = faiss_manager,
        embedder: EmbeddingManager = embedding_manager,
    ):
        self.manager = manager
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Performs vector search and returns matching metadata documents."""
        if not self.manager.is_loaded:
            return []

        try:
            target_dim = self.manager.dimension
            q_vector = self.embedder.embed_query(query, target_dimension=target_dim)
            return self.manager.search(q_vector, top_k=top_k)
        except Exception as e:
            logger.warning(f"Error during context retrieval: {e}")
            return []

    def get_formatted_context(self, query: str, top_k: int = 3, max_chars: int = 1200) -> str:
        """
        Retrieves top relevant records and formats them as concise, structured evidence.
        Respects token limits by capping total characters.
        """
        records = self.retrieve(query, top_k=top_k)
        if not records:
            return (
                "[Knowledge Base Context: No external documents found. "
                "Base analysis on domain industry standards and explicit user inputs.]"
            )

        snippets = []
        char_count = 0

        for i, item in enumerate(records, 1):
            source = item.get("source") or item.get("category") or "Knowledge Document"
            title = item.get("title") or item.get("topic") or f"Record {i}"
            text = item.get("text") or item.get("content") or str(item)

            # Clean and truncate individual snippet if needed
            clean_text = " ".join(text.split())
            if len(clean_text) > 400:
                clean_text = clean_text[:400] + "..."

            snippet = f"- [{source} | {title}]: {clean_text}"
            if char_count + len(snippet) > max_chars:
                break

            snippets.append(snippet)
            char_count += len(snippet)

        return "[Retrieved Knowledge Evidence]:\n" + "\n".join(snippets)


# Global singleton
knowledge_retriever = KnowledgeRetriever()
