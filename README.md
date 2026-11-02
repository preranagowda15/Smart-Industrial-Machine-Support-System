# Manufacturing Manual Assistant

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django 5.2](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![REST Framework](https://img.shields.io/badge/DRF-3.18-red.svg)](https://www.django-rest-framework.org/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.28-orange.svg)](https://pymupdf.readthedocs.io/)
[![Tests: 16/16 Passed](https://img.shields.io/badge/Tests-16%2F16%20Passed-brightgreen.svg)]()

A full-stack, production-grade **Retrieval-Augmented Generation (RAG)** application built with Python, Django, Django REST Framework, PyMuPDF, and vector search. It enables manufacturing engineers to ask technical questions about specific machinery and receive verifiable answers grounded strictly and exclusively in official PDF operation and maintenance manuals.

---

## 1. Core Objectives & Safety Invariants

1. **Role-Based Authorization**: Distinct roles for **Administrator**, **Engineer**, and **Supervisor** enforced on backend REST endpoints.
2. **Machine-Level Retrieval Isolation**: Strict filtering (`where={"machine_id": selected_machine_id}`) applied directly inside the vector database query engine. No cross-machine data leakage.
3. **Multi-Document Retrieval**: Seamlessly retrieves complementary evidence across multiple manuals (e.g. HP-200 Operations and Maintenance manuals).
4. **Verifiable Citations**: Returns document name, revision, exact 1-based physical PDF page number, extracted passage snippet, and a direct browser link (`/media/manuals/<pdf>#page=<page>`).
5. **Zero Hallucination Guarantee**: When evidence is missing or below relevance thresholds, the system returns:  
   `"The available manuals do not contain enough information to answer this question."` and persists status as `INSUFFICIENT_EVIDENCE`.
6. **Administrator-Only Ingestion**: Non-administrators (Engineers/Supervisors) attempting manual uploads receive `HTTP 403 Forbidden`.

---

## 2. Architecture & Modular Structure

```
manufacturing-manual-assistant/
backend/
    config/              # Django settings, URLs, WSGI, ASGI
    apps/
        accounts/        # User model, roles, JWT & session auth, permissions
        machines/        # Machine registry models and APIs
        manuals/         # Manuals, DocumentChunks, ingestion pipeline
        assistant/       # RAG question submission endpoint (/api/assistant/ask/)
        history/         # QuestionHistory, SourceReference models and APIs
        dashboard/       # Supervisor APIs and frontend template views
    services/
        pdf_processor.py      # PyMuPDF 1-based page extraction
        chunking_service.py   # Overlapping passage chunking & metadata preservation
        embedding_service.py  # Dense subword vector generation & API fallback
        vector_store.py       # Persistent vector database with SQL metadata filter
        retrieval_service.py  # Machine-isolated retrieval engine
        rag_service.py        # Strict prompt orchestration & evidence thresholding
        citation_service.py   # Hallucination rejection & PDF link generation
frontend/
    templates/           # Bootstrap 5 HTML templates (base, login, assistant, etc.)
    static/
        css/style.css    # Professional dark navy & clean industrial SaaS theme
        js/              # Modular JavaScript (app.js, assistant.js, manuals.js, etc.)
data/
    Manuals/             # Official machine manuals (HP-200, AC-90)
    machine_manual_index.csv
vector_db/               # Persistent vector collection storage
media/manuals/           # Served PDF documents for clickable page navigation
scripts/
    seed_data.py         # Automated database seeding & indexing
    ingest_manuals.py    # CLI manual importer
    create_admin.py      # Quick admin creation utility
tests/
    test_role_permissions.py   # Mandatory Test 1: Engineer upload denial
    test_machine_isolation.py  # Mandatory Test 2: Machine retrieval isolation
    test_rag_grounding.py      # Strict evidence grounding & citation verification
    test_end_to_end.py         # Full 5 end-to-end competition scenarios
project_graph.json       # Graph Engineering dependency graph
requirements.txt
docker-compose.yml
Makefile
```

---

## 3. Demo Credentials

| Role | Username | Password | Key Permissions |
|---|---|---|---|
| **Administrator** | `admin_demo` | `AdminDemo!2026` | Upload PDF manuals, register machines, full control |
| **Engineer** | `engineer_demo` | `EngineerDemo!2026` | Select machine, ask questions, view own history |
| **Supervisor** | `supervisor_demo` | `SupervisorDemo!2026` | Read-only audit trail, review flagged/unanswered queries |

---

## 4. Quick Start & Execution

### Option A: Local Python Environment

1. **Activate virtual environment**:
   ```powershell
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # macOS / Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply database migrations**:
   ```bash
   python manage.py makemigrations accounts machines manuals history dashboard
   python manage.py migrate
   ```

4. **Seed demo users & index official manuals**:
   ```bash
   python scripts/seed_data.py
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

6. Open your browser at **`http://127.0.0.1:8000/`**.

---

### Option B: Docker Compose (Full PostgreSQL)

```bash
docker compose up --build -d
docker compose exec web python scripts/seed_data.py
```

---

## 5. Automated Verification & Test Suite

All 16 unit, integration, and scenario tests pass:

```bash
python manage.py test tests
```

### Verified Test Cases:
- **Mandatory Test 1 (`test_role_permissions.py`)**: Engineer attempts manual upload; server rejects with `HTTP 403 Forbidden` and zero records created.
- **Mandatory Test 2 (`test_machine_isolation.py`)**: Ingests chunks for `M-HP200` and `M-AC90`. Search on `M-HP200` returns 0 `M-AC90` chunks; search on `M-AC90` returns 0 `M-HP200` chunks.
- **Scenario 1 (`test_end_to_end.py`)**: Supported Question ("What does E17 mean?") -> Retrieves `HP-OPS-01`, generates grounded answer, cites Page 2 with URL `#page=2`.
- **Scenario 2 (`test_end_to_end.py`)**: Multi-Document Question ("What should be inspected during maintenance, and what operating limits should be checked?") -> Retrieves from both `HP-OPS-01` and `HP-MNT-01`, cites both.
- **Scenario 3 (`test_end_to_end.py`)**: Machine Isolation -> Select `HP-200`, ask `AC-90` question -> Returns `INSUFFICIENT_EVIDENCE`.
- **Scenario 4 (`test_end_to_end.py`)**: Unsupported Question -> Asks about supplier pump price -> Returns `INSUFFICIENT_EVIDENCE` and persists in supervisor queue.
- **Scenario 5 (`test_end_to_end.py`)**: Role Security -> Engineer upload returns 403; Supervisor can access query logs.

---

## 6. End-to-End Demonstration Scenarios Guide

In the web interface:

1. **Sign in as Engineer** (`engineer_demo` / `EngineerDemo!2026`).
2. **Scenario 1 — Supported Alarm Question**:
   - Machine: `HP-200`
   - Ask: `"What does E17 mean?"`
   - **Result**: Explains Main Ram Proportional Valve failure, diagnostic steps, cites `HP-OPS-01` Page 2. Click **"Open PDF Page"** to view page 2 in the browser PDF viewer.
3. **Scenario 2 — Multi-Document Question**:
   - Machine: `HP-200`
   - Ask: `"What should be inspected during maintenance, and what operating limits should be checked?"`
   - **Result**: Cites both `HP-OPS-01` (250 bar limit, 120 L oil) and `HP-MNT-01` (daily inspections, weekly column greasing, filter intervals).
4. **Scenario 3 — Machine Isolation**:
   - Machine: `HP-200`
   - Ask: `"What is the AC-90 rated discharge pressure?"`
   - **Result**: Returns `"The available manuals do not contain enough information to answer this question."` (Status: `INSUFFICIENT_EVIDENCE`).
5. **Scenario 4 — Unsupported Question**:
   - Machine: `HP-200`
   - Ask: `"What is the pump replacement price from the supplier?"`
   - **Result**: Returns insufficient evidence.
6. **Scenario 5 — Supervisor & Admin Roles**:
   - Sign in as **Supervisor** (`supervisor_demo` / `SupervisorDemo!2026`): Visit **Supervisor Overview** to review analytics and the flagged unanswered queries from Scenario 3 & 4.
   - Sign in as **Administrator** (`admin_demo` / `AdminDemo!2026`): Visit **Machine Manuals** to upload new manuals or register equipment.
