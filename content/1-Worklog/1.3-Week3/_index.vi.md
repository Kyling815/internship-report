---
title: "Nhật ký tuần 3"
date: 2024-01-01
weight: 3
chapter: false
pre: " <b> 1.3. </b> "
---

# Tuần 3 - Transactional outbox và xử lý bất đồng bộ

## Mục tiêu

Trong nhóm 5 thành viên, mục tiêu tuần 3 của tôi là xác định yêu cầu triển khai và tích hợp cho transactional outbox cùng các worker xử lý bất đồng bộ. Tôi tập trung vào production transport, vòng đời worker, retry, cấu hình và observability; thành viên backend phụ trách business implementation.

## Phần việc cá nhân

| Trạng thái | Phần việc được phân công | Cơ sở minh chứng |
|---|---|---|
| Hoàn thành | Review schema `outbox_events` theo góc nhìn triển khai và phục hồi. | `backend/alembic/versions/0007_outbox_events.py`. |
| Hoàn thành | Kiểm tra các trạng thái vòng đời và retry model phục vụ vận hành. | Migration constraint và `backend/app/services/outbox.py`. |
| Hoàn thành | Review `deduplication_key` cùng các index claim/retry cho nhiều worker. | Migration `0007_outbox_events.py`. |
| Hoàn thành | Xác định yêu cầu runtime cho outbox dispatcher và admin operation. | Các worker `outbox_dispatcher.py` và `outbox_admin.py`. |
| Hoàn thành | Tài liệu hóa SQS Standard làm production event transport cho nhóm. | ADR về production event transport. |
| Hoàn thành | Phối hợp xác định yêu cầu tích hợp cho `async_processing_jobs` và worker document/AI. | Migration, processing job service và processing worker. |
| Hoàn thành một phần | Đánh giá mức sẵn sàng của downstream consumer ngoài contract. | Tài liệu nguồn cho biết notification/search/analytics consumer chưa được triển khai ở giai đoạn này. |

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

Kết quả cá nhân tuần 3 là quyết định dùng SQS và bộ yêu cầu triển khai cho outbox dispatcher, processing worker. Schema outbox, backend service và business logic document/AI vẫn là sản phẩm chung của nhóm.

## Lessons Learned

Idempotency exists at multiple layers. HTTP idempotency prevents duplicate command execution, the transactional outbox prevents lost domain events, and consumers still need event-level deduplication.

## Next Week Plan

Standardize container builds, CI quality gates, smoke tests, security scans, and infrastructure validation so the system can be deployed repeatedly with less manual checking.
