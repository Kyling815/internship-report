---
title: "Backend Deployment"
date: 2024-01-01
weight: 7
chapter: false
pre: " <b> 5.7. </b> "
---

## Objective

Deploy and verify the EKS application workloads: FastAPI backend, chat service, outbox dispatcher, processing worker, and AI service adapter.

## Architecture context

The frontend is not deployed to EKS. EKS hosts the long-running services and workers behind an ALB origin used by CloudFront.

## Deployment inputs

The production workflow computes image URIs from the AWS account, region, ECR repository, and `github.sha`:

| Workload | Image variable | Default ECR repository |
|---|---|---|
| Backend and workers | `BACKEND_IMAGE` | `internship-backend` |
| Chat service | `CHAT_IMAGE` | `internship-chat` |
| AI adapter | `AI_IMAGE` | `internship-ai` |

The deployment script requires:

- `BACKEND_IMAGE`
- `CHAT_IMAGE`
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `AWS_REGION`
- `OUTBOX_QUEUE_URL`

Optional but important:

- `AI_DEPLOY_ENABLED`
- `AI_IMAGE`
- `PROCESSING_WORKER_ENABLED`
- `SAGEMAKER_ENDPOINT_NAME`
- `AI_SERVICE_BASE_URL`
- `IRSA_ROLE_ARN`
- `S3_BUCKET`
- `AI_SERVICE_API_KEY`

## Image build and ECR push

The CI helper `scripts/ci/deploy-eks-pipeline.sh` builds and pushes images:

```bash
bash scripts/ci/deploy-eks-pipeline.sh
```

The workflow verifies pushed backend and chat tags:

```bash
aws ecr describe-images \
  --region ap-southeast-1 \
  --repository-name internship-backend \
  --image-ids imageTag=<GITHUB_SHA>

aws ecr describe-images \
  --region ap-southeast-1 \
  --repository-name internship-chat \
  --image-ids imageTag=<GITHUB_SHA>
```

If `AI_DEPLOY_ENABLED=true`, the AI adapter image is built with:

```bash
docker build --file Dockerfile.ai-service --tag <AI_IMAGE> .
docker push <AI_IMAGE>
```

## Kubernetes namespace and ServiceAccount

The deployment applies:

```bash
kubectl apply -f k8s/app/namespace.yaml
kubectl apply -f k8s/app/serviceaccount.yaml
```

When `IRSA_ROLE_ARN` is set, the EKS-specific ServiceAccount manifest is rendered and applied from `k8s/eks/serviceaccount.yaml`.

Verification:

```bash
kubectl get namespace internship
kubectl get serviceaccount internship-app -n internship -o yaml
```

## ConfigMap and Secret usage

The production ConfigMap comes from `k8s/eks/configmap.yaml`. Important values include:

| Key | Value or purpose |
|---|---|
| `APP_ENV` | `eks` |
| `OUTBOX_PUBLISHER` | `sqs` |
| `AI_SERVICE_BASE_URL` | `http://ai-service:8010` |
| `AI_SERVICE_PARSE_TIMEOUT_SECONDS` | `120` |
| `AI_SERVICE_MATCH_TIMEOUT_SECONDS` | `600` |
| `STORAGE_BACKEND` | `s3` |
| `AWS_REGION` | `ap-southeast-1` |
| `DYNAMODB_USERS_TABLE` | `ChatUsers` |
| `DYNAMODB_GROUPS_TABLE` | `ChatGroups` |
| `DYNAMODB_MESSAGES_TABLE` | `ChatMessages` |

The deployment creates or updates Kubernetes Secret `internship-secrets` from GitHub secrets. Do not print secret values.

Verification:

```bash
kubectl get configmap internship-config -n internship -o yaml
kubectl describe secret internship-secrets -n internship
```

## Migration and chat initialization jobs

The deployment deletes old jobs, applies fresh jobs, and waits for completion:

```bash
kubectl delete job backend-migrate chat-init -n internship --ignore-not-found
kubectl apply -f <rendered-backend-migration-job.yaml>
kubectl apply -f <rendered-chat-init-job.yaml>
kubectl wait --for=condition=complete job/backend-migrate -n internship --timeout=300s
kubectl wait --for=condition=complete job/chat-init -n internship --timeout=300s
```

`backend-migrate` runs `alembic upgrade head`. `chat-init` initializes the DynamoDB chat tables.

## Workload deployments

| Deployment | Container command | Port | Replicas | Purpose |
|---|---|---:|---:|---|
| `backend` | `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers` | 8000 | 2 | FastAPI REST API |
| `chat-service` | `node server.js` through image start command | 3000 | 2 | Chat REST and Socket.IO |
| `backend-outbox-dispatcher` | `python -m app.workers.outbox_dispatcher` | 9101 metrics | 1 | Publishes outbox events to SQS |
| `backend-processing-worker` | `python -m app.workers.processing_worker` | 9102 metrics | 2 in manifest, can be rendered to 0 | Async AI/document jobs |
| `ai-service` | AI image command | 8010 | 1 | SageMaker adapter |

