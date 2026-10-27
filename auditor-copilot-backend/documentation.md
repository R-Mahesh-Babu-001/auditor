# Backend Service Documentation

## Overview
This backend service is built with FastAPI and serves as the core API for the Auditor Copilot application. It provides endpoints for document analysis, chat, SOP flow, and more, leveraging LLMs, Neon PostgreSQL with pgvector, and various audit agents.

## Project Structure
```
auditor-copilot-backend/
├── Dockerfile
├── requirements.txt
├── .env
├── app/
│   ├── config.py       # Configuration and Neon DB / LLM settings
│   ├── main.py         # FastAPI application entrypoint
│   ├── schemas.py      # Pydantic request/response schemas
│   ├── agents/         # Agents (Analysis, Chat, Compliance, Corporate, Document, SOP Flow)
│   ├── llm/            # LLM integrations (Gemini, Azure OpenAI, AWS Bedrock)
│   ├── routers/        # API route definitions
│   └── utils/          # Utilities (Neon pgvector store, memory, PDF loader, streaming)
└── tests/              # Smoke and unit tests
```

## Database
- **Neon PostgreSQL (`pgvector`)**: Cloud serverless PostgreSQL database with the `pgvector` extension for storing and querying vector embeddings and document chunks.
- Supports agent-scoped, user-scoped, and mode-scoped namespaces (`DOCUMENT_ANALYSIS`, `CHAT_MEMORY_<user_id>`, `COMPLIANCE_MEMORY_<user_id>_<mode>`, etc.).
- Robust embedding pipeline supporting Google Gemini / GenAI, Azure OpenAI, standard OpenAI, and deterministic fallback embeddings.

## Key Directories & Files
- **app/main.py**: FastAPI app entry point.
- **app/config.py**: Configuration and environment variables (Neon PostgreSQL, Gemini, Azure, Bedrock).
- **app/agents/**: Agent logic for analysis, chat, documents, compliance, corporate, and SOP flow.
- **app/llm/**: LLM integration (Gemini, AWS Bedrock, Azure OpenAI, etc.).
- **app/routers/**: API route definitions (chat, analysis, documents, compliance, corporate, memory, health).
- **app/utils/vector_store.py**: Neon DB vector store (pgvector) utilities for document embedding, retrieval, and ingestion.
- **requirements.txt**: Python dependencies.
- **Dockerfile**: Containerization setup.

## Setup Instructions
1. **Navigate to `auditor-copilot-backend/`**.
2. **Create a virtual environment** (optional, recommended):
   ```sh
   python -m venv .venv
   source .venv/bin/activate      # On Unix
   # or
   .venv\Scripts\activate       # On Windows
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure environment variables in `.env`:**
   ```env
   DATABASE_URL=postgresql://<user>:<password>@<neon-host>/<dbname>?sslmode=require
   VECTOR_STORE_BACKEND=neon_pgvector
   GEMINI_MODEL=gemini-3.5-flash
   GEMINI_EMBEDDING_MODEL=gemini-embedding-001
   ```
5. **Run the FastAPI server:**
   ```sh
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints
- `/api/chat/stream` - Streaming chat with conversation memory in Neon DB.
- `/api/chat/ingest` - File ingestion into user chat memory in Neon DB.
- `/api/analysis/stream` - Audit scenario analysis and streaming.
- `/api/analysis/ingest` - File ingestion into user analysis memory in Neon DB.
- `/api/documents/query/stream` - Knowledge-base driven document Q&A (RAG) using Neon DB pgvector.
- `/api/documents/ingest` - Document ingestion into `DOCUMENT_ANALYSIS` collection in Neon DB.
- `/api/compliance/stream` & `/api/compliance/run` - Mode-based compliance audit workflows (IT/Finance).
- `/api/corporate/stream` & `/api/corporate/ingest` - Corporate accounting guidelines & justification notes.
- `/api/sop/flowchart` - SOP flow flowchart generation.
- `/api/memory/clear` - Clear vector memory from Neon DB for a specific namespace.
- `/health` - Health check including Neon DB connectivity status.
