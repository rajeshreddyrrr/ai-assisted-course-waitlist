# AI-Assisted Course Waitlist

A bounded Python implementation of enrollment, dropping, and FIFO waitlist promotion for one course offering, prepared for the Course Waitlist AI-Assisted Engineering Assessment.

## Assessment scope

The core deliverable is the framework-independent service in `course_waitlist/service.py`. It implements capacity checks, prerequisite validation, duplicate prevention, dropping, and FIFO promotion. Ineligible waitlisted learners are skipped during promotion but retained in their relative queue position. The tests focus on the assessment's acceptance criteria.

A Streamlit UI and an optional React/FastAPI dashboard are also included as demonstrations. The assessment does not require a frontend or a new database unless the starter requires them.

## Requirements

- Python 3.11+
- pip
- Node.js/npm for the combined React/FastAPI commands below

## Setup

Run from the repository root in PowerShell:

```powershell
python --version
node --version
npm --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm install
npm install --prefix frontend
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again, or use the virtual environment's Python executable directly.

## Start the React frontend and Python backend together

From the repository root, with the Python virtual environment activated, run:

```powershell
npm start
```

This starts both the FastAPI backend at `http://127.0.0.1:8000` and the React/Vite frontend at `http://localhost:5173` in one terminal. Keep the terminal running while using the app. Press `Ctrl+C` to stop both processes. API docs are available at `http://127.0.0.1:8000/docs`.

If you change dependencies, rerun `npm install` at the root and/or `npm install --prefix frontend` as appropriate.

## Run the automated tests

From the repository root, with the Python virtual environment activated, run:

```powershell
npm test
```

This runs `python -m pytest -v` and prints each test's status (PASSED/FAILED) plus the final summary. The command exits with a non-zero status if any test fails.

You can also run the Python test command directly:

```powershell
python -m pytest -v
```

## Run the web UI (Streamlit)

**The Streamlit interface is an alternative UI** and runs separately from the React/FastAPI dashboard. From the repository root:

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`. Keep the terminal running while using the UI.

The Streamlit interface includes learner creation, enrollment and drop actions, capacity settings, prerequisite eligibility controls, the enrolled roster, waitlist, and activity log. New learners are saved in SQLite and are not marked eligible automatically unless you confirm their prerequisites.

## Project layout

- `course_waitlist/service.py` — enrollment, drop, and waitlist-promotion rules.
- `course_waitlist/__main__.py` — deterministic command-line demonstration.
- `app.py` — Streamlit web UI.
- `api.py` and `frontend/` — optional FastAPI/React dashboard.
- `package.json` — root-level `npm start` and `npm test` scripts.
- `tests/test_service.py` — focused acceptance and concurrency tests.
- `tests/test_api.py` — API integration tests for the dashboard extension.
- `docs/DESIGN.md` — service boundary, assumptions, invariants, and tradeoffs.
- `docs/AI_USAGE.md` — prompts, decisions, and verification record.
- `docs/LIMITATIONS.md` — scoped risks and follow-up items.

## Run the service demonstration (CLI, not a web UI)

```powershell
python -m course_waitlist
```

This runs a deterministic in-memory demonstration and prints results in the terminal. It does not open a browser.

## AI-assisted engineering disclosure

AI was used for task decomposition, code drafting, test design, and documentation. Review the implementation and test output independently. The AI-use record must include actual verification evidence; do not claim local tests passed until they have been run.
