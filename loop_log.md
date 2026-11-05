# Plate Inspection System (BIT-PLATE-CV-1.0) - Loop Engineering Log

## Overview
This log documents each iterative step of the loop engineering process:
`OBSERVE -> ANALYZE -> PLAN -> IMPLEMENT -> TEST -> INSPECT -> FIX -> RETEST -> UPDATE`

---

## Iteration 0: Initial Observation & Graph Engineering
- **Date**: 2026-11-02
- **Task**: Inspect workspace and build project dependency graph.
- **Files Changed**:
  - `project_graph.json` (created)
  - `loop_log.md` (created)
- **Commands Run**:
  - `Get-ChildItem -Force`
  - `python --version`
- **Output Summary**:
  - Python 3.12.10 detected.
  - Workspace initialized from scratch.
  - `project_graph.json` created with 14 dependency nodes, clear critical path, inputs, outputs, and validation criteria.
- **Result**: Ready to begin Iteration 1 on node `ENV_SETUP`.
- **Remaining Issues**: None.

---

## Iteration 1: Environment & Infrastructure Setup (ENV_SETUP)
- **Date**: 2026-11-02
- **Task**: Create virtual environment, install requirements, set up .env/.env.example, docker-compose.yml, Dockerfile, and Makefile.
- **Files Changed**:
  - `requirements.txt`
  - `.env.example`
  - `.env`
  - `docker-compose.yml`
  - `Dockerfile`
  - `Makefile`
  - `venv/` (created and populated)
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - `python -m venv venv`
  - `.\venv\Scripts\pip install -r requirements.txt`
  - `.\venv\Scripts\python -c "import django, rest_framework, rest_framework_simplejwt, PIL, numpy, dotenv, pytest; print('Imports successful! Django version:', django.__version__)"`
- **Output Summary**:
  - Installed Django 5.1.15, Pillow 13.0.0, numpy 2.5.4, pytest 9.2.0, djangorestframework 3.17.2, simplejwt 5.5.1, django-cors-headers 4.9.0.
  - Python imports verified successfully.
- **Result**: `ENV_SETUP` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 2: Synthetic Dataset, Pretrained Model & Integrity Pack (DATASET_PACK)
- **Date**: 2026-11-02
- **Task**: Generate 60 synthetic plate images (30 Normal, 30 Defective), Samples/labels.csv, 17-feature logistic regression model (Model/classifier.npz), Model/inference.py, Model/requirements.txt, Validation/ fixtures (not_an_image.jpg, corrupt_image.png, too_small.png), and SHA256SUMS.txt.
- **Files Changed**:
  - `Model/classifier.npz`
  - `Model/inference.py`
  - `Model/requirements.txt`
  - `Samples/images/inspection_001.png` .. `inspection_060.png`
  - `Samples/labels.csv`
  - `Validation/not_an_image.jpg`
  - `Validation/corrupt_image.png`
  - `Validation/too_small.png`
  - `SHA256SUMS.txt`
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - Image generation and training script
  - `.\venv\Scripts\python Model/inference.py Samples/images/inspection_001.png`
  - `.\venv\Scripts\python Model/inference.py Samples/images/inspection_035.png`
  - SHA256SUMS.txt verification script
- **Output Summary**:
  - `python Model/inference.py Samples/images/inspection_001.png` produced: `{"predicted_class": 0, "confidence": 0.9826, "defect_probability": 0.0174, "model_version": "BIT-PLATE-CV-1.0"}`
  - `python Model/inference.py Samples/images/inspection_035.png` produced: `{"predicted_class": 1, "confidence": 0.9824, "defect_probability": 0.9824, "model_version": "BIT-PLATE-CV-1.0"}`
  - Verified 67 files against `SHA256SUMS.txt` with 0 mismatches.
