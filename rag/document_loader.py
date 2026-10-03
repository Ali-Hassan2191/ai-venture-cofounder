"""
Document loader and index builder utility.
Enables loading documents from text or JSON and building a starter FAISS index if requested.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from utils.constants import (
    FAISS_DIR,
    FAISS_INDEX_FILE,
    FAISS_CONFIG_FILE,
    FAISS_METADATA_FILE,
)
from rag.embeddings import embedding_manager

logger = logging.getLogger(__name__)


def create_starter_faiss_index(
    output_dir: str = FAISS_DIR,
    dimension: int = 384,
) -> bool:
    """
    Creates a starter FAISS index with foundational startup benchmarks,
    unit economics models, SaaS benchmarks, and venture evaluation data.
    Ensures the RAG system works out of the box until the founder provides custom files.
    """
    os.makedirs(output_dir, exist_ok=True)
    index_file = os.path.join(output_dir, "index.faiss")
    config_file = os.path.join(output_dir, "config.json")
    metadata_file = os.path.join(output_dir, "metadata.json")

    starter_documents = [
        {
            "id": 1,
            "title": "Early Stage SaaS & Market Benchmarks",
            "source": "Venture Benchmark Study",
            "category": "Market",
            "text": (
                "B2B SaaS conversion rates typically average 1.5% to 3.5% from visitor to signup, "
                "and 15% to 25% from trial to paid. CAC to LTV ratio should ideally exceed 1:3 for "
                "sustainable scalability, with a CAC payback period under 12 months."
            ),
        },
        {
            "id": 2,
            "title": "Consumer App Unit Economics & Retention",
            "source": "Growth Strategy Journal",
            "category": "Marketing",
            "text": (
                "Consumer mobile applications experience standard Day 1 retention around 25-35%, "
                "Day 7 retention around 10-15%, and Day 30 retention around 5-8%. Campus and hyper-local "
                "networks succeed when achieving over 40% monthly cohort retention through viral loops."
            ),
        },
        {
            "id": 3,
            "title": "Food Delivery & Hyper-local Unit Economics",
            "source": "Logistics & Marketplace Economics",
            "category": "Finance",
            "text": (
                "Hyper-local delivery platforms operate with tight gross margins of 15% to 28%. Key levers "
                "include order batching (delivering multiple orders per courier run), dynamic delivery fees, "
                "and restaurant commission fees ranging between 12% and 25%."
            ),
        },
        {
            "id": 4,
            "title": "AI Application Architecture Best Practices",
            "source": "Modern Engineering Standards",
            "category": "Technology",
            "text": (
                "Production AI applications must decouple LLM orchestration from core business databases. "
                "RAG pipelines should index curated domain summaries rather than multi-megabyte raw dumps. "
                "Vector retrieval latency should be under 50ms with local FAISS index caching."
            ),
        },
        {
            "id": 5,
            "title": "Startup Failure Modes and Risk Mitigation",
            "source": "Venture Capital Risk Matrix",
            "category": "Risk",
            "text": (
                "The #1 cause of early startup failure is lack of market demand (42%), followed by running out "
                "of cash (29%), and weak founding team alignment (23%). Founders must pre-validate willingness "
                "to pay prior to heavy technical development."
            ),
        },
        {
            "id": 6,
            "title": "Dynamic Go-To-Market & Early Traction",
            "source": "GTM Playbook",
            "category": "Marketing",
            "text": (
                "Initial customer acquisition should prioritize high-touch, unscalable channels first: "
                "direct campus ambassadorship, targeted micro-influencer seeding, and community-driven launch "
                "campaigns before allocating capital to paid ads."
            ),
        },
    ]

    try:
        # 1. Build embeddings
        vectors = []
        for doc in starter_documents:
            vec = embedding_manager.embed_query(doc["text"], target_dimension=dimension)
            vectors.append(vec)

        vectors_np = np.vstack(vectors).astype(np.float32)

        # 2. Build FAISS index (IndexFlatIP for cosine / inner product search)
        index = faiss.IndexFlatIP(dimension)
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors_np)
        index.add(vectors_np)

        # 3. Write index
        faiss.write_index(index, index_file)

        # 4. Write config
        config_data = {
            "dimension": dimension,
            "metric": "cosine",
            "index_type": "IndexFlatIP",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "total_documents": len(starter_documents),
            "description": "Foundational startup benchmarks, unit economics, and risk mitigation knowledge base.",
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        # 5. Write metadata
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(starter_documents, f, indent=2)

        logger.info(f"Starter FAISS index created successfully at '{output_dir}'.")
        return True

    except Exception as e:
        logger.error(f"Failed to create starter FAISS index: {e}", exc_info=True)
        return False
