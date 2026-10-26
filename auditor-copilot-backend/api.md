# Auditor Copilot Backend API Documentation

This document outlines the API endpoints available in the Auditor Copilot Backend service.

## Base URL
All API endpoints (except health check) are prefixed with `/api`.

---

## Health Check

### `GET /health`
Checks the operational status of the backend service and validates configuration for LLM providers.

**Response:**
- `status`: "ok"
- `service`: "auditor-copilot-backend"
- `providers`: Object indicating if Azure OpenAI and AWS Bedrock are configured.

---

## Chat

### `POST /api/chat/stream`
Streams a chat response from the LLM agent based on the user's query.

**Request Body (`ChatRequest`):**
- `query` (string): The user's chat message or question.
- `llm_config` (object): Configuration for the LLM to use (provider, model, etc.).
- `user_id` (string, optional): Unique identifier for the user to maintain session context.

**Response:**
- Returns a Server-Sent Events (SSE) stream of the text response.

### `POST /api/chat/ingest`
Uploads and indexes files into a temporary chat memory for a specific user context.

**Parameters:**
- `user_id` (query parameter): Unique identifier for the user.

**Request Body:**
- `files` (multipart/form-data): List of files to upload and ingest.

**Response:**
- `status`: "ok"
- `files_ingested`: List of filenames that were successfully processed.

---

## Analysis

### `POST /api/analysis/stream`
Streams an audit analysis response based on a provided scenario description.

**Request Body (`AnalysisRequest`):**
- `scenario` (string): Description of the audit scenario to analyze.
- `llm_config` (object): Configuration for the LLM to use.

**Response:**
- Returns a Server-Sent Events (SSE) stream of the analysis.

### `POST /api/analysis/ingest`
Uploads and indexes files into a temporary analysis memory for a specific user context.

**Parameters:**
- `user_id` (query parameter): Unique identifier for the user.

**Request Body:**
- `files` (multipart/form-data): List of files to upload and ingest.

**Response:**
- `status`: "ok"
- `files_ingested`: List of filenames that were successfully processed.

---

## Document Analysis

### `POST /api/documents/query/stream`
Streams answers to questions based on the content of previously ingested documents.

**Request Body (`DocumentQueryRequest`):**
- `question` (string): The question to ask about the documents.
- `llm_config` (object): Configuration for the LLM to use.

**Response:**
- Returns a Server-Sent Events (SSE) stream of the answer.

### `POST /api/documents/ingest`
Uploads and indexes documents into the persistent document analysis collection.

**Request Body:**
- `files` (multipart/form-data): List of files to upload and ingest.

**Response:**
- `status`: "success"
- `files_ingested`: List of filenames processed.
- `documents_added`: Number of document chunks added to the vector store.

---

## SOP Flowchart

### `POST /api/sop/flowchart`
Generates a structured flowchart JSON from a text-based Standard Operating Procedure (SOP).

**Request Body (`SOPFlowRequest`):**
- Text content or parameters describing the SOP.

**Response:**
- `status`: "success"
- `data`: The generated flowchart structure.

---

## Compliance

### `POST /api/compliance/stream`
Streams a compliance analysis response.

**Request Body (`ComplianceRequest`):**
- `query` (string): The compliance question or scenario.
- `llm_config` (object): Configuration for the LLM.
- `mode` (string, optional): The compliance mode (e.g., "IT"). Defaults to "IT".
- `user_id` (string, optional): User context identifier.

**Response:**
- Returns a Server-Sent Events (SSE) stream of the analysis.

### `POST /api/compliance/run`
Executes a compliance analysis and returns the full result (non-streaming).

**Request Body (`ComplianceRequest`):**
- Same as `/api/compliance/stream`.

**Response:**
- JSON object containing the complete analysis result.

---

## Corporate Accounting

### `POST /api/corporate/stream`
Streams an analysis response for corporate accounting guidelines or justification notes.

**Request Body (`CorporateRequest`):**
- `query` (string): The query regarding guidelines or justification notes.
- `llm_config` (object): Configuration for the LLM to use.
- `user_id` (string, optional): Unique identifier for the user to maintain session context.

**Response:**
- Returns a Server-Sent Events (SSE) stream of the analysis.

### `POST /api/corporate/ingest`
Uploads and indexes files into a temporary corporate memory for a specific user context.

**Parameters:**
- `user_id` (query parameter): Unique identifier for the user.

**Request Body:**
- `files` (multipart/form-data): List of files to upload and ingest.

**Response:**
- `status`: "ok"
- `files_ingested`: List of filenames that were successfully processed.

---

## Memory Management

### `POST /api/memory/clear`
Clears the vector store memory for a specific agent context.

**Request Body (`ClearMemoryRequest`):**
- `agent` (string): The name of the agent memory to clear (e.g., "chat_memory").
- `user_id` (string, optional): The specific user ID to clear memory for.
- `mode` (string, optional): The specific mode to clear memory for (if applicable).

**Response:**
- `status`: "ok"