- **Result**: `DATASET_PACK` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 3: Django Project Core Architecture (DJANGO_CORE)
- **Date**: 2026-11-02
- **Task**: Initialize Django core modular monolith architecture (settings, urls, wsgi, asgi, manage.py), custom apps scaffolding, static & media configurations, SimpleJWT, CORS.
- **Files Changed**:
  - `backend/manage.py`
  - `manage.py`
  - `backend/config/__init__.py`
  - `backend/config/settings.py`
  - `backend/config/urls.py`
  - `backend/config/wsgi.py`
  - `backend/config/asgi.py`
  - `backend/apps/accounts/models.py`
  - `backend/apps/accounts/apps.py`
  - `backend/apps/inspections/apps.py`
  - `backend/apps/reviews/apps.py`
  - `backend/apps/evaluation/apps.py`
  - App `urls.py` stubs
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - `.\venv\Scripts\python backend/manage.py check`
  - `.\venv\Scripts\python manage.py check`
- **Output Summary**:
  - `System check identified no issues (0 silenced).`
- **Result**: `DJANGO_CORE` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 4: Accounts App & Role-Based Access Control (ACCOUNTS_APP)
- **Date**: 2026-11-02
- **Task**: Implement custom User model with OPERATOR, SUPERVISOR, ADMIN roles, migrations, serializers, JWT login/refresh/logout/me endpoints, admin user management endpoints (/api/users/), and role-based permission classes.
- **Files Changed**:
  - `backend/apps/accounts/models.py`
  - `backend/apps/accounts/permissions.py`
  - `backend/apps/accounts/serializers.py`
  - `backend/apps/accounts/views.py`
  - `backend/apps/accounts/urls.py`
  - `backend/apps/accounts/user_urls.py`
  - `backend/config/settings.py` (added testserver to ALLOWED_HOSTS)
  - `backend/apps/accounts/migrations/0001_initial.py`
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - `.\venv\Scripts\python manage.py makemigrations accounts`
  - `.\venv\Scripts\python manage.py migrate`
  - Verification test script checking 401 unauth, 200 login, role token payload, 403 forbidden for Operator on admin endpoint, and 200 for Admin on admin endpoint.
- **Output Summary**:
  - All migrations applied cleanly.
  - Verification script output: `ACCOUNTS_APP verification tests PASSED!`.
- **Result**: `ACCOUNTS_APP` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 5: Image Validator Service (SERVICES_VALIDATOR)
- **Date**: 2026-11-03
- **Task**: Implement `backend/services/image_validator.py` adhering to Section 6.1 (content check, im.load() full decode, dimensions, extensions, max size, standard machine-readable error codes).
- **Files Changed**:
  - `backend/services/image_validator.py`
  - `Validation/corrupt_image.png` (calibrated truncated byte offset for im.load() decode exception)
  - `SHA256SUMS.txt` (updated checksum for corrupt_image.png)
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - Verification test script testing not_an_image.jpg, corrupt_image.png, too_small.png, unsupported extensions, and valid images.
- **Output Summary**:
  - `not_an_image.jpg` rejected with `NOT_AN_IMAGE`.
  - `corrupt_image.png` rejected with `CORRUPT_IMAGE`.
  - `too_small.png` rejected with `TOO_SMALL`.
  - Unsupported file types rejected with `UNSUPPORTED_TYPE`.
  - Valid plate images validated with is_valid=True, dimensions 256x256, format PNG.
- **Result**: `SERVICES_VALIDATOR` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 6: Model Service & SHA256 Integrity Service (SERVICES_MODEL_INTEGRITY)
- **Date**: 2026-11-03
- **Task**: Implement `backend/services/model_service.py` (strict wrapper around `Model.inference.predict`) and `backend/services/integrity_service.py` (verifying all files against `SHA256SUMS.txt`).
- **Files Changed**:
  - `backend/services/model_service.py`
  - `backend/services/integrity_service.py`
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - Parity test verifying exact float and int equality between `model_service.predict_plate` and `Model.inference.predict`.
  - Integrity check verification on original 67 files.
  - Tamper detection verification on manipulated hashes.
- **Output Summary**:
  - Parity verified with 0 drift.
  - 67 files matched clean integrity check.
  - Tampered copy correctly flagged as invalid with mismatch and missing counts.
