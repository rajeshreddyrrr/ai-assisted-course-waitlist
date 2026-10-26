# AI-Assisted Course Waitlist

A bounded course-offering service demonstrating enrollment, dropping, prerequisite checks, and FIFO waitlist promotion. Built with an AI-assisted engineering workflow for the Charles Schwab AI Engineering Assessment.

## Scope and policy

- One course offering with a fixed capacity.
- In-memory state; no database or frontend.
- Each learner can be enrolled or waitlisted only once.
- Learners must satisfy the prerequisite rule to enroll or join the waitlist.
- When a seat opens, promote the earliest **currently eligible** learner.
- Ineligible learners encountered in the waitlist are skipped but retained in their queue position.
- A lock serializes state changes among threads in this process.

## Requirements

- Python 3.11+
- `pytest`

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m course_waitlist
```

The CLI runs a small demonstration. No external services or credentials are required.

## Project layout

- `course_waitlist/` — service and demonstration CLI.
- `tests/` — acceptance-focused automated tests.
- `docs/DESIGN.md` — design, invariants, policy, and tradeoffs.
- `docs/AI_USAGE.md` — prompt/use record and verification checklist.
- `docs/LIMITATIONS.md` — scoped risks and follow-up items.

## Design summary

The service returns structured result objects for expected business outcomes. Learners who fail prerequisites are rejected without changing state. Duplicate requests do not create duplicate records. Dropping a learner who is not enrolled returns a clear result without mutating state.

This is an assessment-sized in-memory implementation, not a production registration platform. Read the design and limitations documents before extending it.

## AI-assisted engineering disclosure

ChatGPT was used as the primary implementation assistant for task decomposition, code drafting, test design, and documentation. The AI-use log records the prompts and decisions used for this implementation. Before submission, run the commands above, inspect the changes, and update verification statuses to reflect tests and review actually performed.
