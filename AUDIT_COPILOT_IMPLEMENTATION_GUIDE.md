# AuditReady Copilot - Master Implementation Guide

## 1. Executive Summary & Purpose

AuditReady Copilot is an enterprise-grade internal audit automation platform engineered specifically for **Procure-to-Pay (P2P)** audits, **IT General Controls (ITGC)** segregation of duties testing, **Vendor Assurance**, and **Continuous Auditing**.

This guide documents the complete technical architecture, database migration to **Neon PostgreSQL (`audit_copilot` schema)**, the transition to **Google Gemini** as the exclusive LLM provider, the implementation of deterministic, zero-hallucination audit testing engines in Python, and the end-to-end integration of the React/Vite frontend workspace.

---

## 2. Architecture & Design Principles

### 2.1 Core Architectural Principles
1. **Evidence-First Integrity**: Every audit assertion, workpaper sentence, and reported finding must link directly to verified documentary evidence (PO, goods receipt, invoice, bank remittance, or policy document) stored with SHA-256 integrity hashes.
2. **Deterministic Test Execution**: Calculations that determine audit exceptions (e.g. 3-way match variances, duplicate invoices, cutoff dates, dollar approval limits) are executed strictly using deterministic Python algorithms. Large Language Models are **never** used to compute mathematical tolerances or scan numbers.
3. **Targeted AI Utilization**: Google Gemini is used solely where language intelligence is required:
   - Extracting structured attributes from unstructured contracts and SOPs.
   - Suggesting column-to-canonical schema mappings for uploaded ledgers.
   - Synthesizing professional, IIA/IPPF-compliant workpapers citing verified evidence fragments.
   - Interactive auditor advisory chat grounded in Neon PGVector embeddings.
4. **Lean Persistence & Cost Optimization**: Raw file bytes remain in external local/object storage (`storage/evidence_uploads`), while structured metadata, hashes, fragments, and vector embeddings reside in Neon PostgreSQL, respecting Neon serverless storage quotas.

---

## 3. Neon PostgreSQL Relational & Vector Persistence

### 3.1 Schema & Table Layout
The platform connects to Neon PostgreSQL using SQLAlchemy 2.0 with the pre-provisioned `audit_copilot` schema containing 47 relational tables:

```
audit_copilot/
  ├── Tenancy & Users (organizations, app_users, organization_memberships, audit_engagements)
  ├── Evidence & Datasets (evidence_files, evidence_fragments, audit_datasets, dataset_columns, dataset_rows)
  ├── P2P Entities (p2p_suppliers, p2p_purchase_orders, p2p_goods_receipts, p2p_invoices, p2p_payments, p2p_approval_events)
  ├── RCM Governance (audit_criteria, audit_risks, audit_controls, criteria_control_mappings, risk_control_mappings)
  ├── Testing & Exceptions (audit_test_rule_templates, audit_test_rules, audit_test_runs, audit_exceptions, exception_row_links)
  ├── Workpapers & Findings (audit_findings, workpapers, workpaper_versions, workpaper_evidence_links, remediation_actions)
  └── Audit Governance (agent_runs, chat_conversations, chat_messages, sop_process_maps, audit_event_log)
```

### 3.2 PgBouncer Connection Pooler Handling
Neon utilizes serverless PgBouncer connection poolers (`ep-*-pooler.*.aws.neon.tech`). Passing `search_path` options in client startup connection parameters is explicitly rejected by PgBouncer (`ERROR: unsupported startup parameter in options: search_path`).
- **Solution**: Every SQLAlchemy ORM model explicitly specifies `__table_args__ = {"schema": "audit_copilot"}`. This generates fully-qualified SQL queries (e.g. `SELECT ... FROM audit_copilot.audit_exceptions`) that work seamlessly across both direct connections and PgBouncer poolers.
- **Connection Recycling**: Database engine is configured with `pool_pre_ping=True` and `pool_recycle=300` to automatically recover from idle serverless scale-to-zero wakeups.

