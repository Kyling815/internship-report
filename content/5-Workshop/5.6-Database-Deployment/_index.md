---
title: "Database Deployment"
date: 2024-01-01
weight: 6
chapter: false
pre: " <b> 5.6. </b> "
---

## Objective

Deploy and verify the data layer used by the Internship Application Tracker: RDS PostgreSQL, ElastiCache Redis, DynamoDB chat tables, and DynamoDB Lambda idempotency table.

## Architecture context

Different data stores are used for different access patterns:

| Store | Purpose |
|---|---|
| RDS PostgreSQL | Users, companies, jobs, applications, workflow history, idempotency records, async processing jobs, transactional outbox |
| ElastiCache Redis | Socket.IO pub/sub between multiple chat pods |
| DynamoDB chat tables | Permanent chat users, groups, and messages |
| DynamoDB dedupe table | Lambda consumer idempotency for SQS events |
| S3 | File storage and event archives, covered in infrastructure/frontend chapters |

## PostgreSQL deployment

The production RDS identifier is `internship-prod-postgres`. PostgreSQL stores transactional business data and all database-backed worker queues.

Evidence required:

- DB instance class
- allocated storage
- storage encryption status
- backup retention
- Multi-AZ setting
- subnet group name
- security group IDs
- deletion protection setting

Verification:

```bash
aws rds describe-db-instances \
  --db-instance-identifier internship-prod-postgres \
  --region ap-southeast-1
```

Check subnet groups:

```bash
aws rds describe-db-subnet-groups --region ap-southeast-1
```

## Alembic migrations

The backend uses Alembic migrations in `backend/alembic/versions/`. Important migrations include:

| Migration | Purpose |
|---|---|
| `0004_idempotency_records.py` | Idempotency records |
| `0005_idempotency_status_check.py` | Bounded idempotency statuses |
| `0006_job_application_versions.py` | Optimistic version fields |
| `0007_outbox_events.py` | Transactional outbox |
| `0008_async_processing_jobs.py` | Async processing queue |
| `1065bcf66cb9_0007_add_rerank_run_tables.py` | Rerank run tables |

The EKS deployment creates a Kubernetes Job named `backend-migrate` that runs:

```bash
alembic upgrade head
```

Manual verification from the repository root:

```bash
cd backend
alembic current
alembic heads
alembic history --verbose
```

Do not run migrations against production unless the deployment window and rollback plan are approved.

## PostgreSQL connection configuration

The production deployment provides `DATABASE_URL` through the Kubernetes Secret `internship-secrets`. The actual connection string is secret, so I do not print it in the documentation.

Kubernetes verification without exposing the value:

```bash
kubectl get secret internship-secrets -n internship
kubectl describe secret internship-secrets -n internship
```

Backend readiness verifies PostgreSQL by executing `SELECT 1`:

```bash
kubectl port-forward service/backend 18080:8000 -n internship
curl -fsS http://127.0.0.1:18080/health/ready
```

Expected response:

```json
{"status":"ready","service":"internship-api","dependencies":{"postgres":true}}
```

## ElastiCache Redis

The production Redis replication group is `internship-prod-redis`, and I verified it as `available` in the Week 8 evidence. Redis is used by the Socket.IO adapter so chat events can be broadcast between multiple chat pods.

Verification:

```bash
aws elasticache describe-replication-groups \
  --replication-group-id internship-prod-redis \
  --region ap-southeast-1
```

The chat service reads `REDIS_URL` from `internship-secrets`. In production, Redis must be reachable from chat pods and should not be exposed publicly.

## DynamoDB chat tables

The chat service uses three DynamoDB tables:

- `ChatUsers`
- `ChatGroups`
- `ChatMessages`

I verified all three chat tables as `ACTIVE` in the Week 8 evidence. The chat service readiness endpoint depends on both DynamoDB and Redis:

```bash
kubectl port-forward service/chat-service 18081:3000 -n internship
curl -fsS http://127.0.0.1:18081/health/ready
```

Expected response when dependencies are ready:

