# Enterprise Document Intelligence Workspace

A production-deployed, multi-cloud Retrieval-Augmented Generation (RAG) platform that lets users upload unstructured text or PDF documents, index them into a vector store, and run multi-turn conversational Q&A over that content using a generative AI model.

**Live Demo:** [hexdeploy-ai-document-in-doc-intel-apibackendappfrontend-acyyks.streamlit.app](https://hexdeploy-ai-document-in-doc-intel-apibackendappfrontend-acyyks.streamlit.app/)

---

## Overview

This project moves beyond a local prototype into a fully decoupled three-tier architecture, separating the UI, application/API layer, and data/vector storage across independent cloud services. It supports asynchronous document ingestion, chunking, embedding, and semantic retrieval, with conversational responses grounded in the uploaded documents.

## Architecture

```
[ Presentation UI Tier ] ────( Streamlit Cloud )
              │
     TLS + X-API-Key header
              │
              ▼
[ Application Gateway ] ──────( FastAPI on Render )
              │                        │
     (Local vector mapping)     (SQLAlchemy ORM)
              │                        │
              ▼                        ▼
     [ FAISS Vector Engine ]   [ PostgreSQL (Render) ]
```

| Tier | Framework / Provider | Purpose |
|---|---|---|
| Presentation Layer | Streamlit Cloud | File upload UI, chat interface, session state |
| Application Gateway | FastAPI (Render Web Service) | Auth, text parsing, chunking, RAG orchestration |
| Vector Engine | FAISS (in-memory) | Semantic similarity search over embedded chunks |
| Relational Database | PostgreSQL (Render) | Telemetry, processing logs, chunk indices, diagnostics |

## Key Features

- **RAG pipeline** — ingests text/PDF documents, chunks and embeds them, and retrieves relevant context for LLM-generated answers
- **Multi-turn conversation** — maintains chat context across a session
- **API key authentication** — every request from the frontend to backend requires a valid `X-API-Key` header; unauthenticated requests are rejected at the gateway
- **Rate limiting** — IP-based throttling via SlowAPI (5 file-index operations/min, 20 query requests/min) to protect the backend and control LLM cost
- **Telemetry logging** — all processing events, timestamps, file signatures, and error tracebacks are logged to PostgreSQL for observability

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SlowAPI
- **Frontend:** Streamlit
- **Vector Search:** FAISS
- **Database:** PostgreSQL
- **LLM:** Gemini API
- **Hosting:** Render (API + DB), Streamlit Cloud (UI)

## Project Structure

```
doc-intel-api/
├── app/
│   ├── models/          # DB schema structures and telemetry tracking
│   ├── routers/          # Route handlers (auth, ingest)
│   ├── services/          # Core RAG parsing/orchestration logic
│   ├── utils/            # Utility and cryptographic helpers
│   ├── database.py        # SQLAlchemy PostgreSQL session/engine setup
│   ├── models.py          # Telemetry log schemas
│   ├── main.py            # FastAPI app entrypoint and security setup
│   └── frontend.py        # Streamlit UI source
├── vector_stores/          # Local FAISS index storage
├── requirements.txt
└── .gitignore
```

## Known Constraints

- **Cold starts:** The backend runs on Render's free tier, which spins down after inactivity. The first request after idling will have a brief lag while the container wakes up; subsequent requests are fast.
- **In-memory vector storage:** FAISS indexes live inside the backend's runtime container, so storage paths must stay consistent between local development and deployment.

## Security

- All frontend → backend calls require a valid `X-API-Key`; unauthenticated calls are rejected before hitting business logic.
- Secrets (API keys, DB credentials) are stored as environment variables, not committed to source control (`.gitignore` covers `.venv/`, logs, and secret files).

## Status

Stable and actively deployed as of July 2026.

---

*Built by [hexdeploy](https://github.com/hexdeploy)*
