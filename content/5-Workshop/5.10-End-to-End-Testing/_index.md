---
title: "End-to-End Testing"
date: 2024-01-01
weight: 10
chapter: false
pre: " <b> 5.10. </b> "
---

## Objective

Define an acceptance test set for the deployed Internship Application Tracker and record which results are verified, implemented but still requiring runtime evidence, proposed, or not completed.

## Architecture context

End-to-end tests must cover the full public path:

```text
Browser -> CloudFront -> S3 or ALB -> EKS workloads -> managed AWS services
```

They must also cover asynchronous paths:

```text
Backend -> PostgreSQL outbox -> dispatcher -> SQS -> Lambda -> DynamoDB dedupe -> S3 archive -> SES
```

## Test status definitions

| Status | Meaning |
|---|---|
| Verified | Runtime evidence from Week 8 or exported production evidence confirms the result |
| Implemented, verification required | Code or manifests implement the capability, but production runtime evidence is not included |
| Proposed | Recommended test or control, not proven implemented |
| Not completed | Not implemented or not completed in the evidence I have |

## Acceptance test table

| ID | Test case | Test input or command | Expected result | Evidence status |
|---|---|---|---|---|
| TC01 | CloudFront frontend | `curl -I https://dhm2rz5nmsibj.cloudfront.net/` | CloudFront returns frontend response | Implemented, verification required |
| TC02 | Backend health through CloudFront | `curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready` | Backend readiness JSON with PostgreSQL dependency true | Implemented, verification required |
| TC03 | Chat health through CloudFront | `curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready` | Chat readiness JSON with Redis and DynamoDB true | Implemented, verification required |
| TC04 | Socket.IO handshake | Browser or Socket.IO client connects with path `/socket.io` | Socket connection established through CloudFront and ALB | Implemented, verification required |
| TC05 | Registration | Create candidate or HR account | User created or duplicate email returns 409 | Implemented, verification required |
| TC06 | Login | Valid credentials | JWT session created and role-based route opens | Implemented, verification required |
| TC07 | Job creation | HR creates job posting | Job stored in PostgreSQL with version | Implemented, verification required |
| TC08 | Application submission | Candidate applies to published job | Application, documents, status history, outbox event and processing job are committed | Implemented, verification required |
| TC09 | Duplicate application handling | Repeat apply for same job/candidate | `409` duplicate application or idempotent replay | Implemented, verification required |
| TC10 | CV upload | Apply with CV/document | File stored in S3 or configured storage backend and metadata stored in PostgreSQL | Implemented, verification required |
| TC11 | Processing job creation | Submit CV/job parse request | `async_processing_jobs` row created and status visible | Implemented, verification required |
| TC12 | AI completion | Worker calls `ai-service` and SageMaker endpoint | Parsed CV/job or matching result persisted | Implemented, verification required |
| TC13 | Chat between two clients | Send direct or group message | Sender receives ACK; recipient receives realtime message | Implemented, verification required |
| TC14 | Chat persistence | Reload chat history | DynamoDB returns persisted message | Implemented, verification required |
| TC15 | Chat pod restart and reconnect | Restart one chat pod during active session | Socket reconnects and no duplicate persisted message for retry | Implemented, verification required |
| TC16 | PostgreSQL connectivity | Backend `/health/ready` | `postgres: true` | Implemented, verification required |
| TC17 | Redis status | Chat `/health/ready` | `redis: true` | Redis runtime status verified from Week 8 evidence; health endpoint output still useful |
| TC18 | DynamoDB table status | `describe-table` for chat tables | `ACTIVE` for `ChatUsers`, `ChatGroups`, `ChatMessages` | Verified from Week 8 DynamoDB evidence |
| TC19 | Outbox dispatcher | Inspect dispatcher deployment and logs | Dispatcher reads PostgreSQL outbox and publishes to SQS | Deployment verified from Week 8 EKS evidence; event publish verification required |
| TC20 | SQS event | Inspect `internship-prod-outbox` | Message accepted with SSE, visibility timeout, retention | Queue and DLQ verified from Week 8 SQS evidence |
| TC21 | Lambda processing | Smoke-test event `lambda-smoke-fixed-1785220478` | Lambda processed event and returned `EMAIL_SENT` | Function and log group partially verified; successful invocation evidence still required |
| TC22 | SES notification | Same smoke-test event | Email send result recorded as `EMAIL_SENT` | Verification required; Week 8 evidence does not prove SES delivery |
| TC23 | S3 event archive | Inspect archive key | `outbox-archive/2026/07/28/lambda-smoke-fixed-1785220478.json` exists | Verification required; Week 8 evidence does not prove archive object creation |
| TC24 | DynamoDB idempotency | Process duplicate event ID | Duplicate is skipped by dedupe table | Implemented, verification required |
| TC25 | Duplicate Lambda event | Re-send same event ID | No second side effect | Implemented, verification required |
| TC26 | DLQ handling | Force consumer failure in controlled test | Message redriven to `internship-prod-outbox-dlq` after max receive count | Proposed |
| TC27 | CloudFront routing correctness | Check distribution behaviors | Default to S3; `/api`, `/chat`, `/socket.io` to ALB | Partially verified from CloudFront monitoring; behavior export or browser smoke proof still required |
| TC28 | Frontend no longer in EKS | `kubectl get deployment frontend -n internship` | Not found | Partially verified from current architecture and EKS workload evidence; explicit command output still useful |