### 3.3 Vector Embeddings with Neon PGVector
ChromaDB has been completely purged from the repository. Vector indexing is handled natively in Neon PostgreSQL using `langchain_postgres.vectorstores.PGVector`:
- Connection utilizes the existing `DATABASE_URL` with the `pgvector` extension.
- Embeddings are generated using Google Gemini embeddings (`models/text-embedding-004`).
- A `DeterministicFallbackEmbeddings` model and `ResilientEmbeddingsWrapper` ensure local development and offline environments generate consistent, deterministic 768-dimensional vectors when external network egress is restricted.

---

## 4. Exclusive LLM Provider: Google Gemini

All legacy runtime paths to Azure OpenAI and AWS Bedrock have been removed.
- **Primary Model**: `gemini-2.5-flash` (or `gemini-2.5-pro` for deep analytical workpaper generation).
- **Client Libraries**: `google-genai` and `langchain-google-genai`.
- **Factory Routing**: `app.llm.llm_factory.get_llm()` routes exclusively to `app.llm.gemini.get_gemini_chat()`. Any attempt to request legacy providers raises a `ValueError` or automatically defaults to Gemini.
- **Health Reporting**: `/health` endpoint exposes real-time Gemini configuration status and Neon connectivity status.

---

## 5. Deterministic Audit Testing Engines

All audit rules reside in `app/audit/rules/`:

### 5.1 Three-Way Match (`P2P_THREE_WAY_MATCH`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_three_way_match()`
- **Logic**:
  - Compares Purchase Orders, Goods Receipts, and Vendor Invoices by PO number and line numbers.
  - Flags missing purchase orders (unauthorized invoicing).
  - Flags missing goods receipts (billing before delivery verification).
  - Flags quantity variances where `invoiced_quantity > received_quantity` beyond user-specified tolerance %.
  - Flags price/amount variances where `invoiced_amount > po_amount` beyond monetary and percentage tolerances.
  - Verifies currency consistency across PO and invoice lines.

### 5.2 Duplicate Invoice & Payment Detection (`P2P_DUPLICATE_INVOICE_PAYMENT`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_duplicate_invoice_payment()`
- **Logic**:
  - Normalizes invoice identifiers (strips punctuation, whitespace, and leading zeroes).
  - Flags exact duplicates: Identical supplier, normalized invoice number, and gross amount.
  - Flags probable duplicate billing: Identical supplier and identical amount billed within a 14-day proximate date window under different invoice numbers.

### 5.3 Delegation of Authority Approval Verification (`P2P_MISSING_APPROVAL`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_missing_approval()`
- **Logic**:
  - Compares invoice amounts against organizational Delegation of Authority (DOA) thresholds (e.g. $1,000 / $5,000 / $25,000).
  - Verifies that approval events exist from authorized supervisor user IDs before invoice disbursement.

### 5.4 PO & Invoice Linkage / Supplier Mismatch (`P2P_PO_INVOICE_MISMATCH`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_po_invoice_mismatch()`
- **Logic**:
  - Flags invoices missing mandatory PO reference numbers where policy requires a PO.
  - Flags invalid PO numbers that do not exist in the approved PO register.
  - Detects supplier mismatches where an invoice references a valid PO issued to a completely different vendor.

### 5.5 Financial Period Cut-Off Verification (`P2P_PERIOD_CUTOFF`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_period_cutoff_check()`
- **Logic**:
  - Identifies goods receipts accepted within the current accounting period where vendor invoices were delayed and billed in subsequent periods (unrecorded liabilities).
  - Flags invoices recorded before physical goods receipt or service completion.

### 5.6 Threshold Splitting Risk Signals (`P2P_THRESHOLD_SPLITTING`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_threshold_splitting()`
- **Logic**:
  - Identifies clusters of invoices or purchase orders to the same vendor occurring within 3-7 days whose individual amounts fall just below approval thresholds (e.g. $9,000 to $9,999 on a $10,000 approval limit).
  - Flags transactions as structured purchases intended to evade supervisory authorization.

### 5.7 Supplier Bank Account Change & Payment Proximity (`P2P_BANK_CHANGE_TIMING`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_bank_change_payment_timing()`
- **Logic**:
  - Detects payments released within 14 days of an update to the supplier's bank account or remittance details.
  - Mitigates business email compromise (BEC) and unauthorized diversion of enterprise disbursements.