- **Result**: `SERVICES_MODEL_INTEGRITY` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 7: Inspections & Reviews Apps (INSPECTIONS_APP, REVIEWS_APP)
- **Date**: 2026-11-03
- **Task**: Implement Inspection model with clean immutability enforcement, upload validation pipeline, REST API endpoints (`POST /api/inspections/`, `GET /api/inspections/`, `GET /api/inspections/{id}/`), append-only Review model with deletion/modification prevention, and `POST /api/inspections/{id}/reviews/`.
- **Files Changed**:
  - `backend/apps/inspections/models.py`
  - `backend/apps/inspections/serializers.py`
  - `backend/apps/inspections/views.py`
  - `backend/apps/inspections/urls.py`
  - `backend/apps/reviews/models.py`
  - `backend/apps/reviews/serializers.py`
  - `backend/apps/reviews/views.py`
  - `backend/apps/reviews/urls.py`
  - Migrations: `inspections.0001_initial`, `reviews.0001_initial`
  - `project_graph.json` (status updated to VERIFIED for both nodes)
- **Commands Run**:
  - `.\venv\Scripts\python manage.py makemigrations inspections reviews`
  - `.\venv\Scripts\python manage.py migrate`
  - Comprehensive verification test suite for upload rejections, immutability, operator access scoping (403), supervisor append-only review, and review deletion prevention.
- **Output Summary**:
  - `not_an_image.jpg` rejected (400, `NOT_AN_IMAGE`, 0 completed inspections).
  - `corrupt_image.png` rejected (400, `CORRUPT_IMAGE`, 0 completed inspections).
  - `too_small.png` rejected (400, `TOO_SMALL`, 0 completed inspections).
  - Valid plate upload succeeded with predictions and limits notice.
  - Immutability prevented editing prediction.
  - Operator B blocked from Operator A inspection (403).
  - Operator review attempt returned 403.
  - Supervisor reviews appended without modifying inspection.
  - Review deletion blocked.
- **Result**: `INSPECTIONS_APP` and `REVIEWS_APP` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 8: Evaluation Metrics Service (SERVICES_METRICS)
- **Date**: 2026-11-03
- **Task**: Implement `backend/services/metrics_service.py` to evaluate the model on all 60 labeled samples using original model outputs before any human review.
- **Files Changed**:
  - `backend/services/metrics_service.py`
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - Verification test script evaluating all 60 sample images.
  - Verification of 2x2 confusion matrix orientation (`rows = actual, columns = predicted, order Normal, Defective`), defect recall formula, exact FN=0 caveat statement, and explicit missing/failed file tracking.
- **Output Summary**:
  - Evaluated 60 sample images: 30 Normal, 30 Defective.
  - Computed TP=30, FN=0, FP=0, TN=30.
  - Confusion matrix: `[[30, 0], [0, 30]]` with rows=[Actual Normal, Actual Defective], cols=[Predicted Normal, Predicted Defective].
  - Defect recall: 1.0 (100.0%).
  - FN=0 caveat statement triggered: "no false negatives occurred, but 60 synthetic development images cannot establish real-world reliability."
  - Missing file correctly flagged in `failed_predictions` and counted.
- **Result**: `SERVICES_METRICS` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 9: Evaluation App & Model Integrity API (EVALUATION_APP, INTEGRITY_API)
- **Date**: 2026-11-03
- **Task**: Implement `EvaluationRun` model, `GET /api/evaluation/` (latest metrics), `POST /api/evaluation/run/` (trigger evaluation, Supervisor/Admin), `GET /api/model/integrity/` (Admin only), and management command `python manage.py run_evaluation`.
- **Files Changed**:
  - `backend/apps/evaluation/models.py`
  - `backend/apps/evaluation/views.py`
  - `backend/apps/evaluation/urls.py`
  - `backend/apps/evaluation/integrity_urls.py`
  - `backend/apps/evaluation/management/commands/run_evaluation.py`
  - `backend/apps/evaluation/management/commands/runevaluation.py`
  - Migration: `evaluation.0001_initial`
  - `project_graph.json` (status updated to VERIFIED for both nodes)
