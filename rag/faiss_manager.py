"""
FAISS Index Manager.
Handles loading, status checking, and querying of the pre-built FAISS index.
Reads and integrates:
- data/faiss_index/index.faiss
- data/faiss_index/config.json
- data/faiss_index/metadata.json
- data/faiss_index/chunks.json

Connects FAISS vector IDs -> chunks.json (text content) -> metadata.json (source & page information).
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import faiss
from utils.constants import (
    FAISS_DIR,
    FAISS_INDEX_FILE,
    FAISS_CONFIG_FILE,
    FAISS_METADATA_FILE,
    FAISS_CHUNKS_FILE,
)

logger = logging.getLogger(__name__)


class FAISSManager:
    """
    Manages loading, status checking, and semantic querying of the pre-built FAISS index.
    Seamlessly integrates:
    - index.faiss: Vector representations
    - config.json: Index configuration and embedding model specifications
    - metadata.json: Document source, page, and provenance attribution
    - chunks.json: Raw text snippets for each vector chunk
    """

    def __init__(
        self,
        index_path: str = FAISS_INDEX_FILE,
        config_path: str = FAISS_CONFIG_FILE,
        metadata_path: str = FAISS_METADATA_FILE,
        chunks_path: Optional[str] = None,
    ):
        self.index_path = index_path
        self.config_path = config_path
        self.metadata_path = metadata_path
        self.chunks_path = chunks_path or FAISS_CHUNKS_FILE

        self.index: Optional[faiss.Index] = None
        self.config: Dict[str, Any] = {}
        self.records: List[Dict[str, Any]] = []
        self.records_by_id: Dict[Any, Dict[str, Any]] = {}
        self.metadata: List[Dict[str, Any]] = []  # Alias to self.records for compatibility
        self.is_loaded: bool = False
        self.has_chunks: bool = False
        self.load_error: Optional[str] = None

        # Configuration defaults (overridden by config.json)
        self.dimension: int = 384
        self.embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
        self.normalize_embeddings: bool = True
        self.index_type: str = "IndexFlatIP"
        self.chunk_size: int = 1000
        self.chunk_overlap: int = 200
        self.num_chunks: int = 0
        self.num_documents: int = 0

        # Attempt to load on startup
        self.reload()

    def _resolve_chunks_file(self) -> Optional[str]:
        """Resolves chunks.json or common alternative spellings like chuncks.json."""
        candidates = [
            self.chunks_path,
            os.path.join(FAISS_DIR, "chunks.json"),
            os.path.join(FAISS_DIR, "chuncks.json"),
        ]
        for p in candidates:
            if p and os.path.exists(p):
                return p
        return None

    def reload(self) -> bool:
        """
        Loads or reloads the FAISS index, configuration, metadata, and chunk files.
        Connects FAISS vector IDs -> chunks.json -> metadata.json.
        Returns True if files exist and load successfully; otherwise False.
        """
        self.is_loaded = False
        self.load_error = None
        self.has_chunks = False
        self.records = []
        self.records_by_id = {}
        self.metadata = []

        if not os.path.exists(self.index_path):
            self.load_error = f"FAISS index file not found at '{self.index_path}'."
            logger.info(self.load_error)
            return False

        if not os.path.exists(self.config_path):
            self.load_error = f"FAISS configuration file not found at '{self.config_path}'."
            logger.info(self.load_error)
            return False

        if not os.path.exists(self.metadata_path):
            self.load_error = f"FAISS metadata file not found at '{self.metadata_path}'."
            logger.info(self.load_error)
            return False

        try:
            # 1. Load config.json
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

            self.embedding_model = str(
                self.config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
            )
            self.dimension = int(
                self.config.get("embedding_dim", self.config.get("dimension", 384))
            )
            self.normalize_embeddings = bool(
                self.config.get("normalize_embeddings", True)
            )
            self.index_type = str(self.config.get("index_type", "IndexFlatIP"))
            self.chunk_size = int(self.config.get("chunk_size", 1000))
            self.chunk_overlap = int(self.config.get("chunk_overlap", 200))
            self.num_chunks = int(self.config.get("num_chunks", 0))
            self.num_documents = int(self.config.get("num_documents", 0))

            # 2. Load FAISS index
            self.index = faiss.read_index(self.index_path)

            # 3. Load metadata.json
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                raw_meta = json.load(f)

            meta_by_id = self._index_metadata_by_id(raw_meta)

            # 4. Load chunks.json
            chunks_file = self._resolve_chunks_file()
            chunks_by_id = {}
            if chunks_file:
                try:
                    with open(chunks_file, "r", encoding="utf-8") as f:
                        raw_chunks = json.load(f)
                    chunks_by_id = self._index_chunks_by_id(raw_chunks)
                    self.has_chunks = len(chunks_by_id) > 0
                    logger.info(
                        f"FAISSManager: Successfully loaded {len(chunks_by_id)} chunks from '{chunks_file}'."
                    )
                except Exception as ce:
                    logger.warning(f"FAISSManager: Could not load chunks from '{chunks_file}': {ce}")

            # 5. Connect FAISS vector IDs -> chunks.json -> metadata.json
            total_vectors = self.index.ntotal if self.index else 0
            self.records = []
            self.records_by_id = {}

            for idx in range(total_vectors):
                # Retrieve metadata record for vector ID
                meta_item = meta_by_id.get(idx) or meta_by_id.get(str(idx)) or {}
                source = meta_item.get("source", "Knowledge Dossier")
                page = meta_item.get("page")

                # Retrieve chunk text for vector ID
                text_content = (
                    chunks_by_id.get(idx)
                    or chunks_by_id.get(str(idx))
                    or meta_item.get("text")
                    or meta_item.get("content")
                    or ""
                )

                # Generate clean human-readable title from source name
                clean_title = (
                    source.replace(".pdf", "").replace("_", " ").strip()
                    if source
                    else f"Document #{idx}"
                )

                record = {
                    "id": idx,
                    "text": text_content,
                    "source": source,
                    "page": page,
                    "title": clean_title,
                }
                # Preserve any additional metadata keys from metadata.json
                for k, v in meta_item.items():
                    if k not in record:
                        record[k] = v

                self.records.append(record)
                self.records_by_id[idx] = record
                self.records_by_id[str(idx)] = record

            # Keep self.metadata aliased to self.records for backward compatibility
            self.metadata = self.records
            self.is_loaded = True

            logger.info(
                f"FAISSManager: Successfully loaded index with {total_vectors} vectors "
                f"(dim={self.dimension}, model={self.embedding_model}, has_chunks={self.has_chunks}) "
                f"and {len(self.records)} unified records."
            )
            return True

        except Exception as e:
            self.load_error = f"Error reading FAISS files: {str(e)}"
            logger.error(self.load_error, exc_info=True)
            self.is_loaded = False
            return False

    def _index_metadata_by_id(self, raw_meta: Any) -> Dict[Any, Dict[str, Any]]:
        """Indexes raw metadata into a dictionary keyed by both int and string IDs and positional index."""
        result = {}
        if isinstance(raw_meta, list):
            for i, item in enumerate(raw_meta):
                if isinstance(item, dict):
                    mid = item.get("id", i)
                    result[mid] = item
                    result[str(mid)] = item
                    result[i] = item
                else:
                    d = {"source": "Knowledge Dossier", "text": str(item), "id": i}
                    result[i] = d
                    result[str(i)] = d
        elif isinstance(raw_meta, dict):
            # Check for wrapped collections
            if "documents" in raw_meta and isinstance(raw_meta["documents"], list):
                return self._index_metadata_by_id(raw_meta["documents"])
            if "data" in raw_meta and isinstance(raw_meta["data"], list):
                return self._index_metadata_by_id(raw_meta["data"])

            for k, v in raw_meta.items():
                if isinstance(v, dict):
                    result[k] = v
                    if str(k).isdigit():
                        result[int(k)] = v
                else:
                    d = {"text": str(v), "source": "Knowledge Dossier"}
                    result[k] = d
                    if str(k).isdigit():
                        result[int(k)] = d
        return result

    def _index_chunks_by_id(self, raw_chunks: Any) -> Dict[Any, str]:
        """Indexes raw chunk text into a dictionary keyed by both int and string IDs and positional index."""
        result = {}
        if isinstance(raw_chunks, list):
            for i, item in enumerate(raw_chunks):
                if isinstance(item, dict):
                    cid = item.get("id", i)
                    txt = item.get("text") or item.get("content") or item.get("chunk") or ""
                    result[cid] = txt
                    result[str(cid)] = txt
                    result[i] = txt
                else:
                    txt = str(item)
                    result[i] = txt
                    result[str(i)] = txt
        elif isinstance(raw_chunks, dict):
            for k, v in raw_chunks.items():
                txt = v.get("text", "") if isinstance(v, dict) else str(v)
                result[k] = txt
                if str(k).isdigit():
                    result[int(k)] = txt
        return result

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs semantic similarity search against the FAISS index.
        Returns top_k matching records containing text chunks, source document,
        page information, and similarity scores.
        """
        if not self.is_loaded or self.index is None:
            return []

        try:
            # Ensure query vector is 2D float32
            if len(query_vector.shape) == 1:
                q = np.expand_dims(query_vector, axis=0).astype(np.float32)
            else:
                q = query_vector.astype(np.float32)

            # Normalize query vector if index utilizes cosine / inner product metric
            if self.normalize_embeddings:
                norm = np.linalg.norm(q)
                if norm > 1e-9:
                    q = q / norm

            k = min(top_k, self.index.ntotal)
            if k <= 0:
                return []

            distances, indices = self.index.search(q, k)
            results = []

            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self.records):
                    item = dict(self.records[idx])
                    item["_distance"] = float(dist)
                    item["score"] = float(dist)
                    item["_index"] = int(idx)
                    results.append(item)

            return results
        except Exception as e:
            logger.error(f"Error during FAISS vector search: {e}", exc_info=True)
            return []

    def get_status(self) -> Dict[str, Any]:
        """Returns the current FAISS health, configuration, and availability status."""
        return {
            "is_loaded": self.is_loaded,
            "index_path": self.index_path,
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "metadata_count": len(self.records),
            "has_chunks": self.has_chunks,
            "embedding_model": self.embedding_model,
            "index_type": self.index_type,
            "num_documents": self.num_documents,
            "load_error": self.load_error,
        }


# Global FAISS Singleton
faiss_manager = FAISSManager()
