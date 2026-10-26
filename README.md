# AI-Assisted Course Waitlist

A bounded course-offering service with a polished Streamlit dashboard, enrollment, dropping, prerequisite checks, and FIFO waitlist promotion. Built with an AI-assisted engineering workflow for the Charles Schwab AI Engineering Assessment.

## Features

- Interactive dashboard with capacity, enrollment, open-seat, and waitlist metrics.
- Learner enrollment and dropping through a graphical interface.
- Configurable prerequisite eligibility for demo learners.
- FIFO waitlist promotion, including skipping currently ineligible waitlisted learners.
- Activity log and class roster.
- Service-level automated tests for acceptance criteria and concurrency.

## Requirements

- Python 3.11+
- Dependencies in `requirements.txt`

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. To run the service tests in a separate terminal:

```bash
python -m pytest -q
python -m course_waitlist
```

## Project layout

- `app.py` — interactive CourseFlow dashboard with SQLite persistence.
- `course_waitlist/` — enrollment service and CLI demonstration.
- `tests/` — acceptance-focused automated tests.
- `docs/DESIGN.md` — design, invariants, policy, and tradeoffs.
- `docs/AI_USAGE.md` — prompt/use record and verification checklist.
- `docs/LIMITATIONS.md` — scoped risks and follow-up items.

## Demo assumptions and limitations

The dashboard uses a small set of fictional demo learners. Prerequisite eligibility is toggled in the sidebar to demonstrate acceptance and promotion behavior. The UI persists capacity, eligibility, enrollment, waitlist, and recent activity in a local SQLite file named `course_waitlist.db` in the project root. Keep this file locally; it is created automatically on first launch. The service lock protects threads within one process only; this is not a production multi-user registration platform.

## AI-assisted engineering disclosure

ChatGPT was used as the primary implementation assistant for task decomposition, code drafting, test design, UI drafting, and documentation. Before submission, run the application and tests locally, inspect the changes, and update `docs/AI_USAGE.md` with actual verification evidence.
