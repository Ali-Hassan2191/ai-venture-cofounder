# FAISS Vector Index Directory

This directory contains the vector search assets required by the **AI Venture Co-Founder** Advanced RAG pipeline.

---

## 1. Required Files

The RAG retriever expects exactly the following three files in this folder (`data/faiss_index/`):

1. **`index.faiss`**: The serialized binary FAISS index containing embedded knowledge vectors.
2. **`config.json`**: Index configuration, vector dimension, distance metric, and model reference.
3. **`metadata.json`**: Structured metadata matching each vector index (ID, title, category, text content, source).

---

## 2. Where to Place Your Custom Files

Place your pre-built FAISS files directly into:
```
ai_venture_cofounder/
└── data/
    └── faiss_index/
        ├── index.faiss
        ├── config.json
        └── metadata.json
```

When you place your custom files here, the application automatically detects, validates, and reloads them on startup.

---

## 3. Configuration Format (`config.json`)

The `config.json` file should define the vector dimensionality and metric:

```json
{
  "dimension": 384,
  "metric": "cosine",
  "index_type": "IndexFlatIP",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "total_documents": 250,
  "description": "Venture benchmarks, customer acquisition costs, and pricing research."
}
```

*Note: The application dynamically reads `"dimension"` from this file to ensure all incoming query embeddings match the exact vector space of your index.*

---

## 4. Metadata Format (`metadata.json`)

The `metadata.json` file associates vector row indices with text snippets and provenance. The application supports standard formats:

### Recommended: Array of Document Objects
```json
[
  {
    "id": 0,
    "title": "B2B SaaS Pricing Tiers",
    "category": "Finance",
    "source": "OpenView 2026 SaaS Benchmarks",
    "text": "Early stage B2B SaaS applications charging annually achieve 28% lower churn than monthly subscriptions."
  },
  {
    "id": 1,
    "title": "Campus Delivery Unit Economics",
    "category": "Logistics",
    "source": "Hyperlocal Commerce Report",
    "text": "High student density allows 3-4 order batches per delivery runner, reducing delivery cost by 45%."
  }
]
```

### Alternatively: Key-Indexed Dictionary
```json
{
  "0": { "title": "Market Size Data", "text": "..." },
  "1": { "title": "Customer Retention", "text": "..." }
}
```

---

## 5. How the Index is Loaded & Queried

1. `rag/faiss_manager.py` verifies the existence of all 3 files.
2. It parses `config.json` to determine vector dimension `D` (e.g. 384, 768, 1536).
3. `faiss.read_index()` loads the vector index into memory.
4. When an AI agent executes a research task, `rag/retriever.py` queries the index using cosine similarity.
5. The top matching context snippets are injected into the agent's prompt to ensure evidence-based, grounded analysis.

---

## 6. Embedding Compatibility Requirements

- Ensure your query embeddings use the same dimensionality (`dimension`) declared in `config.json`.
- Recommended embedding models:
  - `sentence-transformers/all-MiniLM-L6-v2` (dimension: 384)
  - `text-embedding-3-small` (dimension: 1536)
  - `BAAI/bge-small-en-v1.5` (dimension: 384)
- If `sentence-transformers` is not installed or when offline, the fallback deterministic embedder generates dimension-matched normalized vectors to prevent application downtime.
