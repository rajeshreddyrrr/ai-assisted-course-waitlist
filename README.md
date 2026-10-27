# AI-Assisted Course Waitlist

CourseFlow is a course enrollment and FIFO waitlist demo with a custom React dashboard, a Python/FastAPI service, and SQLite persistence. It was built with an AI-assisted engineering workflow for the Charles Schwab AI Engineering Assessment.

## Features

- Responsive React interface with enrollment overview, class roster, FIFO waitlist, activity log, and offering settings.
- Learner enrollment and dropping through the dashboard.
- Prerequisite eligibility controls and validation.
- FIFO waitlist promotion that skips learners who are currently ineligible.
- SQLite persistence across application restarts.
- Service-level automated tests for acceptance criteria and concurrency.

## Requirements

- Python 3.11+
- Node.js 20+ and npm

## Run locally

Open a terminal in the repository root.

### 1. Start the API

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn api:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

### 2. Start the React UI

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL Vite prints, usually `http://localhost:5173`. Keep both terminals running while using the app.

The SQLite database `course_waitlist.db` is created in the repository root on first API request. It stores capacity, prerequisite eligibility, enrolled learners, waitlist order, and recent activity.

### 3. Run tests

From the repository root with the Python virtual environment active:

```powershell
python -m pytest -v
```

The earlier Streamlit dashboard remains available as a fallback via `python -m streamlit run app.py`, but the recommended showcase experience is the React UI.

## Project layout

- `frontend/` — React + Vite UI.
- `api.py` — FastAPI endpoints and SQLite state persistence.
- `course_waitlist/` — core enrollment service and CLI demonstration.
- `tests/` — service acceptance tests.
- `docs/DESIGN.md` — design, invariants, policy, and tradeoffs.
- `docs/AI_USAGE.md` — AI use record and verification checklist.
- `docs/LIMITATIONS.md` — scoped risks and follow-up items.

## Demo assumptions and limitations

The dashboard uses fictional demo learners and a single sample offering. Prerequisite eligibility is configurable for demonstration. SQLite is suitable for this local assessment demo; this is not a production multi-user registration platform with authentication, authorization, or multi-host transaction coordination.

## AI-assisted engineering disclosure

ChatGPT was used as the primary implementation assistant for task decomposition, code drafting, test design, UI drafting, and documentation. Before submission, run the application and tests locally, inspect the changes, and update `docs/AI_USAGE.md` with actual verification evidence.
