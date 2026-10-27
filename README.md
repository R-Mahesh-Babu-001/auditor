# AuditReady Copilot (P2P Enterprise Edition)

AuditReady Copilot is an evidence-first, enterprise AI internal audit workspace engineered specifically for Procure-to-Pay (P2P) audits, IT General Controls (ITGC) segregation of duties reviews, and continuous monitoring.

The system features:
- **Authoritative Relational Persistence**: Neon Serverless PostgreSQL with explicit qualification under the `audit_copilot` schema (47 tables).
- **Dedicated Vector Database**: Qdrant Cloud Free (`QdrantAuditVectorStore`) with native `:memory:` fallback for policy, document, and contract semantic search with strict tenant/engagement metadata filtering. Authoritative financial calculations and transaction reconciliation NEVER rely on vector similarity.
- **Exclusive Generative LLM Provider**: Google Gemini (`gemini-3.5-flash`, `gemini-2.5-pro`) exclusively powering intelligent workpaper synthesis, semantic claims mapping, and advisory chat.
- **Dataset-Specific Deterministic Audit Engine**: Pure, explainable Python rules for 3-way matching, duplicate detection, authorization threshold verification, split-purchase risk signals, period cutoff review, and reproducible stratified sampling. Each rule declares required canonical dataset types (`purchase_orders`, `goods_receipts`, `invoices`, `payments`, `approvals`, `suppliers`, `user_access`, `employee_directory`, `ai_system_inventory`) and rejects missing or ambiguous selections.
- **Complete Evidence & Source Row Traceability**: Every identified exception automatically links and persists all contributing source rows (`ExceptionRowLink`) and supporting documents (`ExceptionEvidenceLink`) in Neon DB.
- **Genuine Authentication & Authorization**: JWT Bearer token authentication, 401 unauthenticated enforcement in production/strict mode, 403 cross-tenant isolation, and role gates (Auditor, Reviewer, Manager, Org Admin) requiring reviewer approval for workpapers and findings.
- **Truthful Dataset Profiling**: Canonical field mapping, SHA-256 file deduplication, and row-level validation metrics (`valid_row_count`, `invalid_row_count`, `validation_errors`).
- **Structured Facts Workpaper Generation**: Compiles deterministic facts packet with SHA-256 snapshot hashing (`input_snapshot_hash`), structured narrative generation, and mandatory human reviewer approval gate (`POST /api/workpapers/{id}/approve`).
- **Interactive React Frontend**: Vite + React 19 workspace with executive KPIs, engagement tracking, dataset profiling, RCM coverage, exception triage, workpapers, Prompt Library, and remediation tracking.

---

## Architecture Overview

```
+-------------------------------------------------------------------------+
|                  React / Vite Audit Workspace Frontend                  |
|  - Executive Dashboard (Live Neon KPIs)    - RCM Explorer & Coverage    |
|  - Engagements & Multi-Tenant Context      - Deterministic Test Runs    |
|  - Datasets & Ledger Profiler              - Exceptions Triage Queue    |
|  - Workpapers & Reviewer Sign-Off          - Remediation Tracking       |
|  - Prompt Library with P2P Workflows       - Continuous Auditing        |
+-------------------------------------------------------------------------+
                                    | (REST APIs with JWT Bearer Token)
                                    v
+-------------------------------------------------------------------------+
|                        FastAPI Backend Engine                           |
|  - Auth & Context Guard (/api/auth/token, /api/auth/me)                 |
|  - Health & Diagnostics (/health, /ready - Neon, Qdrant, Gemini)        |
|  - Datasets & Truthful Validation (/api/datasets)                       |
|  - Deterministic Rule Engine (/api/tests/run)                           |
|  - Exceptions & Source Row Traceability (/api/exceptions)               |
|  - Gemini Workpaper Synthesis & Sign-Off (/api/workpapers)              |
+-------------------------------------------------------------------------+
          |                         |                         |
(Deterministic SQL)        (Semantic Retrieval)      (Grounded Synthesis)
          v                         v                         v
+-----------------------+ +--------------------+ +------------------------+
|    Neon PostgreSQL    | | Qdrant Vector DB   | |     Google Gemini      |
| - Schema: audit_copilot| - Qdrant Cloud Free | | - gemini-3.5-flash     |
|   (47 tables)         | - Local :memory:     | | - Pydantic structured  |
| - Relational storage  | - Tenant isolated    | |   workpaper narrative  |
| - Connection pooling  | - Document search    | | - google-genai SDK     |
+-----------------------+ +--------------------+ +------------------------+
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Neon PostgreSQL connection string (`DATABASE_URL`)
- Google Gemini API key (`GEMINI_API_KEY`)
- Qdrant Cloud URL & Key (`QDRANT_URL`, `QDRANT_API_KEY`) or in-memory mode

### 2. Backend Configuration & Startup

```bash
# Navigate to backend directory
cd auditor-copilot-backend

# Copy environment configuration
cp .env.example .env

# Configure your secrets in .env
# DATABASE_URL=postgresql://user:password@ep-sample-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
# GEMINI_API_KEY=your_gemini_api_key
# QDRANT_URL=https://your-cluster.qdrant.io
# QDRANT_API_KEY=your_qdrant_key

# Activate virtual environment
source .venv/bin/activate

# Run automated test suites (47 tests)
PYTHONPATH=. pytest tests/ -v

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Startup

```bash
# Navigate to frontend directory
cd auditor-copilot-frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start development server
npm run dev
```

---

## Automated Test Coverage

The test suite includes 47 automated tests covering all critical components:

| Test Suite | Purpose | Tests | Status |
|:---|:---|:---:|:---:|
| `test_dataset_selection.py` | Canonical rule specs, distinct collections, missing & ambiguous dataset errors, decimal precision | 6 | PASSED |
| `test_auth_security.py` | JWT token issuance/verification, 401 unauthenticated, 403 cross-tenant isolation, reviewer role gate | 6 | PASSED |
| `test_evidence_linking.py` | Multi-row `ExceptionRowLink` persistence for 3-way match, duplicate invoices, and PO mismatch | 2 | PASSED |
| `test_qdrant_integration.py` | Qdrant Cloud / :memory: upsert, semantic search, document deletion, multi-tenant filtering, healthcheck | 4 | PASSED |
| `test_workpaper_generation.py` | Verified facts packet hashing (`input_snapshot_hash`), draft status, reviewer approval gate | 2 | PASSED |
| `test_e2e_p2p_flow.py` | Complete synthetic P2P lifecycle (3-way match, duplicate, missing approval, cutoff, workpaper sign-off) | 5 | PASSED |
| `test_audit_rules.py` | Deterministic unit tests across all P2P, ITGC SoD, Vendor, and AI governance rules | 14 | PASSED |
| `test_api_smoke.py` | Health endpoints, memory clearing, system status | 2 | PASSED |
| `test_neon_integration.py` | Database connectivity, schema verification, collection naming logic | 4 | PASSED |
| `test_corporate_agent.py` | Corporate agent streaming and ingest smoke tests | 2 | PASSED |
| **Total** | | **47** | **ALL PASSED** |