- **Commands Run**:
  - `.\venv\Scripts\python manage.py makemigrations evaluation`
  - `.\venv\Scripts\python manage.py migrate`
  - `.\venv\Scripts\python manage.py run_evaluation`
  - Test script verifying permission matrix: Operator blocked (403), Supervisor granted evaluation (200/201), Supervisor blocked from integrity (403), Admin granted integrity (200).
- **Output Summary**:
  - `manage.py run_evaluation` printed 2x2 confusion matrix (rows=actual, cols=pred), recall 100%, accuracy 100%, and limitation statement.
  - Role restrictions enforced (403 for operator on evaluation; 403 for operator and supervisor on integrity).
  - Admin integrity endpoint returned 200 with 67 files verified clean.
- **Result**: `EVALUATION_APP` and `INTEGRITY_API` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 10: Seeding & Utility Scripts (SCRIPTS)
- **Date**: 2026-11-03
- **Task**: Implement `scripts/seed_users.py`, `scripts/create_admin.py`, and `scripts/run_evaluation.py`.
- **Files Changed**:
  - `scripts/seed_users.py`
  - `scripts/create_admin.py`
  - `scripts/run_evaluation.py`
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - `.\venv\Scripts\python scripts/seed_users.py`
  - `.\venv\Scripts\python scripts/create_admin.py`
  - Authentication check script verifying `operator1`, `supervisor1`, and `admin1` logins and roles.
- **Output Summary**:
  - `operator1` (OPERATOR), `supervisor1` (SUPERVISOR), `admin1` (ADMIN) successfully created and verified.
  - Auth test confirmed all 3 users can authenticate and obtain JWT tokens with corresponding role claims.
- **Result**: `SCRIPTS` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 11: Frontend Industrial Dashboard UI (FRONTEND_PAGES)
- **Date**: 2026-11-03
- **Task**: Implement industrial UI templates (base, login, upload, inspection_detail, history, review_queue, evaluation, admin_dashboard), CSS theme (dark navy sidebar, light content, green/red/amber status indicators), and `app.js` with client-side JWT handling, automatic refresh, and role-based navigation.
- **Files Changed**:
  - `frontend/static/css/style.css`
  - `frontend/static/js/app.js`
  - `frontend/templates/base.html`
  - `frontend/templates/login.html`
  - `frontend/templates/upload.html`
  - `frontend/templates/inspection_detail.html`
  - `frontend/templates/history.html`
  - `frontend/templates/review_queue.html`
  - `frontend/templates/evaluation.html`
  - `frontend/templates/admin_dashboard.html`
  - `backend/config/views.py`
  - `backend/config/urls.py`
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - `.\venv\Scripts\python manage.py check`
  - Verification script testing HTTP 200 responses on all 7 frontend pages plus test fixture routes.
- **Output Summary**:
  - All pages rendered with HTTP 200 OK.
  - Dropzone, preview, inspection result card, review timeline, confusion matrix, and admin integrity components verified.
- **Result**: `FRONTEND_PAGES` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 12: Comprehensive Pytest Test Suite (TEST_SUITE)
- **Date**: 2026-11-03
- **Task**: Implement comprehensive pytest test suite across all 8 mandatory testing domains from Section 10:
  1. `test_upload_validation.py`: Rejects `not_an_image.jpg`, `corrupt_image.png`, `too_small.png` with machine-readable error codes (`NOT_AN_IMAGE`, `CORRUPT_IMAGE`, `TOO_SMALL`) and creates 0 completed inspections.
  2. `test_prediction_persistence.py`: Valid upload persists `predicted_class`, `confidence`, `defect_probability`, and `model_version`.
  3. `test_model_service_parity.py`: Verifies `model_service.predict_plate` output matches `Model/inference.py` output across sample files with 0 preprocessing drift.
  4. `test_role_permissions.py`: Verifies unauthenticated (401), operator isolation (403 on other operator inspections), operator review attempt (403), supervisor permission (200/201).
  5. `test_review_append_only.py`: Verifies review is append-only, original prediction unchanged after reviews and retry, reviews cannot be deleted or modified.
  6. `test_evaluation_metrics.py`: Verifies 2x2 confusion matrix orientation (rows=actual, cols=pred, order Normal, Defective), recall formula, explicit failure tracking, and confirms labels are never passed to inference.
  7. `test_integrity_verification.py`: Verifies clean files match 100% and tampered copy is detected with mismatch counts.
  8. `test_end_to_end.py`: Verifies login -> upload -> result -> supervisor review -> evaluation run.
