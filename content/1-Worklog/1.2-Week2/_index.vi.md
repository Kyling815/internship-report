---
title: "Nhật ký tuần 2"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 1.2. </b> "
---

# Tuần 2 - Kiểm soát concurrency và data integrity

## Mục tiêu

Trong nhóm 5 thành viên, mục tiêu tuần 2 của tôi là review các yêu cầu concurrency và data integrity ảnh hưởng đến môi trường nhiều replica. Tôi hỗ trợ thành viên backend và chat kiểm tra idempotency, version check và database constraint trước khi đưa hệ thống lên Kubernetes.

## Phần việc cá nhân

| Trạng thái | Phần việc được phân công | Cơ sở minh chứng |
|---|---|---|
| Hoàn thành | Phân tích concurrent write khi nhiều backend pod xử lý đồng thời. | `docs/architecture/concurrency-policy.md`. |
| Hoàn thành | Đóng góp góc nhìn triển khai vào chính sách optimistic/pessimistic UI. | `docs/architecture/concurrency-policy.md` và `docs/frontend/COMMAND_MUTATION_POLICY.md`. |
| Hoàn thành | Review cơ chế idempotency do thành viên backend triển khai cho thao tác ứng tuyển. | Service, router và migration `0004_idempotency_records.py`. |
| Hoàn thành | Review workflow command dùng `expectedVersion` trong môi trường nhiều pod. | Optimistic concurrency service, workflow command và các router liên quan. |
| Hoàn thành | Phối hợp với thành viên chat kiểm tra hành vi retry và chống ghi trùng. | Chat repository và concurrency test. |
| Hoàn thành một phần | Thu thập screenshot API và CI log hiện có. | Cần bổ sung minh chứng: chưa có artifact screenshot hoặc GitHub Actions log trong kho local. |

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

Kết quả cá nhân tuần 2 là bản review theo góc nhìn triển khai đối với chính sách concurrency của nhóm và hành vi khi chạy nhiều replica. Phần triển khai backend và chat thuộc trách nhiệm của các thành viên phụ trách hai component này.

## Lessons Learned

Service load balancing does not serialize writes. Correctness must be enforced at the storage and transaction boundary, then reflected clearly through API response codes and UI behavior.

## Next Week Plan

Build the transactional outbox and asynchronous processing layers so committed domain changes can trigger reliable downstream work without keeping the main API request open.