Apply and verify:

```bash
bash scripts/k8s/deploy-eks.sh
kubectl rollout status deployment/backend -n internship --timeout=300s
kubectl rollout status deployment/chat-service -n internship --timeout=300s
kubectl rollout status deployment/backend-outbox-dispatcher -n internship --timeout=300s
kubectl rollout status deployment/backend-processing-worker -n internship --timeout=300s
kubectl rollout status deployment/ai-service -n internship --timeout=900s
```

Only run the `ai-service` rollout command when AI deployment is enabled.

## AI and processing worker gate

The deployment script blocks unsafe worker enablement:

- `PROCESSING_WORKER_ENABLED=true` requires `AI_DEPLOY_ENABLED=true`.
- `PROCESSING_WORKER_ENABLED=true` requires `AI_IMAGE`.
- SageMaker endpoint `internship-qwen3-4b` must be `InService`.

Check the endpoint before enabling the worker:

```bash
aws sagemaker describe-endpoint \
  --endpoint-name internship-qwen3-4b \
  --region ap-southeast-1 \
  --query EndpointStatus \
  --output text
```

Expected result:

```text
InService
```

## Health probes

| Workload | Startup probe | Readiness probe | Liveness probe |
|---|---|---|---|
| `backend` | `/health/live` | `/health/ready` | `/health/live` |
| `chat-service` | `/health/live` | `/health/ready` | `/health/live` |
| `ai-service` | Not configured separately | `/health/ready` | `/health/ready` |
| `backend-outbox-dispatcher` | TCP `9101` | TCP `9101` | TCP `9101` |
| `backend-processing-worker` | TCP `9102` | TCP `9102` | TCP `9102` |

## HPA and PDB

The manifest `k8s/app/autoscaling.yaml` defines:

| Resource | HPA | PDB |
|---|---|---|
| `backend` | min 2, max 5, CPU target 70% | min available 1 |
| `chat-service` | min 2, max 5, CPU target 70% | min available 1 |
| `backend-processing-worker` | min 2, max 5, CPU target 70% | min available 1 when worker enabled |

When the processing worker is disabled, deployment scripts delete its HPA and PDB and scale it to zero.

Verification:

```bash
kubectl get hpa,pdb -n internship
kubectl describe hpa backend -n internship
kubectl describe hpa chat-service -n internship
```

## Ingress and ALB routing

The public ALB Ingress is `k8s/eks/ingress-alb-no-domain.yaml`. It routes:

- `/api` to Service `backend`
- `/chat` to Service `chat-service`
- `/socket.io` to Service `chat-service`

Deploy public ALB routing with the workflow mode `deploy-public` or the helper script:

```bash
ENABLE_ALB_INGRESS=true bash scripts/aws/deploy-public-ingress.sh
```

Verification:

```bash
kubectl get ingress internship-public -n internship
curl -fsS http://k8s-internshippublic-48101b50ad-85486086.ap-southeast-1.elb.amazonaws.com/api/health/ready
curl -fsS http://k8s-internshippublic-48101b50ad-85486086.ap-southeast-1.elb.amazonaws.com/chat/health/ready
```

## Port-forward smoke checks

The deployment script uses local port-forwards for health smoke tests:

```bash
kubectl port-forward service/backend 18080:8000 -n internship
curl -fsS http://127.0.0.1:18080/health/ready
```

```bash
kubectl port-forward service/chat-service 18081:3000 -n internship
curl -fsS http://127.0.0.1:18081/health/ready
```

```bash
kubectl port-forward service/ai-service 18082:8010 -n internship
curl -fsS http://127.0.0.1:18082/health/ready
```

## Expected result

- Migration and chat init jobs complete.
- Backend, chat, and dispatcher deployments roll out successfully.
- Processing worker is either Ready or intentionally scaled to zero.
- AI service is Ready when AI deployment is enabled.
- Services have endpoints.
- ALB health checks pass for backend and chat.
- CloudFront can reach ALB origin for `/api`, `/chat`, and `/socket.io`.

## Common errors

| Symptom | Cause | Resolution |
|---|---|---|
| `Missing required environment variable` | Required deployment secret or variable absent | Add the missing GitHub secret or variable |
| `Unable to compute backend/chat image URIs` | Workflow variable or SHA-based image construction issue | Use account, region, repository, and `github.sha` |
| ECR image not found | Build/push job did not publish the SHA tag | Inspect `build-images` job and ECR repository |
| `PROCESSING_WORKER_ENABLED=true` fails | AI dependencies not ready | Enable AI image and verify SageMaker `InService` first |
| Chat readiness fails | Redis or DynamoDB dependency unavailable | Inspect chat logs and DynamoDB/Redis status |
| Backend readiness fails | PostgreSQL unavailable or migration failed | Inspect backend logs and RDS connectivity |

## Outcome

The EKS backend deployment is complete when backend, chat, dispatcher, optional worker, and optional AI adapter are running with correct probes, services, endpoints, scaling controls, and ALB routing.
