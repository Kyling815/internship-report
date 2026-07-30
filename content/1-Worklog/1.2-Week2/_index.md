---
title: "Week 2 Worklog"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 1.2. </b> "
---

# Week 2 - Concurrency Control and Data Integrity

## Objectives

Within the five-member team, my Week 2 objective was to review the concurrency and data-integrity requirements that would affect multi-replica deployment. I supported the responsible backend and chat members by checking that idempotency, version checks, and database constraints were suitable for later Kubernetes scaling.

## My Contributions

| Status | My assigned contribution | Evidence basis |
|---|---|---|
| Completed | Analyzed concurrent writes across multiple backend pods. | `docs/architecture/concurrency-policy.md`. |
| Completed | Contributed deployment-oriented review notes to the optimistic and pessimistic UI policies. | `docs/architecture/concurrency-policy.md` and `docs/frontend/COMMAND_MUTATION_POLICY.md`. |
| Completed | Reviewed the backend member's database-backed idempotency path for candidate apply requests. | `backend/app/services/idempotency_service.py`, `backend/app/routers/jobs.py`, and migration `0004_idempotency_records.py`. |
| Completed | Reviewed version-gated workflow commands using `expectedVersion` for multi-pod behavior. | `backend/app/services/optimistic_concurrency.py`, `backend/app/services/workflow_commands.py`, and HR/Candidate routers. |
| Completed | Coordinated integration validation for chat retry and duplicate-write behavior with the chat member. | `chat-service/repositories/chatRepository.js` and `chat-service/tests/chatRepository.concurrency.test.js`. |
| Partially completed | Attached visible API screenshots and CI logs where available. | Evidence pending: I did not have a screenshot or GitHub Actions log artifact in the local evidence archive. |

## Technical Implementation

Concurrency control was implemented at the database and API-contract level:

- PostgreSQL unique constraints protect duplicate user, company, application, and idempotency records.
- `Idempotency-Key` is accepted for candidate application submission and selected workflow commands.
- Reusing the same idempotency key with the same payload replays the stored response.
- Reusing the same idempotency key with a different payload returns `409` with `idempotency_key_reused`.
- Mutable HR job and application commands require `expectedVersion`.
- Stale version updates return controlled `409 Conflict` responses.
- Chat retries use deterministic client message IDs and DynamoDB conditional write behavior to avoid duplicate logical messages.

Conflict flow:

{{< mermaid >}}
sequenceDiagram
  participant C as Client
  participant API as FastAPI backend pod
  participant DB as PostgreSQL
  C->>API: POST /jobs/{id}/apply + Idempotency-Key
  API->>DB: reserve scoped idempotency record
  alt new request
    API->>DB: insert application, documents, history
    API->>DB: complete idempotency record
    API-->>C: 200/201 application response
  else exact replay
    DB-->>API: completed stored response
    API-->>C: stored response + Idempotency-Replayed
  else payload mismatch or duplicate business conflict
    API-->>C: 409 Conflict
  end
{{< /mermaid >}}

## Problems and Solutions

| Problem | Root cause | Resolution | Status |
|---|---|---|---|
| Duplicate registration or company creation could surface as uncontrolled database errors. | Unique constraints existed or were needed, but error translation had to be explicit. | Integrity errors are rolled back and translated into `409 Conflict`. | Completed |
| Candidate apply can be retried by browser/network clients. | A second request may reach another backend pod before the first response is received. | Scoped idempotency records persist request hash and response data. | Completed |
| HR workflow updates can become stale when two users act on the same job/application. | Plain updates do not know whether the client saw the latest row version. | Commands require `expectedVersion` and use conditional updates. | Completed |
| Chat retries can duplicate realtime messages. | Socket retries and REST retries can re-send the same logical message. | Chat repository uses deterministic message identity and skips duplicate broadcast on replay. | Completed |
| Public evidence for a `409` screenshot is missing. | The source repo contains tests and docs, but no screenshot artifact. | I kept screenshot evidence pending. | Blocked |

## Testing, Build and Deployment Results

| Area | Result | Evidence |
|---|---|---|
| Backend concurrency tests | Partially completed | Test sources exist: `backend/tests/test_apply_idempotency.py`, `backend/tests/test_apply_idempotency_postgres.py`, `backend/tests/test_optimistic_concurrency.py`, and `backend/tests/test_optimistic_concurrency_postgres.py`. Current-run output is pending. |
| Chat concurrency tests | Partially completed | Test source exists: `chat-service/tests/chatRepository.concurrency.test.js`. Current-run output is pending. |
| API conflict behavior | Implemented | Source contains explicit `409` handling for stale versions, duplicate apply, and idempotency-key reuse. |
| Deployment | Planned | This week focused on correctness before deployment. |

## Evidence

### Screenshots

Evidence pending: add screenshots under `/images/worklog/week-02/`, for example:

- `/images/worklog/week-02/duplicate-apply-409.png`
- `/images/worklog/week-02/idempotency-replay.png`
- `/images/worklog/week-02/postgres-concurrency-tests.png`

### Commits and Pull Requests

| Commit | Description | Evidence | Pull Request |
|---|---|---|---|
| `0f9e7f2` | Added backend workflow outbox, idempotency records, optimistic concurrency helpers, async processing foundation, and tests. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/0f9e7f2aed730153e905df0700fc3401f8957b21) | Evidence pending |
| `5326cb0` | Hardened chat repository concurrency and added chat concurrency tests. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/5326cb0ad12bf5e311236469e5c2b90c7fe20b6e) | Evidence pending |
| `77faab4` | Integrated workflow and processing contracts into frontend API helpers and UI flows. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/77faab4a919405beef1865fc06a106b0289a3310) | Evidence pending |
| `5041f84` | Fixed failing optimistic concurrency test assertions. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/5041f84600390724c4760c51da499592b1cf6104) | Evidence pending |

### Test Logs

Evidence pending: attach actual output from commands such as:

```bash
cd backend
python -m pytest tests/test_apply_idempotency.py tests/test_optimistic_concurrency.py
python -m pytest -m postgres tests/test_apply_idempotency_postgres.py tests/test_optimistic_concurrency_postgres.py
```

### Build Logs

Not applicable for the core Week 2 task. No dedicated build artifact was found for this phase.

### Deployment Logs

Not applicable for Week 2. The feature was designed to be safe before scaling the backend in Kubernetes.

## Weekly Results

My Week 2 result was a deployment-focused review of the team's database-backed concurrency policy and its behavior with multiple replicas. The backend and chat implementations themselves were owned by the teammates responsible for those components.

## Lessons Learned

Service load balancing does not serialize writes. Correctness must be enforced at the storage and transaction boundary, then reflected clearly through API response codes and UI behavior.

## Next Week Plan

Build the transactional outbox and asynchronous processing layers so committed domain changes can trigger reliable downstream work without keeping the main API request open.
