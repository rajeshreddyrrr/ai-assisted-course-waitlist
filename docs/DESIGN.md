# Design Specification

## Service boundary
`EnrollmentService` owns enrollment, dropping, and waitlist promotion for exactly one `CourseOffering`. The offering stores capacity plus ordered learner-ID lists for enrolled learners and the waitlist. The React/Vite dashboard calls the FastAPI layer, which invokes the enrollment service and persists state to SQLite. The legacy `app.py` Streamlit dashboard remains available as a fallback; business rules remain in the service.

## Data and results
- `CourseOffering.capacity`: non-negative integer.
- `CourseOffering.enrolled`: ordered list of currently enrolled learner IDs.
- `CourseOffering.waitlist`: FIFO list of waiting learner IDs.
- `Result`: stable result code, message, requested learner ID, and optional promoted learner ID.

Learner IDs are trimmed and must be non-empty strings. The core service is process-local and in memory; the Streamlit UI persists its state through a local SQLite database (`course_waitlist.db`).

## Eligibility assumption
An injected `eligible(learner_id)` callback represents the prerequisite rule. The default callback allows all learners for the service demo. The UI provides a fictional set of learners and allows the presenter to configure which learners satisfy prerequisites. A false result rejects direct enrollment and does not add the learner to the waitlist. If an accepted waitlisted learner becomes ineligible before promotion, that learner is skipped and retained in the original queue position. Promotion continues to the earliest currently eligible learner. `refresh_waitlist()` can retry promotion after eligibility changes if a seat is available.

If the eligibility callback raises an exception, the service fails closed and treats the learner as ineligible for that operation. A production service should distinguish provider failures from a confirmed prerequisite failure.

## Invariants
1. Enrolled count never exceeds capacity.
2. A learner appears at most once across enrolled and waitlist state.
3. A learner cannot be both enrolled and waitlisted.
4. Enrollment and promotion require eligibility.
5. Waitlist order is preserved among learners not promoted; the first currently eligible learner is selected.
6. Invalid requests and unsuccessful drops do not mutate state.

## State transitions

### Enroll
1. Validate and normalize learner ID.
2. Return a clear duplicate result if already enrolled or waitlisted.
3. Check prerequisites; reject if not eligible.
4. Enroll immediately if a seat exists; otherwise append once to the waitlist.

### Drop
1. Validate learner ID.
2. If not enrolled, return `NOT_ENROLLED` without modifying state.
3. Remove the learner.
4. If a seat is available, scan the waitlist from the front. Promote the first eligible learner and retain ineligible entries.

### Explicit waitlist refresh
`refresh_waitlist()` permits a caller to retry promotion after external prerequisite changes. It promotes at most one learner when a seat is available.

## UI behavior
The React dashboard displays offering metrics, lets a presenter change capacity and prerequisite eligibility, processes enroll/drop actions, shows the current roster and FIFO waitlist, and records recent activity. FastAPI persists demo state in the local SQLite database (`course_waitlist.db`) so it survives app restarts. The UI is for demonstrating the service, not a production identity or registration system.

## Concurrency and persistence
A reentrant lock serializes API state read-modify-write operations inside a single Python process, and the service lock protects transitions. These locks do not coordinate multiple API processes or hosts. SQLite stores the latest state between restarts; a production multi-instance service would need database transactions and stronger concurrency controls. A persistent implementation would need database transactions, unique constraints, and suitable row/queue locking. A production implementation should test concurrency against its actual persistence mechanism.

## Tradeoffs
- One offering only; no catalog, identity integration, or database.
- Lists provide understandable FIFO behavior but are not optimized for very large queues.
- Eligibility is injected rather than implemented as a configurable policy engine.
- Ineligible waitlisted learners are skipped but retained.
- Expected business outcomes use result codes; the in-memory implementation has no external infrastructure.
