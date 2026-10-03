"""
Document loader and index inspection utility.
Guarantees that existing user files (index.faiss, config.json, metadata.json, chunks.json)
are NEVER overwritten, replaced, or modified.
Provides diagnostics for pre-built FAISS knowledge assets.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from utils.constants import (
    FAISS_DIR,
    FAISS_INDEX_FILE,
    FAISS_CONFIG_FILE,
    FAISS_METADATA_FILE,
    FAISS_CHUNKS_FILE,
)

logger = logging.getLogger(__name__)


def inspect_existing_faiss_index(output_dir: str = FAISS_DIR) -> Dict[str, Any]:
    """
    Inspects existing FAISS index files and returns structural metadata.
    Does NOT modify or overwrite any files.
    """
    index_file = os.path.join(output_dir, "index.faiss")
    config_file = os.path.join(output_dir, "config.json")
    metadata_file = os.path.join(output_dir, "metadata.json")
    chunks_file = os.path.join(output_dir, "chunks.json")

    status = {
        "dir": output_dir,
        "has_index": os.path.exists(index_file),
        "has_config": os.path.exists(config_file),
        "has_metadata": os.path.exists(metadata_file),
        "has_chunks": os.path.exists(chunks_file),
        "config": {},
        "metadata_count": 0,
        "chunks_count": 0,
    }

    if status["has_config"]:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                status["config"] = json.load(f)
        except Exception as e:
            logger.warning(f"Could not read config.json: {e}")

    if status["has_metadata"]:
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                status["metadata_count"] = len(meta) if isinstance(meta, (list, dict)) else 1
        except Exception as e:
            logger.warning(f"Could not read metadata.json: {e}")

    if status["has_chunks"]:
        try:
            with open(chunks_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)
                status["chunks_count"] = len(chunks) if isinstance(chunks, (list, dict)) else 1
        except Exception as e:
            logger.warning(f"Could not read chunks.json: {e}")

    return status


def create_starter_faiss_index(
    output_dir: str = FAISS_DIR,
    dimension: int = 384,
) -> bool:
    """
    Safety guard: checks if index already exists.
    If existing index files are present, this function immediately returns True
    and PRESERVES all existing files without making any changes.
    """
    index_file = os.path.join(output_dir, "index.faiss")
    if os.path.exists(index_file):
        logger.info(
            f"FAISS index already exists at '{index_file}'. "
            "Preserving existing user index files without modification."
        )
        return True

    logger.warning(
        f"No existing FAISS index found at '{index_file}'. "
        "Please provide pre-built index.faiss, config.json, metadata.json, and chunks.json in '{output_dir}'."
    )
    return False