## Manual command set

Run only with approved production access:

```bash
aws eks update-kubeconfig --name internship-prod --region ap-southeast-1
kubectl get deployments,pods,svc,endpoints,hpa,pdb -n internship -o wide
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

AWS service checks:

```bash
aws dynamodb describe-table --table-name ChatUsers --region ap-southeast-1
aws dynamodb describe-table --table-name ChatGroups --region ap-southeast-1
aws dynamodb describe-table --table-name ChatMessages --region ap-southeast-1
aws elasticache describe-replication-groups --replication-group-id internship-prod-redis --region ap-southeast-1
aws sqs get-queue-url --queue-name internship-prod-outbox --region ap-southeast-1
aws lambda get-function --function-name internship-outbox-handler --region ap-southeast-1
aws sagemaker describe-endpoint --endpoint-name internship-qwen3-4b --region ap-southeast-1
```

## Request examples

Backend health:

```bash
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
```

Chat health:

```bash
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

AI health through port-forward:

```bash
kubectl port-forward service/ai-service 18082:8010 -n internship
curl -fsS http://127.0.0.1:18082/health/ready
```

## Database result checks

Do not publish database credentials or raw personal data. Use application APIs, migration logs, and aggregate checks where possible.

Useful production-safe checks:

```bash
kubectl logs job/backend-migrate -n internship --tail=100
kubectl logs deployment/backend-processing-worker -n internship --tail=100
kubectl logs deployment/backend-outbox-dispatcher -n internship --tail=100
```

## Storage result checks

Frontend bucket:

```bash
aws s3 ls s3://internship-prod-frontend-<AWS_ACCOUNT_ID>/ --region ap-southeast-1
```

Event archive:

```bash
aws s3 ls s3://internship-prod-uploads-<AWS_ACCOUNT_ID>/outbox-archive/2026/07/28/ --region ap-southeast-1
```

## CloudWatch log checks

Lambda:

```bash
aws logs tail /aws/lambda/internship-outbox-handler --since 1h --region ap-southeast-1
```

EKS workload CloudWatch log group names require evidence from log shipping configuration before being listed as deployed.

## Expected result

The platform is accepted for demonstration when critical public health checks pass, EKS workloads are Ready, DynamoDB/Redis/SQS/Lambda/SageMaker resources are available, and the Lambda smoke-test path has exported proof for event processing, archive, and email result.

## Common errors

| Symptom | Likely cause | Resolution |
|---|---|---|
| Health check passes through ALB but fails through CloudFront | CloudFront behavior or origin configuration issue | Inspect CloudFront distribution behaviors |
| Chat test fails after scaling | Redis adapter or ALB stickiness issue | Verify Redis readiness and target group stickiness |
| Duplicate application creates two records | Missing DB unique constraint or idempotency bug | Run backend idempotency tests and inspect constraints |
| Worker jobs stay queued | Worker disabled or SageMaker not ready | Verify `PROCESSING_WORKER_ENABLED`, `ai-service`, and endpoint status |
| Lambda smoke test fails with DynamoDB reserved word | `result` used directly in UpdateExpression | Use `#result` and `ExpressionAttributeNames` mapping |

## Outcome

The E2E test plan is evidence-aware. It avoids marking tests passed solely because code exists and records which runtime checks still require exported evidence.
