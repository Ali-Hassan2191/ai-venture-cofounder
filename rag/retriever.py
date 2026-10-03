"""
Semantic Retrieval Engine for RAG.
Retrieves relevant startup, market, competitor, technical, and financial benchmarks from FAISS index.
Preserves source document and page attribution for transparent evidence tracing.
Supplies compact, high-signal context to CrewAI agents without wasting prompt tokens.
"""
import logging
from typing import List, Dict, Any
from rag.faiss_manager import faiss_manager, FAISSManager
from rag.embeddings import embedding_manager, EmbeddingManager

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """
    Retrieves semantic context for agent prompts from the pre-built FAISS index,
    connecting vectors -> chunks.json -> metadata.json.
    """

    def __init__(
        self,
        manager: FAISSManager = faiss_manager,
        embedder: EmbeddingManager = embedding_manager,
    ):
        self.manager = manager
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs vector search and returns top_k matching records containing:
        - text: Chunk content from chunks.json
        - source: Document source filename from metadata.json
        - page: Document page number from metadata.json
        - score: Similarity score
        - id: Vector ID
        """
        if not self.manager.is_loaded:
            return []

        try:
            target_dim = self.manager.dimension
            model_name = self.manager.embedding_model
            normalize = self.manager.normalize_embeddings

            q_vector = self.embedder.embed_query(
                query,
                target_dimension=target_dim,
                model_name=model_name,
                normalize=normalize,
            )
            return self.manager.search(q_vector, top_k=top_k)
        except Exception as e:
            logger.warning(f"Error during context retrieval: {e}")
            return []

    def get_formatted_context(
        self, query: str, top_k: int = 3, max_chars: int = 1600
    ) -> str:
        """
        Retrieves top relevant records and formats them as structured evidence.
        Preserves source information and page numbers so agents can cite empirical benchmarks.
        """
        records = self.retrieve(query, top_k=top_k)
        if not records:
            return (
                "[Knowledge Base Context: No specific benchmark records matched the query. "
                "Base analysis on standard industry frameworks and user inputs.]"
            )

        snippets = []
        char_count = 0

        for i, item in enumerate(records, 1):
            source = item.get("source") or "Knowledge Document"
            page = item.get("page")
            page_info = f" (Page {page})" if page is not None else ""
            title = item.get("title")
            header = f"{source}{page_info}" if not title else f"{source} | {title}{page_info}"
            text = item.get("text") or item.get("content") or ""

            # Normalize whitespace and truncate individual chunk if exceptionally long
            clean_text = " ".join(str(text).split())
            if len(clean_text) > 500:
                clean_text = clean_text[:500] + "..."

            snippet = f"- [Source: {header}]:\n  \"{clean_text}\""
            if char_count + len(snippet) > max_chars:
                break

            snippets.append(snippet)
            char_count += len(snippet)

        return "[Retrieved Knowledge Evidence]:\n" + "\n\n".join(snippets)


# Global singleton
knowledge_retriever = KnowledgeRetriever()
