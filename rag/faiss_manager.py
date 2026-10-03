"""
FAISS Index Manager.
Handles loading and management of:
- data/faiss_index/index.faiss
- data/faiss_index/config.json
- data/faiss_index/metadata.json
Gracefully handles missing files, diverse metadata schemas, and index status reporting.
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
)

logger = logging.getLogger(__name__)


class FAISSManager:
    """
    Manages loading, status checking, and querying of the pre-built FAISS index.
    """

    def __init__(
        self,
        index_path: str = FAISS_INDEX_FILE,
        config_path: str = FAISS_CONFIG_FILE,
        metadata_path: str = FAISS_METADATA_FILE,
    ):
        self.index_path = index_path
        self.config_path = config_path
        self.metadata_path = metadata_path

        self.index: Optional[faiss.Index] = None
        self.config: Dict[str, Any] = {}
        self.metadata: List[Dict[str, Any]] = []
        self.is_loaded: bool = False
        self.load_error: Optional[str] = None
        self.dimension: int = 384

        # Attempt to load on startup
        self.reload()

    def reload(self) -> bool:
        """
        Loads or reloads the FAISS index, configuration, and metadata files.
        Returns True if all files exist and load successfully; otherwise False.
        """
        self.is_loaded = False
        self.load_error = None

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
            # 1. Load config
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            self.dimension = int(self.config.get("dimension", 384))

            # 2. Load FAISS index
            self.index = faiss.read_index(self.index_path)

            # 3. Load metadata and normalize to List[Dict[str, Any]]
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                raw_meta = json.load(f)

            self.metadata = self._normalize_metadata(raw_meta)
            self.is_loaded = True
            logger.info(
                f"FAISSManager: Successfully loaded index with {self.index.ntotal} vectors "
                f"(dim={self.dimension}) and {len(self.metadata)} metadata records."
            )
            return True

        except Exception as e:
            self.load_error = f"Error reading FAISS files: {str(e)}"
            logger.error(self.load_error, exc_info=True)
            self.is_loaded = False
            return False

    def _normalize_metadata(self, raw_meta: Any) -> List[Dict[str, Any]]:
        """
        Normalizes different JSON formats into a standardized list of dicts:
        Supports:
        - List of dicts: [{"text": "...", "source": "..."}]
        - Dict with 'documents' or 'data' key
        - Dict mapped by string indices: {"0": {...}, "1": {...}}
        - List of plain strings: ["content 1", "content 2"]
        """
        if isinstance(raw_meta, list):
            normalized = []
            for item in raw_meta:
                if isinstance(item, dict):
                    normalized.append(item)
                else:
                    normalized.append({"text": str(item), "source": "general_knowledge"})
            return normalized

        if isinstance(raw_meta, dict):
            if "documents" in raw_meta and isinstance(raw_meta["documents"], list):
                return self._normalize_metadata(raw_meta["documents"])
            if "data" in raw_meta and isinstance(raw_meta["data"], list):
                return self._normalize_metadata(raw_meta["data"])

            # Map by numeric keys
            items = []
            # Sort keys numerically if possible
            sorted_keys = sorted(
                raw_meta.keys(),
                key=lambda k: int(k) if k.isdigit() else k,
            )
            for k in sorted_keys:
                v = raw_meta[k]
                if isinstance(v, dict):
                    items.append(v)
                else:
                    items.append({"text": str(v), "key": str(k)})
            return items

        return [{"text": str(raw_meta)}]

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs semantic similarity search against the FAISS index.
        Returns top_k matching metadata documents with distance scores.
        """
        if not self.is_loaded or self.index is None:
            return []

        try:
            # Ensure query vector is 2D float32
            if len(query_vector.shape) == 1:
                q = np.expand_dims(query_vector, axis=0).astype(np.float32)
            else:
                q = query_vector.astype(np.float32)

            k = min(top_k, self.index.ntotal)
            if k <= 0:
                return []

            distances, indices = self.index.search(q, k)
            results = []

            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self.metadata):
                    item = dict(self.metadata[idx])
                    item["_distance"] = float(dist)
                    item["_index"] = int(idx)
                    results.append(item)

            return results
        except Exception as e:
            logger.error(f"Error during FAISS vector search: {e}", exc_info=True)
            return []

    def get_status(self) -> Dict[str, Any]:
        """Returns the current FAISS health and availability status."""
        return {
            "is_loaded": self.is_loaded,
            "index_path": self.index_path,
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata),
            "load_error": self.load_error,
        }


# Global FAISS Singleton
faiss_manager = FAISSManager()
