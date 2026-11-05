# Plate Inspection System (BIT-PLATE-CV-1.0)

Quality Inspection Web Application for Metal Plate Product **P-PLATE01**.

---

## 1. Project Overview & Scope
This application provides automated quality inspection for synthetic images of metal plates (**P-PLATE01**). When an operator uploads a photo, the system validates the image, invokes the pretrained logistic regression model (**BIT-PLATE-CV-1.0**), displays the classification (**Normal** or **Defective**) with confidence and defect probability, permanently persists the immutable inspection record, allows supervisors to append audit reviews, and provides honest evaluation benchmarking across the 60 labeled development samples.

### Operational Scope & Limitations:
- **Product Scope:** Demonstration system designed for fictional product **P-PLATE01** on 256×256 synthetic development images with centered plate framing and dark border.
- **Binary Assessment Only:** Evaluates only binary classification (**Normal** / **Defective**). Does not determine defect type, spatial location, depth, root cause, or time-to-failure.
- **Uncalibrated Confidence:** The confidence score represents the raw sigmoid model probability and must not be interpreted as an empirical probability of hardware safety or real-world reliability.
- **Human Oversight Required:** Human supervisor review is strictly separated and recorded in an append-only audit log.

---

## 2. Architecture & Tech Stack

```
plate-inspection/
├── backend/
│   ├── apps/
│   │   ├── accounts/         # Custom User model, JWT authentication, roles & permissions
│   │   ├── inspections/      # Inspection model, upload validation, prediction persistence
│   │   ├── reviews/          # Append-only Review table, supervisor audit trail
│   │   └── evaluation/       # Benchmark evaluation runner & model integrity endpoint
│   ├── config/               # Django settings, URLs, WSGI, ASGI
│   ├── services/
│   │   ├── image_validator.py    # 5-rule upload validation pipeline
│   │   ├── model_service.py      # Thin wrapper around Model/inference.py
│   │   ├── integrity_service.py  # SHA-256 file checksum verification
│   │   └── metrics_service.py    # Confusion matrix & recall computation
│   ├── tests/                # 8 comprehensive pytest suites
│   └── manage.py
├── frontend/
│   ├── static/               # Industrial CSS, JS API client, icons
│   └── templates/            # HTML5 + Bootstrap 5 dashboards
├── Model/
│   ├── classifier.npz        # Pretrained 17-feature logistic regression weights
│   ├── inference.py          # Authoritative preprocessing & predict(path) contract
│   └── requirements.txt      # numpy, Pillow
├── Samples/
│   ├── images/               # 60 labeled synthetic images (30 Normal, 30 Defective)
│   └── labels.csv            # relative_path, label (0=Normal, 1=Defective)
├── Validation/
│   ├── not_an_image.jpg      # Text file pretending to be JPEG
│   ├── corrupt_image.png     # Truncated PNG (fails full pixel load)
│   └── too_small.png         # 32x32 image (below 64x64 minimum dimension)
├── scripts/
│   ├── create_admin.py       # Admin initialization
│   ├── seed_users.py         # Demo user seeding (operator1, supervisor1, admin1)
│   ├── run_evaluation.py     # Standalone evaluation command
│   └── capture_browser_demo.py # Playwright automated UI verification
├── SHA256SUMS.txt            # Authoritative SHA-256 checksums of model & datasets
├── project_graph.json        # Graph Engineering dependency graph
├── loop_log.md               # Loop Engineering continuous iteration log
├── docker-compose.yml        # PostgreSQL + Django production containerization
├── Makefile                  # Automation targets
├── requirements.txt          # Python application dependencies
└── README.md
```

### Technology Stack:
- **Backend:** Python 3.12+, Django 5.1, Django REST Framework, SimpleJWT, django-cors-headers, NumPy, Pillow, python-dotenv.
- **Database:** PostgreSQL (with SQLite development fallback).
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Bootstrap 5, Bootstrap Icons. No heavy frontend frameworks (no React/Next.js).
- **Testing:** Pytest, pytest-django, Playwright.

---

## 3. Role-Based Access Control (RBAC)

The system enforces role permissions at the backend API level using DRF permission classes:

| Role | Permissions & Capabilities |
| :--- | :--- |
| **Operator** | Log in, upload plate photos, inspect results, view own historical inspections. Attempting to review returns **403 Forbidden**. Attempting to view another operator's inspection returns **403 Forbidden**. |
| **Supervisor** | View all operator inspections, record append-only reviews (`CONFIRMED` / `OVERRIDDEN`), view evaluation metrics dashboard, run fresh benchmarks. |
| **Admin** | All supervisor capabilities + manage system users (`/api/users/`) and verify SHA-256 model checksums (`/api/model/integrity/`). |

Unauthenticated requests to protected endpoints return **401 Unauthorized**.

---

## 4. Setup & Installation

### Prerequisites
- Python 3.12 or higher
- Git

