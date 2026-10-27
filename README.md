# AI-Assisted Course Waitlist

A bounded Python implementation of enrollment, dropping, and FIFO waitlist promotion for one course offering, prepared for the Course Waitlist AI-Assisted Engineering Assessment.

## Assessment scope

The core deliverable is the framework-independent service in `course_waitlist/service.py`. It implements capacity checks, prerequisite validation, duplicate prevention, dropping, and FIFO promotion. Ineligible waitlisted learners are skipped during promotion but retained in their relative queue position. The tests focus on the assessment's acceptance criteria.

An optional CourseFlow dashboard/API is also present from follow-up development. The attached assessment says not to add a frontend or a new database unless the starter requires them, so the dashboard is not required to demonstrate the assessed service.

## Requirements

- Python 3.11+
- pip

## Setup and run the tests

Run these commands from the repository root:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -v
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again, or use the virtual environment's Python executable directly.

## Run the service demonstration

From the repository root, with the virtual environment active:

```powershell
python -m course_waitlist
```

The demonstration creates an in-memory offering, processes a few enrollment requests, drops a learner, and prints the resulting enrolled and waitlist state. It does not require a database.

## Optional dashboard/API

The optional React/FastAPI demonstration is not required by the assessment. If you want to run it, follow the dashboard-specific instructions in the repository history or start the API and frontend as separate processes. Its SQLite file is separate from the core in-memory service.

## Project layout

- `course_waitlist/service.py` — enrollment, drop, and waitlist-promotion rules.
- `course_waitlist/__main__.py` — deterministic command-line demonstration.
- `tests/test_service.py` — focused acceptance and concurrency tests.
- `tests/test_api.py` — optional API integration tests for the dashboard extension.
- `docs/DESIGN.md` — service boundary, assumptions, invariants, and tradeoffs.
- `docs/AI_USAGE.md` — prompts, decisions, and verification record.
- `docs/LIMITATIONS.md` — scoped risks and follow-up items.

## AI-assisted engineering disclosure

AI was used for task decomposition, code drafting, test design, and documentation. Review the implementation and test output independently. The AI-use record must include actual verification evidence; do not claim local tests passed until they have been run.