### 5.8 Supplier Master Duplication Review (`P2P_SUPPLIER_MASTER_DUPLICATION`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_supplier_master_duplication()`
- **Logic**:
  - Identifies colliding vendor master profiles sharing identical Tax IDs / EINs, IBANs, or bank account numbers.
  - Performs normalized name fuzzy matching to flag duplicate supplier records that bypass volume discount tiers.

### 5.9 Reproducible Stratified Sampling (`P2P_SAMPLE_SELECTION`)
- **Location**: `app/audit/rules/p2p_rules.py` -> `run_reproducible_sample()`
- **Logic**:
  - Partitions population into high-value stratum (top 30%) and representative random stratum.
  - Uses fixed pseudo-random seeds (e.g. `seed=42`) ensuring external regulatory examiners can reproduce the exact same audit sample.

### 5.10 ITGC & Segregation of Duties Review (`ITGC_SOD_CONFLICT`)
- **Location**: `app/audit/rules/itgc_and_governance.py` -> `run_itgc_sod_analysis()`
- **Logic**:
  - Enforces toxic entitlement pairs (PO Creation + Invoice Approval, Vendor Master Maintenance + Payment Release, Goods Receipt + Invoice Entry).
  - Scans employee termination lists against active ERP user accounts to flag retained access.
  - Flags dormant accounts (>90 days without login).

### 5.11 Vendor Assurance & AI Governance
- **Location**: `app/audit/rules/itgc_and_governance.py` -> `run_vendor_assurance_review()`, `run_ai_governance_review()`
- **Logic**:
  - Audits critical vendors for valid SOC 1/2 Type II reports and expiration dates.
  - Audits corporate AI systems against NIST AI RMF and EU AI Act requirements (system owner, risk tier, monitoring plan).

---

## 6. Complete API Endpoint Catalog

The backend exposes 49 OpenAPI endpoints grouped by domain:

### Health & Diagnostics
- `GET /health`: Detailed status of Neon DB, pgvector, and Google Gemini LLM.
- `GET /ready`: Readiness probe for container orchestration.

### Authentication & Context
- `GET /api/auth/me`: Resolves current auditor identity, tenant organization, and active engagement.

### Audit Engagements
- `GET /api/engagements`: List audit engagements for current organization.
- `POST /api/engagements`: Create a new audit engagement with scope and period dates.
- `GET /api/engagements/{id}`: Detailed engagement status and summary.

### Evidence & Datasets
- `GET /api/evidence`: List evidence files (PDF, DOCX, TXT) with SHA-256 integrity hashes.
- `POST /api/evidence/upload`: Secure upload, hashing, fragment extraction, and Neon PGVector indexing.
- `GET /api/datasets`: List tabular datasets (CSV, XLSX) with row and column counts.
- `POST /api/datasets/upload`: Ingest ledger file, profile columns, and detect canonical P2P fields.
- `GET /api/datasets/{id}/preview`: Preview profiled columns, inferred data types, and sample rows.

### Risk and Control Matrix (RCM)
- `GET /api/rcm/criteria`: List COSO, IIA, SOX audit criteria.
- `GET /api/rcm/risks`: List identified procurement and financial risks.
- `GET /api/rcm/controls`: List preventive and detective controls.
- `GET /api/rcm/coverage`: Compute control coverage ratio and identify testing gaps.

### Deterministic Tests & Execution
- `GET /api/tests/templates`: List pre-seeded audit rule templates (3-way match, duplicate invoice, missing approval).
- `GET /api/tests/runs`: List historical test execution records.
- `POST /api/tests/run`: Execute deterministic test against ingested dataset rows and persist exceptions.

### Exceptions & Triage
- `GET /api/exceptions`: List identified exceptions filtered by severity or disposition.
- `GET /api/exceptions/{id}`: Retrieve detailed observed vs expected values and evidence ties.
- `POST /api/exceptions/{id}/disposition`: Record auditor disposition (Confirmed, False Positive, Accepted Risk) with rationale.

### Findings & Reporting
- `GET /api/findings`: List formal audit findings with 5-element structure.
- `POST /api/findings`: Convert confirmed exception into an audit finding.

