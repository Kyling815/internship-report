---
title: "Week 3 Worklog"
date: 2024-01-01
weight: 3
chapter: false
pre: " <b> 1.3. </b> "
---

# Week 3 - Transactional Outbox and Asynchronous Processing

## Objectives

Within the five-member team, my Week 3 objective was to define the deployment and integration requirements for the transactional outbox and asynchronous workers. I focused on production transport, worker lifecycle, retries, configuration, and observability while the backend member owned the business implementation.

## My Contributions

| Status | My assigned contribution | Evidence basis |
|---|---|---|
| Completed | Reviewed the `outbox_events` schema from a deployment and recovery perspective. | `backend/alembic/versions/0007_outbox_events.py`. |
| Completed | Validated the lifecycle states and retry model needed for operations. | Migration check constraint and `backend/app/services/outbox.py`. |
| Completed | Reviewed `deduplication_key` and claim/retry indexes for multi-worker execution. | Migration `0007_outbox_events.py`. |
| Completed | Defined runtime requirements for the outbox dispatcher and admin operations. | `backend/app/workers/outbox_dispatcher.py` and `backend/app/workers/outbox_admin.py`. |
| Completed | Documented SQS Standard as the production event transport for the team. | `docs/architecture/adr/ADR-001-production-event-transport.md`. |
| Completed | Coordinated integration requirements for `async_processing_jobs` and the document/AI worker. | Migration `0008_async_processing_jobs.py`, `processing_jobs.py`, and `processing_worker.py`. |
| Partially completed | Assessed downstream consumer readiness beyond the contract. | Source docs state downstream notification/search/analytics consumers were not implemented in this phase. |

## Technical Implementation

The outbox design keeps domain mutation and event creation in the same PostgreSQL transaction. If the business write fails, no event is inserted. If the API pod dies after commit, the outbox row remains `PENDING` and can be claimed later by the dispatcher.

{{< mermaid >}}
sequenceDiagram
  participant API as FastAPI backend
  participant DB as PostgreSQL
  participant D as Outbox dispatcher
  participant SQS as Amazon SQS Standard
  participant C as Future consumer
  API->>DB: commit domain change + outbox row
  D->>DB: claim PENDING event
  D->>SQS: publish event envelope
  alt publish accepted
    D->>DB: mark PUBLISHED
  else retryable failure
    D->>DB: return to PENDING with backoff
  else non-retryable or max attempts
    D->>DB: mark DEAD
  end
  C->>SQS: consume message
  C->>C: deduplicate by eventId
{{< /mermaid >}}

Asynchronous processing uses a separate database-backed queue because document parsing and AI matching are user-visible jobs with status, retry behavior, source-version guards, and result payloads. The worker claims jobs, applies lease-based retry logic, and persists results back to PostgreSQL.

## Problems and Solutions

| Problem | Root cause | Resolution | Status |
|---|---|---|---|
| A committed workflow change could lose its follow-up event if publishing failed after the database commit. | Direct publish inside request handling is not transactional with PostgreSQL. | Insert a canonical outbox event in the same DB transaction, then dispatch asynchronously. | Completed |
| SQS Standard can redeliver or reorder messages. | Standard queues provide at-least-once delivery, not exactly-once delivery. | The event envelope includes `eventId`; consumers must deduplicate by `eventId`. | Completed |
| Dispatcher failure can leave events half-processed. | A worker can die after claiming or publishing an event. | Lease expiry, retry counters, `DEAD` status, and admin requeue/cleanup commands were added. | Completed |
| AI and document work can take too long for API request latency. | Parsing CVs, extracting text, and reranking candidates are long-running operations. | Added `async_processing_jobs` and `backend-processing-worker`. | Completed |
| Real downstream consumers were not part of this implementation slice. | I focused the week on producer reliability and the consumer contract. | I kept downstream consumers as future work until runtime evidence is added. | Partially completed |

## Testing, Build and Deployment Results

| Area | Result | Evidence |
|---|---|---|
| Outbox unit/integration test coverage | Partially completed | Test sources exist: `test_outbox_events.py`, `test_outbox_postgres.py`, `test_outbox_publishers.py`, and `test_outbox_admin.py`. Current-run output is pending. |
| Async processing tests | Partially completed | Test sources exist: `test_processing_jobs.py` and `test_processing_jobs_postgres.py`. Current-run output is pending. |
| Kubernetes deployment readiness | Implemented | `k8s/app/backend-outbox-dispatcher.yaml` and `k8s/app/backend-processing-worker.yaml` exist. |
| SQS provisioning | Implemented | `scripts/aws/provision-outbox-sqs.ps1` and `.sh` exist. Runtime queue-name evidence still needs a screenshot or CLI log. |

## Evidence

### Screenshots

Evidence pending: add screenshots under `/images/worklog/week-03/`, for example:

- `/images/worklog/week-03/outbox-table.png`
- `/images/worklog/week-03/sqs-queue-dlq.png`
- `/images/worklog/week-03/dispatcher-logs.png`

### Commits and Pull Requests

| Commit | Description | Evidence | Pull Request |
|---|---|---|---|
| `0f9e7f2` | Added backend workflow outbox, async processing jobs, dispatcher, worker, and tests. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/0f9e7f2aed730153e905df0700fc3401f8957b21) | Evidence pending |
| `be84e4e` | Added Kubernetes deployments, SQS provisioning scripts, validation gates, and alerts for async workers. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/be84e4e5e6bd6a1ba73fb9c11532274788060e8c) | Evidence pending |
| `4970eba` | Documented phase 2 workflow operations, event transport ADR, and consumer contract. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/4970ebad398a5377004e943dc3486f8e717a952e) | Evidence pending |
| `14173c6` | Merged workflow, outbox, async processing, and infrastructure changes. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/14173c6d0e950f13a5f7e809d95fc39841c06048) | Evidence pending |

### Test Logs

Evidence pending: attach actual output from commands such as:

```bash
cd backend
python -m pytest tests/test_outbox_events.py tests/test_outbox_publishers.py tests/test_processing_jobs.py
python -m pytest -m postgres tests/test_outbox_postgres.py tests/test_processing_jobs_postgres.py
```

### Build Logs

Evidence pending: no dedicated Week 3 image build log was found.

### Deployment Logs

Evidence pending: add dispatcher or worker rollout logs after deployment, for example `kubectl rollout status deployment/backend-outbox-dispatcher -n internship`.

## Weekly Results

My Week 3 result was the SQS transport decision and a documented set of deployment requirements for the outbox dispatcher and processing worker. The outbox schema, backend services, and document/AI business logic remained team deliverables.

## Lessons Learned

Idempotency exists at multiple layers. HTTP idempotency prevents duplicate command execution, the transactional outbox prevents lost domain events, and consumers still need event-level deduplication.

## Next Week Plan

Standardize container builds, CI quality gates, smoke tests, security scans, and infrastructure validation so the system can be deployed repeatedly with less manual checking.
