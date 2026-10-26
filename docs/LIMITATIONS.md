# Limitations and Follow-up Risks

1. **In-memory persistence:** Enrollment and waitlist state is lost when the process exits.
2. **Single-process locking:** The lock protects threads sharing this service instance, not multiple processes, containers, or hosts. Persistent multi-instance deployments need database transactions and constraints.
3. **Eligibility provider failure:** Callback exceptions fail closed but are represented as prerequisite failures. A production API should distinguish a provider outage from a confirmed prerequisite failure.
4. **Prerequisite changes:** Waitlisted learners are rechecked during promotion. The service offers `refresh_waitlist()` for a caller to trigger promotion after eligibility changes.
5. **Single offering and local IDs:** No catalog, learner identity service, authentication, authorization, audit trail, or multi-offering isolation is implemented.
6. **Operational API:** The service exposes Python methods and a demonstration CLI only. HTTP endpoints are intentionally out of scope.
7. **Scale:** List scans and removals are O(n), appropriate for this bounded assessment but not necessarily for very large queues.
8. **Verification:** The candidate must run the tests and demo locally and record actual evidence before submission.
