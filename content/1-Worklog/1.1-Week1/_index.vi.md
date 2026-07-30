---
title: "Nhật ký tuần 1"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 1.1. </b> "
---

# Tuần 1 - Phân tích project và kiến trúc cơ sở

## Mục tiêu

Trong nhóm 5 thành viên, mục tiêu cá nhân của tôi trong tuần đầu là tìm hiểu các phần mã nguồn liên quan đến triển khai, xác định ranh giới và phụ thuộc giữa các service, đồng thời lập tài liệu kiến trúc cơ sở cho công việc Cloud/DevOps ở các tuần sau.

## Phần việc cá nhân

| Trạng thái | Phần việc được phân công | Cơ sở minh chứng |
|---|---|---|
| Hoàn thành | Khảo sát cấu trúc monorepo và xác định các service chạy chính. | Cây mã nguồn, `README.md`, `docker-compose.yml` và commit `4e939cf`. |
| Hoàn thành | Lập bản đồ phụ thuộc giữa frontend, FastAPI backend, chat service, AI service, PostgreSQL, Redis và DynamoDB. | Các thư mục service, Compose và cấu hình hệ thống. |
| Hoàn thành | Review luồng request ban đầu giữa browser, API, chat và các lớp lưu trữ. | API client, backend router, Socket.IO server và storage service. |
| Hoàn thành | Kiểm tra mô hình khởi chạy local và tài liệu hóa cách chạy riêng từng service. | Commit `d3c1168` và `e43cc04`. |
| Hoàn thành một phần | Chuẩn bị kế hoạch minh chứng cho kiến trúc local ban đầu. | Cần bổ sung minh chứng: chưa có screenshot trong thư mục ảnh Hugo. |

## Technical Implementation

The source repository is a monorepo with separate service responsibilities:

- `frontend/`: React and Vite application for Candidate and HR users.
- `backend/`: FastAPI API, SQLAlchemy models, Alembic migrations, authentication, jobs, applications, documents, and AI orchestration routes.
- `chat-service/`: Node.js, Express, Socket.IO, Redis adapter, and DynamoDB-backed chat persistence.
- `ai_service/`: AI parsing, CV/job normalization, reranking, and later SageMaker adapter code.
- `docker-compose.yml`: local dependencies and multi-service startup path.

Initial architecture baseline:

{{< mermaid >}}
graph LR
  User["Candidate / HR browser"] --> Frontend["React / Vite frontend"]
  Frontend --> Backend["FastAPI backend"]
  Frontend --> Chat["Node.js Socket.IO chat service"]
  Backend --> Postgres["PostgreSQL"]
  Backend --> Storage["S3-compatible document storage"]
  Backend --> AI["AI service"]
  Chat --> Redis["Redis pub/sub"]
  Chat --> DynamoDB["DynamoDB chat tables"]
{{< /mermaid >}}

The baseline also identified the first cloud migration direction: keep long-running backend and chat services containerized, move durable relational data to PostgreSQL/RDS, use DynamoDB for chat records, use Redis for realtime fan-out, and prepare the application for containerization and CI/CD.

## Problems and Solutions

| Problem | Root cause | Resolution | Status |
|---|---|---|---|
| The first source snapshot contained broad application code and generated dependency content. | The initial commit added the complete baseline in one large commit. | Later work separated documentation, scripts, and runtime responsibilities into clearer paths. | Completed |
| The project originally contained Prisma-related Node database artifacts while the backend used SQLAlchemy/PostgreSQL. | Database strategy changed toward FastAPI, SQLAlchemy, Alembic, and PostgreSQL. | Commit `ab60f7d` removed Prisma artifacts and documented the EC2/RDS direction. | Completed |
| Local startup needed to support more than one developer workflow. | A single startup command was useful for demos, but separate terminal commands were easier for debugging. | Commits `d3c1168` and `e43cc04` documented both startup approaches. | Completed |
| I did not have architecture screenshots in the local evidence archive. | I did not have the original screenshot artifacts in the source repo. | I kept screenshot evidence pending instead of creating fake screenshots. | Blocked |

## Testing, Build and Deployment Results

| Area | Result | Evidence |
|---|---|---|
| Source inspection | Completed | `git show --stat 4e939cf` shows backend, frontend, Docker, migrations, tests, and docs added in the first commit. |
| Local startup | Partially completed | Startup scripts and README instructions exist in history, but no saved terminal log was found. |
| Tests | Partially completed | Test files exist under `backend/tests`; no Week 1 test output artifact was found. |
| Build | Partially completed | Dockerfiles and Vite project files exist; no Week 1 build log artifact was found. |
| Deployment | Planned | Week 1 only defined the deployment direction; no AWS deployment was expected yet. |

## Evidence

### Screenshots

Evidence pending: add architecture or local application screenshots under `/images/worklog/week-01/`, for example:

- `/images/worklog/week-01/repository-structure.png`
- `/images/worklog/week-01/local-backend-health.png`
- `/images/worklog/week-01/architecture-baseline.png`

### Commits and Pull Requests

| Commit | Description | Evidence | Pull Request |
|---|---|---|---|
| `4e939cf` | Initial application baseline with backend, frontend, Docker Compose, migrations, and tests. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/4e939cf0313e73fd915380987cce1a5a7c9728a0) | Evidence pending |
| `5ab2924` | Added AI CV matching and AWS RDS configuration. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/5ab2924ca69ed90f7ef5fe5a454578bfa888e9dc) | Evidence pending |
| `ab60f7d` | Removed Prisma artifacts and documented EC2/RDS deployment direction. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/ab60f7d02c6c8fc73384198117625dea5973e24f) | Evidence pending |
| `d3c1168` | Added one-command full-stack startup. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/d3c1168cea4521823febf32e1fd9714e928d0ddc) | Evidence pending |
| `e43cc04` | Documented separate service startup commands. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/e43cc042d868b1ca5c18524d4735dca178f25043) | Evidence pending |

### Test Logs

Evidence pending: no saved Week 1 local or CI test log was found in the source repository.

### Build Logs

Evidence pending: no saved Week 1 Docker or frontend build log was found in the source repository.

### Deployment Logs

Not applicable for Week 1. Deployment planning started in this phase, but cloud deployment was planned for later weeks.

## Weekly Results

Cuối tuần 1, tôi đã hoàn thành bản đồ service/phụ thuộc phục vụ phạm vi triển khai và xác định hướng container hóa, triển khai AWS ban đầu. Mã nguồn ứng dụng và các chức năng nền tảng là kết quả chung của nhóm 5 thành viên.

## Lessons Learned

The main lesson was that deployment planning depends on clear runtime boundaries. Separating API, chat, AI, relational data, realtime pub/sub, and document storage early made later Docker, Kubernetes, and AWS work easier to reason about.

## Next Week Plan

The next week should focus on data integrity and concurrency: database constraints, duplicate request handling, idempotency keys, versioned workflow commands, and tests that prove concurrent writes return controlled conflicts instead of inconsistent data.