```json
{"status":"ready","dependencies":{"redis":true,"dynamodb":true}}
```

DynamoDB verification:

```bash
aws dynamodb describe-table --table-name ChatUsers --region ap-southeast-1
aws dynamodb describe-table --table-name ChatGroups --region ap-southeast-1
aws dynamodb describe-table --table-name ChatMessages --region ap-southeast-1
```

## DynamoDB Lambda dedupe table

The Lambda SQS consumer uses `InternshipLambdaEventDedupe` to store processed `eventId` values. This protects the Lambda side from duplicate SQS delivery.

Verification:

```bash
aws dynamodb describe-table \
  --table-name InternshipLambdaEventDedupe \
  --region ap-southeast-1
```

For the successful smoke-test event:

```bash
aws dynamodb get-item \
  --table-name InternshipLambdaEventDedupe \
  --key '{"eventId":{"S":"lambda-smoke-fixed-1785220478"}}' \
  --region ap-southeast-1
```

The report should not claim this command was run unless the output is exported as evidence.

## Data consistency design

| Concern | Mechanism |
|---|---|
| Duplicate registration | PostgreSQL unique constraints and 409 handling |
| Duplicate candidate apply | Unique `(job_posting_id, candidate_user_id)` and `Idempotency-Key` |
| Stale HR updates | `expectedVersion` and conditional updates |
| Long AI jobs | `async_processing_jobs` table with leases and retries |
| Lost event publication | `outbox_events` committed with business mutation |
| Duplicate SQS delivery | Lambda DynamoDB conditional write by `eventId` |
| Duplicate chat message retry | DynamoDB conditional create with `clientMessageId` |

## Commands

Check Kubernetes data-related configuration:

```bash
kubectl get configmap internship-config -n internship -o yaml
kubectl get secret internship-secrets -n internship
kubectl get job backend-migrate chat-init -n internship
kubectl logs job/backend-migrate -n internship
kubectl logs job/chat-init -n internship
```

Check application tables through application health:

```bash
kubectl rollout status deployment/backend -n internship --timeout=300s
kubectl rollout status deployment/chat-service -n internship --timeout=300s
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

## Expected result

- `backend-migrate` completes successfully.
- Backend readiness returns PostgreSQL dependency `true`.
- Chat readiness returns Redis and DynamoDB dependencies `true`.
- DynamoDB chat tables are `ACTIVE`.
- Redis replication group is `available`.
- Lambda dedupe table exists and supports conditional writes.

## Common errors

| Symptom | Root cause | Resolution |
|---|---|---|
| Backend readiness fails | Wrong `DATABASE_URL`, security group issue, migration failure | Inspect backend logs and RDS security groups |
| Alembic fails to parse URL | Shell interpolation or secret formatting problem | Store URL as a secret and avoid printing it |
| Chat readiness returns `not_ready` | Redis adapter or DynamoDB initialization failure | Inspect `chat-service` logs and `chat-init` job |
| Duplicate Lambda event sends email twice | Dedupe table write is missing or not conditional | Use DynamoDB conditional write keyed by `eventId` |
| Outbox rows stay pending | Dispatcher cannot publish to SQS | Check `OUTBOX_QUEUE_URL`, IRSA SQS policy, dispatcher logs |

## Troubleshooting

Use these commands during incidents:

```bash
kubectl logs deployment/backend -n internship --tail=200
kubectl logs deployment/chat-service -n internship --tail=200
kubectl logs deployment/backend-outbox-dispatcher -n internship --tail=200
kubectl logs deployment/backend-processing-worker -n internship --tail=200
aws rds describe-db-instances --db-instance-identifier internship-prod-postgres --region ap-southeast-1
aws elasticache describe-replication-groups --replication-group-id internship-prod-redis --region ap-southeast-1
aws dynamodb describe-table --table-name ChatMessages --region ap-southeast-1
```

## Outcome

The database layer is ready when PostgreSQL migrations have completed, Redis is available to chat pods, DynamoDB chat tables are active, Lambda dedupe is configured, and application readiness checks pass through the deployed routing path.
