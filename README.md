# AI Document Intelligence API

> Upload any PDF or text document and get instant AI-powered insights — semantic Q&A, summarisation, entity extraction, and sentiment analysis — served through a production RAG pipeline with sub-second retrieval.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io)
[![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat)](https://render.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Render-336791?style=flat&logo=postgresql)](https://render.com)
[![FAISS](https://img.shields.io/badge/Vector_Store-FAISS-0064A4?style=flat)](https://github.com/facebookresearch/faiss)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=flat&logo=githubactions)](https://github.com/features/actions)

---

## Live Demo

**Frontend (Streamlit):**
[https://hexdeploy-ai-document-in-doc-intel-apibackendappfrontend-acyyks.streamlit.app/](https://hexdeploy-ai-document-in-doc-intel-apibackendappfrontend-acyyks.streamlit.app/)

> **Note:** The backend runs on Render's free tier — the first request after idle may take 30–60 seconds to wake the container. Subsequent requests resolve at sub-second latency once the instance is hot.

---

## What It Does

Most document workflows — legal review, research, HR screening — require manually reading hundreds of pages to extract what matters. This system removes that bottleneck entirely.

Upload a PDF or text file → the system chunks it, embeds it into a FAISS vector space, and gives you:

| Endpoint | What You Get |
|---|---|
| `POST /api/upload` | Parse + index document into FAISS vector store |
| `POST /api/ask` | Semantic Q&A with retrieved context chunks |
| `POST /api/summarise` | Concise AI-generated summary |
| `POST /api/entities` | Extracted people, organisations, dates, locations |
| `POST /api/sentiment` | Document-level sentiment with confidence score |
| `GET  /api/benchmark` | Retrieval latency, chunk hit rate, query throughput |
| `GET  /health` | Service health check |

---

## Architecture

```
[ Streamlit Cloud UI ]
        │
        │  TLS + X-API-Key Header
        ▼
[ FastAPI / Render Web Service ]
        │                    │
  (FAISS Vector Engine)  (SQLAlchemy)
        │                    │
  [ vector_stores/ ]   [ Render PostgreSQL ]
```

**Three-tier decoupled microservices across two cloud providers:**

- **Presentation Layer** — Streamlit Cloud manages file upload UI, multi-turn chat state, and insight display panels
- **Application Gateway** — FastAPI on Render handles security validation, RAG orchestration, chunking, and all API routing
- **Data Layer** — FAISS handles high-dimensional semantic vector indexing; PostgreSQL tracks all operational telemetry via SQLAlchemy

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Python 3.11 |
| LLM | Google Gemini 1.5 Flash |
| RAG Framework | LangChain |
| Embeddings | Google text-embedding-004 |
| Vector Store | FAISS (persistent, disk-backed via `vector_stores/`) |
| PDF Parsing | PyMuPDF (fitz) |
| Relational DB | PostgreSQL (Render Managed Cluster) |
| ORM / Telemetry | SQLAlchemy (async) |
| Frontend | Streamlit |
| Auth | X-API-Key header (zero-trust, dropped at gateway) |
| Rate Limiting | SlowAPI (5 index ops/min, 20 query ops/min) |
| Deployment (API) | Render (Dockerized) |
| Deployment (UI) | Streamlit Cloud |
| CI/CD | GitHub Actions |

---

## Project Structure

```
doc-intel-api/
├── app/
│   ├── models/           # Pydantic request/response schemas
│   ├── routers/          # Route handlers (auth, ingest, query, benchmark)
│   ├── services/         # Core RAG engine, embedder, parser, sentiment
│   ├── utils/            # Cryptographic utilities, chunking helpers
│   ├── database.py       # SQLAlchemy PostgreSQL session + engine setup
│   ├── models.py         # Telemetry log ORM schema
│   ├── main.py           # FastAPI app entry, security middleware assembly
│   └── frontend.py       # Streamlit workspace UI
├── vector_stores/        # Persisted FAISS index blocks (per document)
├── .github/
│   └── workflows/
│       └── deploy.yml    # GitHub Actions CI/CD pipeline
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Key Engineering Decisions

### Zero-Trust API Security
Every request crossing from the Streamlit frontend to the FastAPI backend must present a valid `X-API-Key` header. Unauthenticated calls are dropped at the gateway before any downstream processing — preventing unauthorised access and avoiding unnecessary LLM cost generation.

### Token-Bucket Rate Limiting (SlowAPI)
To protect LLM API quota and server processing capacity:
- **5 file index operations per minute** per IP
- **20 conversational query requests per minute** per IP

### Persistent FAISS Vector Storage
FAISS indexes are written to disk under `vector_stores/` on each upload, eliminating the need to re-index documents on every container restart. Index files are mapped by document signature hash for collision-safe retrieval.

### PostgreSQL Telemetry Logging
All pipeline events — upload timestamps, chunk counts, file signatures, query latencies, and HTTP 400/500 tracebacks — are committed transactionally to a managed PostgreSQL cluster via async SQLAlchemy workers, providing complete production observability.

### Benchmark Endpoint
`GET /api/benchmark` returns real operational metrics: average retrieval latency, chunk hit rate, and total queries processed since last cold start. This was deliberately built to surface measurable performance data rather than rely on subjective demo impressions.

---

## Local Setup

### Prerequisites
- Python 3.11+
- Google Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))
- PostgreSQL instance (local or Render free tier)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/hexdeploy/doc-intel-api
cd doc-intel-api

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Fill in: GEMINI_API_KEY, DATABASE_URL, X_API_KEY

# 5. Start the FastAPI backend
uvicorn app.main:app --reload --port 8000

# 6. In a separate terminal, start the Streamlit frontend
streamlit run app/frontend.py
```

Visit `http://localhost:8501` for the UI or `http://localhost:8000/docs` for the interactive API docs.

---

## API Reference

All endpoints require the `X-API-Key` header.

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data
X-API-Key: your-key

file: <PDF or .txt>
```
**Response:**
```json
{
  "document_id": "a3f9c2...",
  "pages": 12,
  "chunks_indexed": 47,
  "status": "indexed"
}
```

### Ask a Question
```http
POST /api/ask
Content-Type: application/json
X-API-Key: your-key

{
  "document_id": "a3f9c2...",
  "question": "What are the key financial risks mentioned?"
}
```
**Response:**
```json
{
  "answer": "The document identifies three key financial risks...",
  "source_chunks": ["chunk_12", "chunk_31"],
  "latency_ms": 843
}
```

### Benchmark Metrics
```http
GET /api/benchmark
X-API-Key: your-key
```
**Response:**
```json
{
  "avg_retrieval_latency_ms": 912,
  "chunk_hit_rate": 0.87,
  "total_queries_processed": 142,
  "uptime_seconds": 3600
}
```

---

## Performance

| Metric | Result |
|---|---|
| Average query retrieval latency | < 2 seconds |
| Chunk hit rate | 87%+ |
| Max document size tested | 98 pages |
| Vector similarity search | Sub-second (FAISS in-process) |

---

## Security

- All secrets managed via environment variables — never committed to source
- `.gitignore` masks `.venv/`, `.env`, `vector_stores/`, and execution logs
- API key auth enforced at gateway layer on every inter-service request
- Unauthenticated requests return `403` immediately with no downstream cost

---

## Roadmap

- [ ] OCR support for scanned PDFs (pytesseract + pdf2image)
- [ ] Structured table extraction to Markdown/JSON (pdfplumber)
- [ ] Multi-document workspace with switchable sidebar
- [ ] Streaming token-by-token LLM responses
- [ ] LlamaIndex integration as alternative RAG framework

---

## Author

**Anup Bileyali**
CS + AI/ML Graduate, R L Jalappa Institute of Technology (Batch 2026)

[github.com/hexdeploy](https://github.com/hexdeploy) · [linkedin.com/in/anup-bileyali](https://linkedin.com/in/anup-bileyali)
