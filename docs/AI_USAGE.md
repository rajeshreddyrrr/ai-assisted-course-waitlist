# AI Prompt and Use Record

This record documents the AI-assisted work on this repository. Add actual follow-up prompts, results, and local test evidence as the work progresses. Do not mark a local test as passed until it has been run.

## Engineering prompt

**Prompt used**

> Review the Course Waitlist AI-Assisted Engineering Assessment. Implement one bounded offering with enrollment, dropping, prerequisite validation, and FIFO waitlist promotion in a minimal runnable project. State assumptions. Ineligible learners must not be enrolled or promoted. Prevent duplicate requests and over-capacity state. Add focused automated tests for available/full capacity, duplicates, FIFO, prerequisite failure, invalid/repeated drops, and concurrency where practical. Include a design specification, setup instructions, AI use record, limitations, and verification evidence. Keep the core enrollment service bounded; a React demonstration UI and local SQLite persistence were added later at the user's explicit request.

**AI response summary**
- Initially use a small Python service and in-memory store because the repository contained no starter implementation; later expose the service through FastAPI and persist its snapshot in SQLite for the requested UI.
- Represent expected outcomes with explicit result codes.
- Serialize mutations with a lock for thread safety within one process.
- Skip ineligible waitlisted learners but retain them in the queue, documenting the policy consistently.
- Add acceptance-focused service tests, then API integration tests, a React/Vite UI, CI checks, and separate implementation, design, AI-use, and limitations documentation.

## Suggestion decisions

| AI suggestion | Decision | Rationale / verification |
|---|---|---|
| Keep the core enrollment service independent of storage | Accepted | The service remains in-memory and framework-independent; FastAPI persists snapshots in SQLite at the API boundary for the requested local UI. |
| Use explicit result codes for expected outcomes | Accepted | Makes duplicate, prerequisite, and invalid-drop outcomes testable. |
| Skip ineligible waitlisted learners but retain them | Accepted | Allows the earliest currently eligible learner to be promoted while preserving skipped learners' relative queue position. Verify with the skip-and-retain test. |
| Serialize operations with a process-local lock | Accepted with limitation | Protects the API read-modify-write flow inside one process, not multiple workers/hosts. SQLite is suitable for this local assessment demo; production needs stronger transaction and concurrency controls. |
| Treat eligibility callback exceptions as ineligible | Accepted with caveat | Fails closed, but conflates provider failure with prerequisite failure. Documented as a production limitation. |

## Verification record

Fill in after running locally:
- [ ] Python version recorded: `python --version`
- [ ] Dependencies installed: `python -m pip install -r requirements.txt`
- [ ] Automated tests executed: `python -m pytest -q`
- [ ] Exact test outcome and pass/fail count recorded here.
- [ ] CLI demonstration executed: `python -m course_waitlist`
- [ ] Code and tests inspected against the documented policy.
- [ ] Invalid inputs, duplicates, and skipped-ineligible promotion behavior manually reviewed.

### Local test evidence

**Status: Not yet run in the candidate's local environment.** Update this section with actual command output, date, Python version, and fixes made. Do not report tests as passing until confirmed.

## Independent review notes

The assessment expects evidence of independent verification, not simply a claim that AI wrote the code. Before submission, review the service and tests, run them locally, record any defects found and changes made, and ensure you can explain the invariants, ineligible-learner policy, and concurrency boundary.


## Follow-up UI and API implementation

At the user's request, the project was extended with a React/Vite dashboard, FastAPI endpoints, SQLite persistence, API integration tests, and a GitHub Actions workflow that runs Python tests and builds the frontend. The capacity update and waitlist refresh operations now promote eligible learners until the offering is full or no eligible waitlisted learner remains.

**Verification caveat:** GitHub Actions was triggered for these changes. Record its final result and run the documented commands locally before submission. Do not describe the UI/API integration as verified until both CI jobs and a local end-to-end walkthrough pass.