### Workpapers & Claim Verification
- `GET /api/workpapers`: List synthesized audit workpapers.
- `POST /api/workpapers/generate`: Synthesize comprehensive workpaper via Google Gemini with verified evidence citations.
- `GET /api/workpapers/{id}/versions`: Retrieve immutable version history of workpaper.

### Remediation Tracking
- `GET /api/remediation`: List corrective action plans with due dates and owners.
- `POST /api/remediation`: Create remediation action linked to a finding.
- `PATCH /api/remediation/{id}`: Update action progress, management comment, or due date.
- `POST /api/remediation/{id}/verify`: Formal auditor sign-off and verification closure.
- `POST /api/remediation/{id}/evidence`: Attach evidence file proving control remediation.

### Executive Dashboard & Continuous Auditing
- `GET /api/dashboard/kpis`: Real-time aggregated metrics from Neon PostgreSQL.
- `GET /api/continuous/rules`: List recurring monitoring rules and cron schedules.
- `POST /api/continuous/rules`: Schedule a recurring rule sweep.
- `POST /api/continuous/rules/{id}/trigger`: Trigger an immediate continuous monitoring sweep.

### Governance & ITGC
- `GET /api/governance/sod-matrix`: Retrieve standard Segregation of Duties toxic pairs.
- `POST /api/governance/itgc/sod`: Run user role conflict and terminated leaver access check.
- `POST /api/governance/vendor-assurance`: Review vendor portfolio for valid SOC 1/2 coverage.
- `POST /api/governance/ai-governance`: Audit corporate AI systems against NIST AI RMF.
- `GET /api/governance/sop-maps`: Retrieve SOP process maps stored in Neon.
- `POST /api/governance/sop-maps`: Persist SOP process map flowchart.
- `GET /api/governance/audit-logs`: Query immutable event log for compliance reviews.

---

## 7. Frontend Architecture & User Interface

The React frontend (`auditor-copilot-frontend/`) is structured as an integrated enterprise workspace:
- **`SideBar.jsx`**: Exposes the four main operational navigation groups across 16 dedicated views:
  1. Audit Assurance Lifecycle (Dashboard, Engagements, Evidence & Datasets, RCM, Tests & Execution, Exceptions & Triage, Workpapers, Findings & Reports, Remediation Tracking, Continuous Auditing)
  2. Governance & Review (ITGC & SoD Review, Vendor Assurance, AI Governance Audit, SOP Process Maps)
  3. AI Copilot Assistant (Interactive Copilot Advisory Chat)
  4. Configuration & System (Workspace & System Settings: active tenant, database schema, PGVector status, and Gemini model engine)
- **`ModelConfigsidebar.jsx`**: Exposes Google Gemini configuration, active model selection (`gemini-2.5-flash`), and real-time persistence assurance indicators (Neon PostgreSQL connection, `audit_copilot` schema, PGVector status).
- **`api.js`**: Centralized API client connecting React components to the FastAPI endpoints with standardized error handling and offline fallbacks.
- **`layoutPage.jsx`**: Coordinates seamless tab switching, header status indicators, and dynamic view rendering.

---

## 8. Verification & Test Execution

### 8.1 Backend Unit & Functional Tests
Run deterministic audit rules test suite:
```bash
PYTHONPATH=auditor-copilot-backend python auditor-copilot-backend/tests/test_audit_rules.py -v
```
All 14 test cases pass covering 3-way match variances, duplicate detection, approval thresholds, PO linkage mismatch, period cutoff, split purchases, bank change timing, supplier master deduplication, sampling, SoD conflicts, leaver access, vendor assurance, and AI governance.

Run Neon PostgreSQL integration test suite:
```bash
PYTHONPATH=auditor-copilot-backend python auditor-copilot-backend/tests/test_neon_integration.py
```
Verifies health check reporting, collection naming isolation, vector storage operations, and memory clear endpoints.

### 8.2 Frontend Lint & Production Build
Run ESLint check:
```bash
npm --prefix auditor-copilot-frontend run lint
```
Result: `0 errors` (exit code 0).

Run Vite production build:
```bash
npm --prefix auditor-copilot-frontend run build
```
Result: Builds production bundle into `dist/` with zero errors.

