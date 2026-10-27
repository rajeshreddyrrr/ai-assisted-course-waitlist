# Design Specification

## Scope and service boundary
The assessed feature is a bounded service for one course offering: enrollment, dropping, and FIFO waitlist promotion. `EnrollmentService` owns these rules and remains independent of the UI, HTTP framework, and persistence. It operates on a `CourseOffering` object in memory. The repository also contains an optional CourseFlow demonstration UI/API added during follow-up work; those are convenience layers, not required by the assessment's stated scope. The assessment says not to add a frontend or a new database unless the starter requires them.

## Data model and results
- `CourseOffering.capacity`: non-negative integer.
- `CourseOffering.enrolled`: ordered list of enrolled learner IDs.
- `CourseOffering.waitlist`: FIFO list of waiting learner IDs.
- `Result`: stable result code, human-readable message, requested learner ID, and optional promoted learner ID.
- Learner IDs are trimmed; blank or non-string values are rejected.

## Prerequisite and waitlist assumptions
The service receives an `eligible(learner_id)` callback representing the prerequisite rule. If no callback is supplied, all learners are considered eligible. An ineligible learner is rejected from direct enrollment and is not added to the waitlist. If a learner who was eligible when waitlisted becomes ineligible before promotion, the service skips that learner and retains them in their original relative queue position. It continues scanning for the earliest currently eligible learner. The policy is consistent for promotion during drop and explicit `refresh_waitlist()`.

If the eligibility callback raises an exception, the service fails closed and treats that learner as ineligible for that operation. A production service should distinguish an eligibility-provider outage from a confirmed prerequisite failure.

## Invariants
1. Enrolled count never exceeds capacity.
2. A learner appears at most once across enrolled and waitlist state.
3. A learner cannot be both enrolled and waitlisted.
4. Enrollment and promotion require eligibility.
5. Waitlist order is preserved among learners not promoted; the first currently eligible learner is selected.
6. Invalid requests and unsuccessful drops do not mutate enrollment or waitlist state.
7. A drop promotes at most one learner because it opens one seat.

## State transitions

### Enroll
1. Validate and normalize learner ID.
2. Return a clear duplicate result if already enrolled or waitlisted.
3. Check prerequisites; reject if ineligible.
4. Enroll immediately if a seat exists; otherwise append once to the waitlist.

### Drop
1. Validate learner ID.
2. If learner is not enrolled, return `NOT_ENROLLED` without mutating state.
3. Remove the learner.
4. Scan the waitlist from the front and promote the first currently eligible learner, retaining skipped ineligible entries.

### Explicit waitlist refresh
`refresh_waitlist()` retries promotion after eligibility changes. It promotes at most one learner when a seat is available. It returns `None` when no eligible learner can be promoted or no seat is available.

## Concurrency and persistence
The core service uses a reentrant lock to serialize transitions within one process. It stores its state in memory and does not claim persistence across process restarts. The optional demo API layer stores a snapshot in a local SQLite file and uses a process-local lock; this does not coordinate multiple API processes or hosts. Neither approach is a production multi-instance registration architecture. Database transactions, uniqueness constraints, and a persistence-specific concurrency test would be required for a production implementation.

## Tradeoffs and limitations
- One offering only; no catalog, identity integration, authentication, or authorization.
- Lists provide understandable FIFO behavior but scans/removals are O(n).
- Eligibility is injected as a callback, not implemented as a configurable policy engine.
- Ineligible waitlisted learners are skipped but retained.
- Core service tests exercise the business rules independently of the optional demo layers.
