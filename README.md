# AI-Assisted Course Waitlist

A bounded Python implementation of enrollment, dropping, and FIFO waitlist promotion for one course offering, prepared for the Course Waitlist AI-Assisted Engineering Assessment.

## Assessment scope

The core deliverable is the framework-independent service in `course_waitlist/service.py`. It implements capacity checks, prerequisite validation, duplicate prevention, dropping, and FIFO promotion. Ineligible waitlisted learners are skipped during promotion but retained in their relative queue position. The tests focus on the assessment's acceptance criteria.

A Streamlit UI and an optional React/FastAPI dashboard are also included as demonstrations. The assessment does not require a frontend or a new database unless the starter requires them.

## Requirements

- Python 3.11+
- pip
- Node.js/npm only if running the optional React dashboard

## Setup

Run from the repository root in PowerShell:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again, or use the virtual environment's Python executable directly.

## Run the web UI (Streamlit)

**This is the simplest way to see the enrollment functionality in a browser.** From the repository root:

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

The Streamlit interface includes an **Add a learner** form in the left sidebar, enrollment and drop actions, capacity settings, prerequisite eligibility controls, the enrolled roster, waitlist, and activity log. New learners are saved in SQLite and are not marked eligible automatically; add them to the prerequisite-eligible list if they meet the course requirements. It stores its demonstration state in the local `course_waitlist.db` SQLite file.

If the browser page does not open automatically, copy the local URL from the terminal into your browser. Keep the terminal running while using the UI.

## Run the optional React/FastAPI dashboard

This is a separate UI from the Streamlit app. Start each process in a separate terminal.

Terminal 1 — API, from the repository root:

```powershell
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — React frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite development server forwards `/api` requests to the backend at `http://127.0.0.1:8000`. You can inspect the API at `http://127.0.0.1:8000/docs`. Both processes must remain running.

## Run tests

From the repository root:

```powershell
python -m pytest -v
```

## Run the service demonstration (CLI, not a web UI)

```powershell
python -m course_waitlist
```

This runs a deterministic in-memory demonstration and prints results in the terminal. It does not open a browser.

## Project layout

- `course_waitlist/service.py` — enrollment, drop, and waitlist-promotion rules.
- `course_waitlist/__main__.py` — deterministic command-line demonstration.
- `app.py` — Streamlit web UI.
- `api.py` and `frontend/` — optional FastAPI/React dashboard.
- `tests/test_service.py` — focused acceptance and concurrency tests.
- `tests/test_api.py` — optional API integration tests for the dashboard extension.
- `docs/DESIGN.md` — service boundary, assumptions, invariants, and tradeoffs.
- `docs/AI_USAGE.md` — prompts, decisions, and verification record.
- `docs/LIMITATIONS.md` — scoped risks and follow-up items.

## AI-assisted engineering disclosure

AI was used for task decomposition, code drafting, test design, and documentation. Review the implementation and test output independently. The AI-use record must include actual verification evidence; do not claim local tests passed until they have been run.
