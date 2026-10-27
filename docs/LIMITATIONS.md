# Limitations and Follow-up Risks

## In-scope limitations
1. **Single offering:** The service models one course offering only; no catalog or multi-term registration is included.
2. **In-memory core state:** `EnrollmentService` is an in-memory service. State does not persist across process restarts unless a caller supplies a persistence layer.
3. **Process-local locking:** A reentrant lock protects transitions in one process. It does not coordinate separate processes, containers, or hosts.
4. **Eligibility callback errors:** Exceptions fail closed and appear as prerequisite failures. A production service should distinguish provider outages from confirmed ineligibility.
5. **Queue scale:** List scans and removals are O(n), appropriate for a bounded assessment but not necessarily very large queues.
6. **No identity or access control:** Authentication, authorization, learner identity verification, and a production audit trail are outside scope.

## Optional demonstration extensions
The repository also contains a CourseFlow dashboard/API and local SQLite persistence added during follow-up work. These demonstrate the service interactively, but the attached assessment explicitly says not to add a frontend or a new database unless the starter requires it. Treat those layers as optional extras rather than evidence required to satisfy the assessed service slice. The core service and its tests should remain independently runnable.

## Verification limitation
The candidate must run the documented tests and CLI demo locally, inspect the implementation, and record actual command output, date, and Python version in `docs/AI_USAGE.md` before submission. A successful CI run is useful supporting evidence but does not replace local review or the candidate's independent verification.