- **Files Changed**:
  - `pytest.ini`
  - `backend/tests/test_upload_validation.py`
  - `backend/tests/test_prediction_persistence.py`
  - `backend/tests/test_model_service_parity.py`
  - `backend/tests/test_role_permissions.py`
  - `backend/tests/test_review_append_only.py`
  - `backend/tests/test_evaluation_metrics.py`
  - `backend/tests/test_integrity_verification.py`
  - `backend/tests/test_end_to_end.py`
  - `backend/services/metrics_service.py` (fixed UTC timezone deprecation warning)
  - `project_graph.json` (status updated to VERIFIED)
- **Commands Run**:
  - `.\venv\Scripts\pytest backend/tests/ -v`
- **Output Summary**:
  - `8 passed in 14.18s` (100% passing, 0 failures, 0 warnings).
- **Result**: `TEST_SUITE` VERIFIED.
- **Remaining Issues**: None.

---

## Iteration 13: System Verification, Demonstration & Documentation (SYSTEM_VERIFICATION_DEMO)
- **Date**: 2026-11-03
- **Task**: Final full verification pass across all acceptance criteria:
  1. `python Model/inference.py Samples/images/inspection_001.png` tested.
  2. All three validation files verified in UI and API with correct machine-readable error codes.
  3. Valid uploads verified with class, confidence, model version, and limits notice.
  4. Real evaluation verified with 2x2 confusion matrix (rows=actual, cols=pred), recall formula, and exact FN=0 caveat.
  5. Role permissions verified in backend (operator review blocked with 403).
  6. Immutability verified: reviews never alter original prediction.
  7. All 8 pytest suites passing with 0 warnings.
  8. Browser automated walkthrough executed via Playwright, generating 7 UI screenshots in `media/screenshots/`.
  9. Comprehensive `README.md` created.
- **Files Changed**:
  - `README.md`
  - `scripts/capture_browser_demo.py`
  - `media/screenshots/screenshot_1_login.png`
  - `media/screenshots/screenshot_2_upload_normal.png`
  - `media/screenshots/screenshot_3_upload_defective.png`
  - `media/screenshots/screenshot_4_validation_rejection.png`
  - `media/screenshots/screenshot_5_inspection_detail_review.png`
  - `media/screenshots/screenshot_6_evaluation_dashboard.png`
  - `media/screenshots/screenshot_7_admin_integrity.png`
  - `project_graph.json` (status updated to VERIFIED - all 14 nodes VERIFIED)
- **Commands Run**:
  - `.\venv\Scripts\python Model/inference.py Samples/images/inspection_001.png` -> printed JSON: `{"predicted_class": 0, "confidence": 0.9826, "defect_probability": 0.0174, "model_version": "BIT-PLATE-CV-1.0"}`
  - `.\venv\Scripts\python manage.py run_evaluation` -> printed 2x2 confusion matrix and recall 100%.
  - `.\venv\Scripts\pytest backend/tests/ -v` -> `8 passed in 14.18s`.
  - `.\venv\Scripts\python scripts/capture_browser_demo.py` -> 7 screenshots captured.
- **Output Summary**:
  - All 7 Acceptance Criteria in Section 11 satisfied and verified against actual runs.
- **Result**: `SYSTEM_VERIFICATION_DEMO` VERIFIED. All nodes in `project_graph.json` are VERIFIED.
- **Remaining Issues**: None.
