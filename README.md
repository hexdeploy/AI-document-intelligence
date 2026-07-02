# 🚀 Enterprise Document Intelligence Workspace

A production-grade, multi-cloud Retrieval-Augmented Generation (RAG) platform designed to process, securely index, and query unstructured enterprise documentation (PDFs and TXT files). Built using a completely decoupled architecture, the system leverages high-performance asynchronous vector space mapping, custom header security clearances, and automated transactional relational database audit tracking.

🌐 **Live Presentation UI:** [Launch Interactive Workspace](https://hexdeploy-ai-document-in-doc-intel-apibackendappfrontend-acyyks.streamlit.app/)

---

## 🏗️ Distributed System Architecture

The ecosystem relies on a modern, decoupled three-tier microservices architecture distributed across isolated cloud ecosystems to optimize processing workloads and isolate state.

* **Presentation Layer (Frontend):** A reactive dashboard hosted on **Streamlit Cloud** optimized for streaming layout files, presenting vector search token states, and managing multi-turn conversational chat views.
* **Application Gateway (Backend API):** A high-throughput **FastAPI** server hosted on **Render** managing cryptographic validation, text parsing logic, dynamic chunk segmentation routines, and orchestration of advanced LLM engines.
* **Vector Engine & Relational Core:** Utilizes localized **FAISS** index spaces for multi-dimensional mathematical similarity mappings alongside an auto-migrating, managed **PostgreSQL** cluster on **Render** tracking structural telemetry logs.

```text
[Streamlit Cloud Frontend]
           │
     (TLS Secure)
   Custom Header Auth (X-API-Key)
           │
           ▼
  [Render FastAPI API] ────(Async Chunks)────> [FAISS Vector Store]
           │                                          │
    (SQLAlchemy ORM)                           (Native Embeddings)
           │                                          │
           ▼                                          ▼
[Render PostgreSQL DB Log]                 [Google Gemini-2.5-Flash]

⚡ Key Architectural Features
Custom Cryptographic Middleware: All inter-service request routing is secured via an explicit X-API-Key dependency injection system, mitigating unauthenticated perimeter mapping risks.

Mitigated LLM Exhaustion (Rate Limiting): Integrated an IP-targeted SlowAPI token-bucket throttling layer (5 uploads/min, 20 queries/min) to safeguard system resources and prevent downstream API cost overruns.

Fault-Tolerant Text Extraction Hierarchy: Processes multi-format streams with dynamic byte allocation (io.BytesIO) using a sliding structural fallback loop to evaluate corrupt layouts or empty page data blocks.

Automated Database Telemetry Logging: Real-time data logging utilizing the SQLAlchemy ORM layer. Successful extractions and system exceptions (HTTP 400/500) are immediately committed to Postgres for monitoring.

Batch-Throttled Vector Mappings: To respect upstream API rate limits, text chunks are split into sliding windows using a RecursiveCharacterTextSplitter (1000 character chunks / 150 character overlap) and loaded into FAISS using a safety-delay ingestion queue.

🛠️ The Production Tech StackComponentFramework / TechnologyPurposeFrontend UIStreamlitUI Rendering & Dynamic Multi-Turn Chat StatesAPI FrameworkFastAPI (Python)High-Performance REST Gateway & Auth PipelineOrchestrationLangChain CoreRAG Infrastructure, Chunking, and Prompt EngineeringVector IndexFAISSHigh-Dimensional Localized Semantic Similarity SearchAI ModelsGemini 2.5 Flash & Embedding-001Content Synthesis, Intent Comprehension, & Vector GenerationORM CoreSQLAlchemyPythonic Object-Relational Database Mapping CoreDatabase ServerManaged PostgreSQLPermanent Operational Logs & Incident Telemetry Tracking