### 1. Clone & Create Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key configuration parameters in `.env`:
```ini
DEBUG=True
SECRET_KEY=your-secure-django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,testserver

# Database options: 'sqlite' or 'postgresql'
DB_ENGINE=sqlite
DB_NAME=plate_inspection_db
DB_USER=plate_user
DB_PASSWORD=plate_secure_password
DB_HOST=localhost
DB_PORT=5432

# Image Validation Limits
MIN_IMAGE_DIM=64
MAX_IMAGE_SIZE_MB=10
```

### 4. Database Migrations
```bash
python manage.py makemigrations accounts inspections reviews evaluation
python manage.py migrate
```

### 5. Seed Demonstration Users
```bash
python scripts/seed_users.py
```
This provisions three demo accounts:
- **Operator:** `operator1` / `Operator123!`
- **Supervisor:** `supervisor1` / `Supervisor123!`
- **Admin:** `admin1` / `Admin123!`

---

## 5. Running the Application

### Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open your browser to: **`http://127.0.0.1:8000`**

### Running via Docker Compose (PostgreSQL + App)
```bash
docker-compose up --build
```

---

## 6. Testing & Quality Verification

### Run Complete Pytest Suite
```bash
pytest backend/tests/ -v
```
The test suite validates:
1. `test_upload_validation.py`: Clean rejection of `not_an_image.jpg`, `corrupt_image.png`, `too_small.png` with error codes (`NOT_AN_IMAGE`, `CORRUPT_IMAGE`, `TOO_SMALL`) and zero completed inspections stored.
2. `test_prediction_persistence.py`: Valid plate upload persists all 4 fields + `model_version`.
3. `test_model_service_parity.py`: Zero drift between `model_service.predict_plate` and `Model/inference.py`.
4. `test_role_permissions.py`: 401 unauthenticated, 403 operator isolation, 403 operator review restriction.
5. `test_review_append_only.py`: Append-only review history, immutability of completed inspections, prevention of review deletions.
6. `test_evaluation_metrics.py`: 2x2 confusion matrix orientation, recall formula, explicit tracking of missing/failed images, FN=0 limitation statement.
7. `test_integrity_verification.py`: 100% SHA-256 checksum matching on clean files; detection of tampered copies.
8. `test_end_to_end.py`: Full operational lifecycle from login to upload, prediction, review, and evaluation.

### Run Model Evaluation Management Command
```bash
python manage.py run_evaluation
```
Console output:
```
BIT-PLATE-CV-1.0 EVALUATION REPORT
Model Version: BIT-PLATE-CV-1.0
Total Samples: 60
Successful:    60
Failed:        0

2x2 CONFUSION MATRIX (rows = actual, columns = predicted):
------------------------------------------------------------
                     | Pred Normal (0)    | Pred Defective (1)
------------------------------------------------------------
Actual Normal (0)    | 30                 (TN) | 0                  (FP)
Actual Defective (1) | 0                  (FN) | 30                 (TP)
------------------------------------------------------------
Defect Recall (TP / (TP+FN)):  100.00%
Overall Accuracy:              100.00%
Precision:                     100.00%

LIMITATION STATEMENT:
no false negatives occurred, but 60 synthetic development images cannot establish real-world reliability.
```

### Run Model Inference CLI Directly
```bash
python Model/inference.py Samples/images/inspection_001.png
```
Output:
```json
{"predicted_class": 0, "confidence": 0.9826, "defect_probability": 0.0174, "model_version": "BIT-PLATE-CV-1.0"}
```

---

## 7. API Reference

| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/auth/login/` | POST | Public | Authenticate user, returns access & refresh JWT tokens + user profile |
| `/api/auth/refresh/` | POST | Public | Refresh expired access token |
| `/api/auth/logout/` | POST | Authenticated | Blacklist refresh token & clear session |
| `/api/auth/me/` | GET | Authenticated | Retrieve current user profile and role |
| `/api/inspections/` | POST | Authenticated | Upload image (multipart), validate, run inference, persist record |
| `/api/inspections/` | GET | Authenticated | List inspections (Operator sees own; Supervisor/Admin sees all) |
| `/api/inspections/{id}/` | GET | Authenticated | Retrieve inspection ticket details (Operator restricted to own) |
| `/api/inspections/{id}/reviews/` | POST | Supervisor/Admin | Append supervisor audit review (`CONFIRMED`/`OVERRIDDEN`) |
| `/api/inspections/{id}/reviews/` | GET | Authenticated | List all append-only reviews on inspection |
| `/api/evaluation/` | GET | Supervisor/Admin | Retrieve latest benchmark evaluation report |
| `/api/evaluation/run/` | POST | Supervisor/Admin | Trigger fresh benchmark evaluation across all 60 samples |
| `/api/model/integrity/` | GET | Admin | Verify SHA-256 checksums against `SHA256SUMS.txt` |
| `/api/users/` | GET/POST | Admin | List system users or register new user with role |

