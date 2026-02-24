# 🧠 U-MEM

## Universal Memory Engine Management

### A Modular Semantic Memory Architecture for Intelligent Systems

---

## 📌 Overview

**U-MEM** is a research-oriented semantic memory architecture designed to transform unstructured documents into structured, persistent, and cluster-aware vector memory.

Unlike traditional keyword-based systems, U-MEM operates on dense semantic representations and organizes knowledge at the **chunk level**, enabling:

* Meaning-based retrieval
* Document-level ranking
* Structured memory mapping
* Cluster-aware knowledge organization
* Extensible retrieval-augmented reasoning

> U-MEM is designed as a memory backbone for intelligent agents and AI systems.

---

# 📄 Abstract

Modern document systems treat documents as flat text blobs indexed via keywords.
U-MEM introduces a structured memory abstraction where:

* Each document is decomposed into semantic chunks
* Each chunk becomes an atomic memory unit
* Each memory unit is embedded and indexed
* Metadata forms a structured relational layer
* Retrieval aggregates meaning at document level

This enables **persistent semantic memory modeling**, preparing the system for future integration with RAG and agent-native memory systems.

---

# ❗ Problem Statement

Modern document systems fail when:

* Meaning diverges from keywords
* Documents are large and unstructured
* Retrieval lacks document-level aggregation
* Memory structure is not persistent

Most pipelines follow:

```
Document → Embedding → Vector Search
```

But ignore:

* Chunk-level modeling
* Structured metadata relationships
* Document-level ranking logic
* Thematic clustering

U-MEM addresses these architectural gaps.

---

# 🏗 High-Level System Architecture

## 🔷 System Architecture Diagram

![Image](https://miro.medium.com/1%2AwHqtILSjqYsF6RnDq2CJDA.png)

### Architecture Flow

```
Client
   ↓
FastAPI API Layer
   ↓
Service Layer
   • Extraction
   • Cleaning
   • Chunking
   • Embedding
   • Search
   • Clustering
   ↓
Memory Layer
   • FAISS Vector Index
   • Metadata Store
   ↓
Runtime Storage
```

---

# 🧩 Core Technologies

## Backend Framework

**FastAPI**

* REST API layer
* Async processing
* Swagger documentation
* Modular routing

---

## Vector Memory Engine

**FAISS**

* Dense vector indexing
* Approximate nearest neighbor search
* Cosine similarity support
* High-dimensional embedding efficiency

FAISS acts as the **dense semantic memory index**.

---

## Embedding System

* Sentence-transformer embeddings
* Normalized dense vectors
* Cosine similarity retrieval

Pipeline:

```
Chunk → Embedding Model → Dense Vector → FAISS Index
```

---

## Clustering Engine

**HDBSCAN**

Why HDBSCAN?

* Density-aware
* No predefined cluster count
* Noise robust
* Suitable for high-dimensional embeddings

Output mapping:

```
document_id → cluster_id
```

---

# 📥 Document Ingestion & Chunking

Supported formats:

* PDF
* DOCX
* TXT
* PNG (OCR extensible)

Processing pipeline:

1. Text extraction
2. Cleaning & normalization
3. Semantic chunking
4. Structured storage

Each chunk becomes an **atomic memory unit**.

### Memory Mapping

```
vector_id → chunk_id → document_id → cluster_id
```

This ensures:

* Fine-grained retrieval
* Structured aggregation
* Memory growth consistency

---

# 🔎 Semantic Retrieval Pipeline

## Retrieval Flow Diagram

![Image](https://miro.medium.com/0%2A7OaGfO2DctgswevJ.jpeg)

![Image](https://sfoteini.github.io/images/post/image-vector-similarity-search-with-azure-computer-vision-and-postgresql/vector-search-flow_huf8a169ce5211bcd5ad8e6422d4d5b0fa_107385_853x401_fit_q95_h2_lanczos_3.webp)

### Retrieval Steps

```
User Query
   ↓
Query Embedding
   ↓
FAISS Similarity Search
   ↓
Top-k Chunk Retrieval
   ↓
Chunk Scoring
   ↓
Document Aggregation
   ↓
Ranked Documents
```

### Ranking Strategy

Instead of returning isolated chunks, U-MEM:

* Aggregates similarity scores per document
* Applies scoring heuristics
* Produces stable document-level ranking

This reduces retrieval fragmentation.

---

# 🔗 Metadata Memory Layer

Structured relationships:

```
vector_id → chunk_id
chunk_id → document_id
document_id → cluster_id
```

Why this matters:

* Enables document-level ranking
* Supports cluster-based grouping
* Prepares system for knowledge graph integration
* Maintains inspectable memory state

Metadata is currently stored in JSON for research transparency.

---

# ⚙ Computational Characteristics

| Operation          | Complexity |
| ------------------ | ---------- |
| Embedding          | O(n)       |
| Vector Insertion   | O(n)       |
| Approximate Search | O(log n)   |
| Clustering         | O(n log n) |

Optimized for:

* Research-scale experimentation
* Architectural extensibility
* Semantic correctness

---

# ⚠ Current Limitations

### 1️⃣ Scalability Constraints

* FAISS index is local
* No distributed infrastructure
* Moderate-scale corpus design

---

### 2️⃣ Static Embedding Model

* No domain fine-tuning
* No adaptive updates
* No reinforcement learning loop

---

### 3️⃣ No Real-Time Memory Reinforcement

* Retrieval does not improve via feedback
* No ranking optimization

---

### 4️⃣ No Generative Layer Yet

* Pure retrieval system
* No RAG integration yet

---

### 5️⃣ Metadata Storage Simplicity

* JSON-based
* Not production-optimized
* Needs migration to structured DB

---

### 6️⃣ No Cloud-Native Infrastructure

* Not containerized
* No object storage integration
* No distributed vector DB

---

# 🚀 Future Implementation Roadmap

## Phase I – Retrieval Optimization

* Advanced ranking heuristics
* Cluster auto-labeling
* Metadata filtering
* Benchmark suite

---

## Phase II – Retrieval-Augmented Generation

* LLM integration
* Context-aware synthesis
* Multi-document reasoning
* Prompt-aware memory retrieval

---

## Phase III – Agent-Native Memory

* Persistent agent memory
* Reinforcement-based memory scoring
* Knowledge graph overlay
* Memory decay strategies

---

## Phase IV – Production Upgrade

* Distributed vector DB (Qdrant / Milvus)
* PostgreSQL metadata store
* Neo4j graph integration
* Docker containerization
* Cloud storage integration

---

# 📁 Project Structure

```
app/
├── api/
├── services/
├── storage/
├── models/
├── core/
├── main.py

tests/

data/ (ignored in git)
├── metadata/
├── raw_files/
├── vectors/

docs/
└── images/
```

Runtime data is excluded from version control.

---

# ⚙ Installation

```bash
git clone https://github.com/sid0803/U-MEM-Universal-Document-Intelligence-Memory-System.git
cd U-MEM-Universal-Document-Intelligence-Memory-System
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run server:

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# 🧪 Research Orientation

U-MEM is designed as:

* Semantic retrieval research framework
* Memory architecture experiment
* RAG backbone prototype
* Agent memory infrastructure

It is intentionally modular and designed for iterative evolution.

---

# 👨‍💻 Author

**Sandipan Chakraborty**
AI / ML Engineer
Systems & Memory Architecture Research

Project: **U-MEM**

