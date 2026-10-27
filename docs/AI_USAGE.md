# AI Prompt and Use Record

This record describes AI assistance used while implementing the Course Waitlist assessment. It distinguishes implemented work from verification that still must be performed by the candidate.

## Engineering prompts used

**Prompt 1 — Core service and assessment deliverables (summary of the request)**

> Review the Course Waitlist AI-Assisted Engineering Assessment. Implement one bounded offering with enrollment, dropping, prerequisite validation, and FIFO waitlist promotion. State assumptions. Prevent duplicate requests and over-capacity state. Add focused automated tests for available/full capacity, duplicates, FIFO, prerequisite failure, invalid/repeated drops, and concurrency where practical. Include a design specification, AI use record, setup instructions, verification evidence, and limitations.

**AI response summary:** Use a small Python service with an in-memory offering, explicit result codes, a prerequisite callback, a documented skip-and-retain policy for ineligible waitlisted learners, focused tests, and a deterministic CLI demonstration.

**Decision:** Accepted and implemented in `course_waitlist/service.py`, `course_waitlist/__main__.py`, and `tests/test_service.py`. The candidate must independently review the behavior and run the tests.

**Prompt 2 — Follow-up interactive dashboard request (summary)**

> Add a more distinctive React UI and a backend API so the enrollment flow can be demonstrated interactively.

**AI response summary:** Add React/Vite UI, FastAPI endpoints, a SQLite snapshot store, API tests, and a CI workflow.

**Decision:** Implemented as an optional extension in `frontend/`, `api.py`, `tests/test_api.py`, and `.github/workflows/verify.yml`. This extension is outside the assessment's explicit scope boundary, which says not to add a frontend or a new database unless the starter requires it. The core service remains separate and is the relevant assessment deliverable.

**Prompt 3 — Repository/documentation review against the attached assessment (summary)**

> Compare the repository with the assessment and complete pending work.

**AI response summary:** The core business rules and many tests were already present, but setup/design/limitations documentation needed to state the service boundary and assessment scope more clearly. Additional tests were added for invalid learner IDs and refresh behavior when the queue is full.

**Decision:** Accepted with edits. Updated `README.md`, `docs/DESIGN.md`, `docs/LIMITATIONS.md`, and `tests/test_service.py`. The local verification record is intentionally not marked complete without actual output.

## Engineering decisions and verification approach

| Suggestion or decision | Status | Reason / verification |
|---|---|---|
| Keep business rules independent of UI, HTTP, and storage | Accepted | `EnrollmentService` is framework-independent and uses an in-memory `CourseOffering`. |
| Use explicit result codes | Accepted | Expected outcomes such as duplicate enrollment, prerequisite failure, and invalid drop are represented distinctly. |
| Skip ineligible waitlisted learners but retain them in queue order | Accepted | Documented in `docs/DESIGN.md`; covered by service tests. |
| Serialize core transitions with a process-local lock | Accepted with limitation | Protects one service instance within one process; it is not a distributed concurrency strategy. |
| Fail closed if eligibility lookup raises | Accepted with caveat | Prevents accidental enrollment, but production code should distinguish an upstream outage from ineligibility. |
| Add React/API/SQLite for an interactive demonstration | Implemented as an optional extension | Helpful for demonstration, but beyond the attached assessment's stated scope. Do not treat these extras as required assessment work. |

## Assessment acceptance-criteria map

1. **Eligible enrollment with available capacity:** covered by `test_enrolls_when_capacity_available`.
2. **Full course adds an eligible learner once; duplicates are rejected:** covered by `test_full_capacity_adds_eligible_learner_to_waitlist_once` and `test_duplicate_enrollment_request_does_not_duplicate_enrolled_record`.
3. **Drop promotes the earliest eligible learner:** covered by `test_drop_promotes_earliest_eligible_waitlisted_learner_fifo`.
4. **Ineligible learner is not enrolled/promoted; skip-and-retain policy:** covered by `test_prerequisite_failure_does_not_mutate_state`, `test_ineligible_learner_is_skipped_and_retained_when_promotion_scans`, and `test_refresh_waitlist_skips_and_retains_ineligible_learner`.
5. **Invalid requests and repeated drops preserve state:** covered by `test_invalid_learner_ids_are_rejected_without_mutation` and `test_invalid_and_repeated_drops_do_not_change_state`.
6. **Concurrency where practical:** covered by `test_concurrent_duplicate_requests_preserve_uniqueness_and_capacity` for the in-memory service's lock.
7. **AI use and independent verification:** this record describes prompts, decisions, affected files, and the required verification steps. Candidate review and local execution remain necessary.

## Verification record

Do not mark a command as passed until it has actually been run. Record the environment and actual results here.

- [ ] Python version recorded using `python --version`.
- [ ] Dependencies installed using `python -m pip install -r requirements.txt`.
- [ ] Core tests executed using `python -m pytest -v`.
- [ ] CLI demo executed using `python -m course_waitlist`.
- [ ] Optional API tests and frontend build checked if the optional extension is retained.
- [ ] Candidate reviewed the service, invariants, tests, and documented eligibility policy.
- [ ] Date, exact command output, and any fixes discovered are recorded below.

### Actual local test evidence

**Status: Not yet verified in the candidate's local environment.** No local test result is claimed here. After running the commands, replace this note with the date, Python version, exact command, and actual pass/fail summary. CI results may be recorded separately and do not replace local verification.

## Independent review notes

The candidate should be able to explain why a duplicate request does not mutate state, why a drop can promote one learner, how an ineligible learner is skipped without being removed, and why the lock protects only a single process. Review AI-generated changes before submission and do not include credentials or secrets in prompts or submitted records.
