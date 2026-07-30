---
title: "Week 1 Worklog"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 1.1. </b> "
---

# Week 1 - Project Analysis and Architecture Baseline

## Objectives

Within the five-member team, my first-week objective was to understand the parts of the source code that affected deployment, identify service boundaries and dependencies, and document an architecture baseline for the later Cloud/DevOps work.

## My Contributions

| Status | My assigned contribution | Evidence basis |
|---|---|---|
| Completed | Reviewed the monorepo structure and identified the main runtime services. | Source tree, `README.md`, `docker-compose.yml`, and commit `4e939cf`. |
| Completed | Mapped the frontend, FastAPI backend, chat service, AI service, PostgreSQL, Redis, and DynamoDB dependencies. | `backend/`, `frontend/`, `chat-service/`, `ai_service/`, Compose files, and service configuration. |
| Completed | Reviewed the initial request flow between browser, API, chat, and storage layers. | Frontend API clients, backend routers, chat Socket.IO server, and backend storage services. |
| Completed | Checked the local startup model and documented separate service startup commands. | Commits `d3c1168` and `e43cc04`. |
| Partially completed | Prepared the evidence plan for the local architecture baseline. | Evidence pending: screenshots are not present in the Hugo image directory yet. |

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

By the end of Week 1, I had produced the service and dependency map needed for my deployment scope and an initial containerization/AWS deployment direction. The application code and feature baseline remained the shared output of the five-member team.

## Lessons Learned

The main lesson was that deployment planning depends on clear runtime boundaries. Separating API, chat, AI, relational data, realtime pub/sub, and document storage early made later Docker, Kubernetes, and AWS work easier to reason about.

## Next Week Plan

The next week should focus on data integrity and concurrency: database constraints, duplicate request handling, idempotency keys, versioned workflow commands, and tests that prove concurrent writes return controlled conflicts instead of inconsistent data.
