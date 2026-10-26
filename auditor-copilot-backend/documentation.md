# Backend Service Documentation

## Overview
This backend service is built with FastAPI and serves as the core API for the Auditor Copilot application. It provides endpoints for document analysis, chat, SOP flow, and more, leveraging LLMs and various agents.

## Project Structure
```
backend-fastapi/
├── Dockerfile
├── requirements.txt
├── .env.example
├── app/
│   ├── config.py
│   ├── main.py
│   ├── schemas.py
│   ├── agents/
│   ├── llm/
│   ├── routers/
│   └── utils/
├── backend_env/ (Python virtual environment)
├── chroma_db/ (Vector DB)
```

## Key Directories & Files
- **app/main.py**: FastAPI app entry point.
- **app/config.py**: Configuration and environment variables.
- **app/agents/**: Agent logic for analysis, chat, documents, compliance, corporate, and SOP flow.
- **app/llm/**: LLM integration (AWS Bedrock, Azure OpenAI, etc.).
- **app/routers/**: API route definitions (chat, analysis, documents, compliance, corporate, etc.).
- **app/utils/**: Utility functions (PDF loader, search, streaming, vector store, etc.).
- **requirements.txt**: Python dependencies.
- **Dockerfile**: Containerization setup.
- **.env.example**: Example environment variables.

## Setup Instructions
1. **Clone the repository** and navigate to `backend-fastapi/`.
2. **Create a virtual environment** (optional, recommended):
   ```sh
   python -m venv backend_env
   source backend_env/Scripts/activate  # On Windows
   # or
   source backend_env/bin/activate      # On Unix
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update values as needed.
5. **Run the FastAPI server:**
   ```sh
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Docker Usage
To build and run the backend with Docker:
```sh
# Build the image
 docker build -t auditor-backend .
# Run the container
 docker run -d -p 8000:8000 --env-file .env auditor-backend
```

## API Endpoints
- `/api/chat` - Chat interface with streaming and ingestion support.
- `/api/analysis` - Document analysis and scenario-based streaming.
- `/api/documents` - Knowledge-base driven document Q&A (RAG).
- `/api/compliance` - Mode-based compliance audit workflows (IT/Finance).
- `/api/corporate` - Corporate accounting guidelines and justification notes analysis.
- `/api/sop_flow` - SOP flow flowchart generation.
- `/api/memory` - Conversation memory management.
- `/health` - Health check.

## Notes
- The backend uses a vector database (ChromaDB) for document embeddings.
- LLM providers are configurable via environment variables.
- For development, use the `--reload` flag with Uvicorn for auto-reload.

## Contributing
- Follow PEP8 style guidelines.
- Add docstrings and type hints where possible.
- Use pull requests for all changes.

## License
See repository root for license information.
