# AuditReady Copilot (P2P Enterprise Edition)

AuditReady Copilot is an evidence-first, enterprise AI internal audit workspace engineered specifically for Procure-to-Pay (P2P) audits, IT General Controls (ITGC) segregation of duties reviews, and continuous monitoring.

The system features:
- **Relational Persistence**: Neon Serverless PostgreSQL with explicit qualification under the `audit_copilot` schema (47 tables).
- **Vector Retrieval**: Neon PGVector (`langchain_postgres.vectorstores.PGVector`) replacing legacy ChromaDB.
- **Exclusive LLM Provider**: Google Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`) exclusively powering intelligent workpaper synthesis, semantic claims mapping, and advisory chat. All Azure OpenAI and AWS Bedrock runtime paths have been removed.
- **Deterministic Audit Testing Engine**: Pure, explainable Python rules for 3-way matching, duplicate detection, authorization threshold verification, split-purchase risk signals, and reproducible stratified sampling. Zero hallucination risk on numerical audit calculations.
- **Full-Featured React Frontend**: Vite + React workspace providing executive dashboards, engagement tracking, dataset profiling, RCM coverage, exception triage, workpapers with claim citations, and remediation tracking.

---

## Architecture Overview

```
+-------------------------------------------------------------------------+
|                  React / Vite Audit Workspace Frontend                  |
|  - Executive Dashboard (Live Neon KPIs)    - RCM Explorer & Coverage    |
|  - Engagements & Scopes                    - Deterministic Test Runs    |
|  - Evidence & CSV/Excel Ledger Profiler    - Exceptions Triage Queue    |
|  - Workpapers & Claim Citations            - Remediation Tracking       |
|  - ITGC & SoD Review                       - Continuous Auditing        |
+-------------------------------------------------------------------------+
                                    | (REST APIs)
                                    v
+-------------------------------------------------------------------------+
|                        FastAPI Backend Engine                           |
|  - Health & Diagnostics (/health, /ready)                               |
|  - Context & Tenancy (/api/auth/me)                                     |
|  - Evidence Hashing & Processing (/api/evidence, /api/datasets)         |
|  - Deterministic Rule Engine (/api/tests/run)                            |
|  - Exceptions & Disposition (/api/exceptions)                           |
|  - Workpaper Synthesis with Gemini (/api/workpapers/generate)           |
+-------------------------------------------------------------------------+
                    |                                 |
       (Deterministic SQL & PGVector)       (Workpaper Synthesis & Chat)
                    v                                 v
+----------------------------------------+ +------------------------------+
|            Neon PostgreSQL             | |        Google Gemini         |
| - Schema: audit_copilot (47 tables)    | | - gemini-2.5-flash           |
| - Extensions: vector (pgvector), pgcrypto| - google-genai SDK           |
| - Connection Pooling (PgBouncer)       | | - langchain-google-genai     |
+----------------------------------------+ +------------------------------+
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Neon PostgreSQL connection string (`DATABASE_URL`)
- Google Gemini API key (`GEMINI_API_KEY`)

### 2. Backend Configuration & Startup

```bash
# Navigate to backend directory
cd auditor-copilot-backend

# Copy environment configuration
cp .env.example .env

# Configure your secrets in .env
# DATABASE_URL=postgresql://user:password@ep-sample-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
# GEMINI_API_KEY=your_gemini_api_key

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run deterministic audit unit tests
PYTHONPATH=. python tests/test_audit_rules.py

# Run Neon integration tests
PYTHONPATH=. python tests/test_neon_integration.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Startup

```bash
# Navigate to frontend directory
cd auditor-copilot-frontend

# Install dependencies
npm ci

# Run linting check
npm run lint

# Build production bundle
npm run build

# Start development server
npm run dev
```

Frontend will run at `http://localhost:3000` (or `http://localhost:5173`).

---

## Health Check & Verification

Verify the backend and database connection:

```bash
curl http://localhost:8000/health
```

Expected Response:
```json
{
  "status": "ok",
  "database": {
    "backend": "neon_pgvector",
    "neon_configured": true,
    "neon_status": "connected",
    "schema": "audit_copilot"
  },
  "llm_provider": {
    "primary": "google_gemini",
    "gemini_model": "gemini-2.5-flash",
    "gemini_configured": true
  }
}
```

Verify service readiness:
```bash
curl http://localhost:8000/ready
```

---

## Core Audit Procedures Implemented

| Rule Code | Procedure Type | Description |
| :--- | :--- | :--- |
| `P2P_THREE_WAY_MATCH` | Deterministic | Matches PO, Goods Receipt, and Invoice lines; flags quantity variances, price variances beyond tolerance %, missing PO, and missing receipt. |
| `P2P_DUPLICATE_INVOICE_PAYMENT` | Deterministic | Identifies exact duplicate invoice numbers/amounts per supplier, and proximate-date duplicate billing amounts. |
| `P2P_MISSING_APPROVAL` | Deterministic | Checks invoice amounts exceeding delegation of authority (DOA) limits for authorized supervisor approvals. |
| `P2P_THRESHOLD_SPLITTING` | Risk Signal | Detects structured purchases clustered just below procurement approval limits (e.g., $9,500 on a $10,000 threshold). |
| `P2P_SAMPLE_SELECTION` | Sampling | Reproducible, deterministic stratified sampling based on transaction values and fixed pseudo-random seeds. |
| `ITGC_SOD_CONFLICT` | IT Governance | Flags incompatible role combinations (e.g. PO Creation + Invoice Approval, Vendor Master Maintenance + Payment Release). |
| `ITGC_LEAVER_ACCESS` | IT Governance | Flags terminated employees who retain active system accounts in ERP ledgers. |
| `VENDOR_ASSURANCE_REVIEW` | Vendor Governance | Checks high-risk vendors for unexpired SOC 1/2 Type II reports and ISO 27001 certifications. |
| `AI_GOVERNANCE_REVIEW` | AI Governance | Audits corporate AI systems inventory for system owners, risk tier classifications, and monitoring plans (NIST AI RMF). |

---

## License & Security
Enterprise confidential. Credentials and sensitive financial evidence must remain within encrypted customer storage and tenant-isolated Neon PostgreSQL schemas.

