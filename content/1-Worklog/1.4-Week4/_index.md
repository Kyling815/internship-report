---
title: "Week 4 Worklog"
date: 2024-01-01
weight: 4
chapter: false
pre: " <b> 1.4. </b> "
---

# Week 4 - Containerization and CI Quality Gates

## Objectives

Week 4 was the first week centered on my primary Cloud/DevOps assignment in the five-member team. My objective was to make the teammates' backend, frontend, chat, and AI components repeatable through containers, Docker Compose, CI quality gates, smoke tests, and security checks.

## My Contributions

| Status | My assigned contribution | Evidence basis |
|---|---|---|
| Completed | Standardized Docker build paths for backend, chat, frontend, and AI service. | `backend/Dockerfile`, `chat-service/Dockerfile`, `frontend/Dockerfile`, and `Dockerfile.ai-service`. |
| Completed | Kept local Compose as the parity environment for dependencies and smoke tests. | `docker-compose.yml`, `docker-compose.ai-service.yml`, and `scripts/ci/smoke-test.sh`. |
| Completed | Consolidated GitHub Actions into the main CI/CD workflow. | `.github/workflows/cicd.yml` and commit `e09e84e`. |
| Completed | Added required quality/security gates. | `scripts/ci/repository_quality.py`, `scripts/ci/infrastructure.py`, `scripts/ci/security_scan.py`, `.gitleaks.toml`, and `.pre-commit-config.yaml`. |
| Completed | Fixed ShellCheck SC2155 in the smoke test script. | Commit `98f3420`. |

## Technical Implementation

The final CI workflow defines validation jobs for backend, chat service, frontend, Docker images, infrastructure, smoke checks, and security scanning. The workflow uses Python 3.12, Node.js 22, shell validation, Docker image builds, Trivy/Gitleaks images, and actionlint/kubeconform support through the infrastructure script.

Relevant workflow checks include:

```bash
python -m ruff format --check .
python -m ruff check .
python -m mypy app tests
python -m pytest -m "not postgres"
npm run check --prefix chat-service
npm run lint --prefix chat-service
npm run format:check --prefix chat-service
npm run test:ci --prefix chat-service
npm run test --prefix frontend
npm run build --prefix frontend
docker build -t internship-backend:ci ./backend
docker build -t internship-chat:ci ./chat-service
docker build -f Dockerfile.ai-service -t internship-ai:ci .
```

## Problems and Solutions

| Problem | Root cause | Resolution | Status |
|---|---|---|---|
| Multiple workflows made the deployment path harder to control. | Separate CI/deploy workflows split validation and deployment behavior. | Consolidated workflows into `.github/workflows/cicd.yml`. | Completed |
| ShellCheck flagged SC2155 in the smoke test script. | Assignment and command substitution were combined in a way ShellCheck warns about. | Commit `98f3420` split the logic to satisfy ShellCheck. | Completed |
| `.env` files can contain UTF-8 BOM and break shell parsing. | Windows editors may add BOM at the beginning of files. | `scripts/ci/smoke-test.sh` strips the BOM when preparing smoke-test env input. | Completed |
| Docker-based infra validation may hang or fail when Docker is unavailable. | Local Windows/Docker setups vary by machine. | Infrastructure scripts support local CLI binaries and bounded Docker fallback behavior. | Completed |

## Testing, Build and Deployment Results

| Area | Result | Evidence |
|---|---|---|
| Backend CI commands | Implemented | Commands are defined in `.github/workflows/cicd.yml`. Current-run output is pending. |
| Chat CI commands | Implemented | Commands are defined in `.github/workflows/cicd.yml` and `scripts/chat-service.sh`. Current-run output is pending. |
| Frontend CI commands | Implemented | Commands are defined in `.github/workflows/cicd.yml` and `scripts/frontend.sh`. Current-run output is pending. |
| Infrastructure/security checks | Implemented | `scripts/ci/infrastructure.py`, `scripts/check-infra.ps1`, `scripts/check-infra.sh`, and `scripts/ci/security_scan.py` exist. |
| Compose smoke test | Implemented | `scripts/ci/smoke-test.sh` exists and ends with `Compose smoke test passed` on success. Current-run output is pending. |

## Evidence

### Commits and Pull Requests

| Commit | Description | Evidence | Pull Request |
|---|---|---|---|
| `b4ef947` | Added required pipeline gates, security scanning, pre-commit config, and infrastructure validation scripts. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/b4ef947551615e6f22ae4261c6c977b4019080a3) | Evidence pending |
| `e09e84e` | Consolidated workflows into a single `cicd.yml` pipeline. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/e09e84ee423067eb5c2fa766133bd133b9f03a45) | Evidence pending |
| `29de145` | Resolved CI failures for pytest, frontend build, and infrastructure checks. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/29de145dc5eca8036ee76aedd29db24953a32245) | Evidence pending |
| `98f3420` | Fixed ShellCheck SC2155 in the smoke test script. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/98f34200147423960604f23a7f960a853c59cd0a) | Evidence pending |
| `c2ad7cc` | Consolidated and optimized the GitHub Actions workflow. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/c2ad7cc72ed18a9f90441696675939f7b94154b6) | Evidence pending |

### Test Logs

Evidence pending: attach CI or local output for backend, chat, frontend, and smoke-test jobs.

### Build Logs

Evidence pending: attach Docker build and Vite build output from GitHub Actions or a local run.

### Deployment Logs

Not applicable for Week 4. This phase prepared deployable artifacts and gates, while AWS/EKS deployment continued in later weeks.

## Weekly Results

My Week 4 result was a shared CI/CD backbone and repeatable container validation path that all five members could use. Feature code remained with the corresponding component owners; my responsibility was packaging, automation, and integration validation.

## Lessons Learned

CI should fail early on repeatable checks: formatting, typing, tests, build, security, shell syntax, Dockerfile quality, and infrastructure manifest validation. Making these checks explicit reduced the amount of manual inspection needed before deployment.

## Next Week Plan

Move from Docker Compose to local Kubernetes with kind, Kubernetes manifests, migration/init jobs, probes, HPA/PDB configuration, and observability resources.
