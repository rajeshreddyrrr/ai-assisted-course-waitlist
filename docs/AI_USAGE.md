# AI Prompt and Use Record

This record documents the AI-assisted work on this repository. Add actual follow-up prompts, results, and local test evidence as the work progresses. Do not mark a local test as passed until it has been run.

## Engineering prompt

**Prompt used**

> Review the Course Waitlist AI-Assisted Engineering Assessment. Implement one bounded offering with enrollment, dropping, prerequisite validation, and FIFO waitlist promotion in a minimal runnable project. State assumptions. Ineligible learners must not be enrolled or promoted. Prevent duplicate requests and over-capacity state. Add focused automated tests for available/full capacity, duplicates, FIFO, prerequisite failure, invalid/repeated drops, and concurrency where practical. Include a design specification, setup instructions, AI use record, limitations, and verification evidence. Do not build a frontend, database, or unrelated registration features.

**AI response summary**
- Use a small Python service and in-memory store because the repository contained no starter implementation.
- Represent expected outcomes with explicit result codes.
- Serialize mutations with a lock for thread safety within one process.
- Skip ineligible waitlisted learners but retain them in the queue, documenting the policy consistently.
- Add acceptance-focused tests and separate implementation, design, AI-use, and limitations documentation.

## Suggestion decisions

| AI suggestion | Decision | Rationale / verification |
|---|---|---|
| Use an in-memory service rather than add a database | Accepted | Matches the assessment fallback and scope boundaries. Verify repository contents and run the service. |
| Use explicit result codes for expected outcomes | Accepted | Makes duplicate, prerequisite, and invalid-drop outcomes testable. |
| Skip ineligible waitlisted learners but retain them | Accepted | Allows the earliest currently eligible learner to be promoted while preserving skipped learners' relative queue position. Verify with the skip-and-retain test. |
| Serialize operations with a process-local lock | Accepted with limitation | Protects threads sharing one service instance, not distributed processes. Review the concurrency test and document the persistence limitation. |
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
