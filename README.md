# AI-Assisted Course Waitlist

CourseFlow is a course enrollment and FIFO waitlist demo with a custom React dashboard, a Python/FastAPI service, and SQLite persistence. It was built with an AI-assisted engineering workflow for the Charles Schwab AI Engineering Assessment.

## Features

- Responsive React interface with enrollment overview, class roster, FIFO waitlist, activity log, and offering settings.
- Learner enrollment and dropping through the dashboard.
- Prerequisite eligibility controls and validation.
- FIFO waitlist promotion that skips learners who are currently ineligible.
- SQLite persistence across application restarts.
- Automated service and API tests.
- GitHub Actions workflow for Python tests and React production build.

## Requirements

Install these before running the application:

- **Python 3.11 or newer**
- **Node.js 20 or newer**, including npm
- Git (to pull the latest code)

Verify the installations in PowerShell:

```powershell
python --version
node --version
npm --version
```

If `python` is not recognized, install Python and enable **Add Python to PATH**. If `node` or `npm` is not recognized, install the current Node.js LTS release and reopen PowerShell.

## Run locally on Windows

The React dashboard and FastAPI backend are two separate processes. **Keep both terminals running.** The React page uses the backend API to save enrollments; opening the frontend alone is not enough.

### 1. Get the latest code

Open PowerShell and move to the repository root (the folder containing `api.py` and `README.md`):

```powershell
cd C:\Users\sknet\source\ai-assisted-course-waitlist
git pull origin main
```

If your repository is in a different folder, use that folder instead.

### 2. Install Python dependencies

Run this from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, you can either allow scripts for this terminal with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again, or skip activation and use `\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `\.venv\Scripts\python.exe -m uvicorn api:app --reload`.

### 3. Start the backend API

In the same terminal, from the repository root:

```powershell
python -m uvicorn api:app --reload
```

Keep this terminal open. You should see Uvicorn report that it is running on `http://127.0.0.1:8000`.

Verify the API in a browser:

- Health check: http://127.0.0.1:8000/api/health — should return JSON with `"status":"ok"`.
- API documentation: http://127.0.0.1:8000/docs
- Current enrollment state: http://127.0.0.1:8000/api/state

If the health check does not work, fix the backend startup error before continuing.

### 4. Install and start the React frontend

Open a **second PowerShell terminal**. Keep the backend terminal running. Then run:

```powershell
cd C:\Users\sknet\source\ai-assisted-course-waitlist\frontend
npm install
npm run dev
```

Use your actual repository path if it differs. Wait for Vite to print its local URL, normally `http://localhost:5173/`, and open that URL in your browser.

**Use the React URL at `http://localhost:5173/` for the CourseFlow experience.** The old Streamlit app is a separate fallback and does not display the React dashboard.

### 5. Verify enrollment works

The initial demo state has a capacity of 3 and no enrolled learners. The default eligible learners are Ava, Noah, Mia, Liam, Zoe, and Ethan.

1. Open **http://localhost:5173/**.
2. In the **Quick Action** card, choose **Ava** from the learner dropdown.
3. Click **Process enrollment**.
4. Wait for the success message. The **Confirmed** count should increase from 0 to 1, Ava should appear in the enrolled roster, and the Activity log should record the action.
5. Enroll Noah and Mia. The confirmed count should reach 3.
6. Enroll Liam. The course is full, so Liam should be added to the FIFO waitlist instead of the confirmed roster.
7. Drop an enrolled learner from the roster. A seat should open and the earliest eligible waitlisted learner should be promoted.
8. Refresh the browser. Enrollment and waitlist data should remain because it is stored in SQLite.

If a learner is rejected because prerequisites are not met, open **Manage prerequisites**, mark that learner eligible, save, and try again. If you change eligibility for someone already waiting, use **Refresh queue** in the Waitlist view to re-evaluate promotion.

### 6. Run automated tests

Open a third terminal in the repository root and activate the virtual environment:

```powershell
cd C:\Users\sknet\source\ai-assisted-course-waitlist
.\.venv\Scripts\Activate.ps1
python -m pytest -v
```

The tests use temporary state where applicable and should not require manually clearing your local demo database.

### 7. Build the frontend

From the frontend folder:

```powershell
cd frontend
npm run build
```

A successful build creates the production bundle under `frontend/dist/`.

## Troubleshooting

### The page opens, but enrollment does not appear

- Confirm that the **FastAPI terminal is still running** and has no errors.
- Open http://127.0.0.1:8000/api/health and confirm it returns `{"status":"ok","database":"course_waitlist.db"}`.
- Confirm you opened **http://localhost:5173/**, not the Streamlit app or a stale production page.
- Choose a learner from the dropdown, then click **Process enrollment** and check the toast message.
- Open http://127.0.0.1:8000/api/state after clicking. If the learner is absent from `enrolled` and `waitlist`, the POST request did not persist; check the API terminal for a traceback.
- Try a hard refresh with **Ctrl+F5** after both processes are running.
- If the page shows “Failed to fetch” or stays on “Connecting to your enrollment workspace…”, the frontend cannot reach the backend. Start the API first and retry.
- If the API returns an error, copy the full error from the API terminal and browser message before troubleshooting further.

### `npm` is not recognized

Install Node.js 20+ (LTS), close and reopen PowerShell, then rerun `node --version` and `npm --version`.

### Port 8000 or 5173 is already in use

Stop the other process using that port, or configure a free port consistently. The Vite proxy is currently configured for the backend at `http://127.0.0.1:8000`.

### Reset the local demo data

Stop the backend with Ctrl+C. In the repository root, delete `course_waitlist.db` only if you want to discard your saved demo enrollments, waitlist, capacity, and activity. Restart the API to create a fresh database. **This is destructive and not required for normal use.**

## Project layout

- `frontend/` — React + Vite UI.
- `api.py` — FastAPI endpoints and SQLite state persistence.
- `course_waitlist/` — core enrollment service and CLI demonstration.
- `tests/` — service and API tests.
- `docs/DESIGN.md` — design, invariants, policy, and tradeoffs.
- `docs/AI_USAGE.md` — AI use record and verification checklist.
- `docs/LIMITATIONS.md` — scoped risks and follow-up items.

## Demo assumptions and limitations

The dashboard uses fictional demo learners and a single sample offering. Prerequisite eligibility is configurable for demonstration. SQLite is suitable for this local assessment demo; this is not a production multi-user registration platform with authentication, authorization, or multi-host transaction coordination.

## AI-assisted engineering disclosure

ChatGPT was used as the primary implementation assistant for task decomposition, code drafting, test design, UI drafting, and documentation. Before submission, run the application and tests locally, inspect the changes, and update `docs/AI_USAGE.md` with actual verification evidence.
