# 🧠 U-MEM

## Universal Document Intelligence & Memory System (R&D)

U-MEM is a **research-oriented document intelligence and long-term memory system** that ingests unstructured documents, converts them into semantic vector memory, clusters knowledge automatically, and enables **high-quality semantic search** across documents.

The system is designed to evolve into a **retrieval-augmented memory backbone** for intelligent agents, copilots, and AI assistants.

---

## 🚀 What Problem Does U-MEM Solve?

Traditional file systems and keyword search fail when:

* Documents grow large and unstructured
* Meaning matters more than exact words
* Knowledge needs to be **remembered, grouped, and recalled**

U-MEM solves this by:

* Converting documents into **semantic memory**
* Organizing information automatically using **clustering**
* Retrieving answers using **meaning, not keywords**

---

## 🧩 High-Level Architecture

![Image](https://www.researchgate.net/publication/300085761/figure/fig2/AS%3A481011596304385%401491693509241/The-Semantic-Search-architecture-and-interface.png)

![Image](https://qdrant.tech/articles_data/what-is-a-vector-database/architecture-vector-db.png)

![Image](https://images.openai.com/static-rsc-3/e29GmmkEY0cgOZsAnufxLmitXMLQ9zsYJzM69qWPdjjcbFBGxSZkzAbw8gjL97nQ27-L9POSzau1wWpQ5Qe10Uy_WNHmUYvc6cHnSDlNlgU?purpose=fullsize\&v=1)

**Architecture Layers:**

```
Client / API
     ↓
FastAPI Layer
     ↓
Service Layer
(Extraction • Chunking • Embeddings • Search • Clustering)
     ↓
Memory Layer
(Vector Store + Metadata Store)
```

---

## 🏗️ System Components

### 1️⃣ Document Ingestion

* Supports **PDF, DOCX, PNG, TXT**
* Extracts raw text
* Normalizes and cleans content

### 2️⃣ Chunking Engine

* Splits documents into **semantic chunks**
* Each chunk becomes a memory unit

### 3️⃣ Embedding Pipeline

* Uses sentence-level embeddings
* Normalized vectors for cosine similarity
* Stored in FAISS vector index

### 4️⃣ Metadata Store

Maintains relationships:

```
vector_id → chunk_id → document_id
```

### 5️⃣ Semantic Search Engine

* Query is embedded
* Vector similarity search
* Chunk-level scoring
* Aggregated into **document-level ranking**

### 6️⃣ Topic Clustering (HDBSCAN)

* Automatically groups related chunks
* Assigns **cluster_id** to documents
* Enables thematic organization

---

## 🧠 Core Features Implemented

✅ File upload API
✅ Text extraction & normalization
✅ Chunk-level embedding storage
✅ Vector ↔ chunk ↔ document mapping
✅ Semantic search with ranking logic
✅ HDBSCAN topic clustering
✅ Cluster assignment to documents
✅ Clean GitHub-ready architecture

---

## 🛠️ Tech Stack

| Layer         | Technology               |
| ------------- | ------------------------ |
| Backend API   | FastAPI                  |
| Language      | Python                   |
| Vector Search | FAISS                    |
| Embeddings    | Sentence Transformers    |
| Clustering    | HDBSCAN                  |
| Storage       | JSON-based metadata      |
| Architecture  | Modular service-oriented |

---

## 📂 Project Structure (Simplified)

```
app/
├── api/                # FastAPI routes
├── services/           # Core intelligence logic
├── storage/            # Vector & metadata storage
├── models/             # Data models
├── core/               # Config & decision logic
├── main.py             # App entry point

data/
├── metadata/           # Runtime metadata (ignored in git)
├── raw_files/          # Uploaded documents (ignored)
├── vectors/            # Vector index (ignored)
```

---

## 🔍 Semantic Search Flow

![Image](https://www.researchgate.net/publication/356389086/figure/fig3/AS%3A1182277157552131%401658888248857/Flowchart-of-the-proposed-semantic-search.png)

![Image](https://media2.dev.to/dynamic/image/width%3D1000%2Cheight%3D420%2Cfit%3Dcover%2Cgravity%3Dauto%2Cformat%3Dauto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F9ymah9nzuldu86xzkdt5.png)

```
User Query
   ↓
Query Embedding
   ↓
Vector Similarity Search (FAISS)
   ↓
Chunk Matching
   ↓
Document Ranking
   ↓
Top Relevant Documents
```

---

## 🧪 Current Status (R&D Phase)

* System is **functionally complete** for:

  * Ingestion
  * Memory creation
  * Search
  * Clustering

* Focused on **correctness, architecture, and extensibility**

---

## 🔮 What’s Coming Next (Roadmap)

### 🔥 Phase 1 (Short Term)

* Search filters (subject, cluster, type)
* Cluster label generation (auto-topic names)
* Improved ranking heuristics

### 🔥 Phase 2 (Mid Term)

* Retrieval-Augmented Generation (RAG)
* Document-aware answer generation
* Memory update & reinforcement

### 🔥 Phase 3 (Long Term)

* Agent memory integration
* Cross-document reasoning
* Persistent long-term knowledge graphs

---

## 🎯 Why U-MEM Is Different

* Not just search → **memory**
* Not keyword-based → **semantic**
* Not flat → **clustered intelligence**
* Designed for **AI agents, not humans only**

---

## 📌 Research Note

U-MEM is an **experimental system** intended for:

* AI memory research
* Semantic retrieval systems
* RAG backends
* Intelligent assistants

---

## 👨‍💻 Author

Sandipan Chakraborty
AI / ML Engineer | Systems & Memory Architect
Project: U-MEM (R&D)


