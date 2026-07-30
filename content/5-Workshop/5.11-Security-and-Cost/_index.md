---
title: "Security and Cost"
date: 2024-01-01
weight: 11
chapter: false
pre: " <b> 5.11. </b> "
---

## Objective

Document the security controls and cost-estimation approach for the production AWS deployment.

## Architecture context

The platform processes user accounts, CVs, job applications, chat messages, AI analysis, event notifications, and email. Security controls must protect identity, secrets, private data, deployment roles, storage, network paths, and event processing. Cost controls must pay special attention to always-on resources such as EKS, NAT Gateway, RDS, Redis, ALB, and SageMaker.

## Security controls

| Area | Implemented or required control | Status |
|---|---|---|
| GitHub OIDC | GitHub Actions assumes AWS role through OIDC with `id-token: write` | Implemented in workflow |
| Long-lived AWS keys | Do not store long-lived AWS access keys in GitHub or source code | Required control |
| IAM least privilege | Deployment, runtime, node, SageMaker, Lambda, and ALB controller roles should be scoped | Implemented concept; policy evidence required |
| IRSA | EKS ServiceAccount `internship-app` can be annotated with runtime role | Implemented in deployment script |
| Kubernetes secrets | `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `OUTBOX_QUEUE_URL`, and optional AI key injected as `internship-secrets` | Implemented in script |
| S3 private frontend bucket | Bucket public access blocked, CloudFront OAC used | Implemented in `ensure-cloudfront.sh`; runtime evidence required |
| CloudFront HTTPS | CloudFront redirects viewers to HTTPS | Implemented in helper config |
| ALB route control | ALB routes only API/chat/socket paths to services | Implemented in Ingress |
| RDS private access | PostgreSQL should not be publicly exposed | Evidence required |
| Redis private access | ElastiCache should not be publicly exposed | Evidence required |
| SQS SSE | Main queue and DLQ use server-side encryption | Verified from Week 8 evidence |
| DynamoDB encryption | DynamoDB tables use AWS-managed encryption by default unless configured otherwise | Evidence required for final table settings |
| RDS encryption | Must be verified with `describe-db-instances` | Evidence required |
| Encryption in transit | CloudFront HTTPS; internal service and database TLS settings require evidence | Partially evidenced |
| Secret handling | No `.env`, token, key, password, or database URL should be committed | Required control |
| DLQ | SQS DLQ isolates failed consumer messages | Verified from Week 8 evidence |
| Idempotency | PostgreSQL idempotency, outbox, chat `clientMessageId`, and Lambda DynamoDB dedupe | Implemented; Lambda smoke verified |
| Backup and PITR | RDS backup and DynamoDB PITR settings require exported evidence | Evidence required |
| Direct ALB access hardening | Restricting ALB origin to CloudFront is recommended | Optional hardening |
| AWS WAF | WAF on CloudFront is recommended for production | Optional hardening |

## Authentication and authorization

The backend uses JWT-based authentication and role-aware routes for candidate and HR workflows. The frontend stores the session under the `internship_tracker_` prefix and clears local/session storage on session expiration. Protected frontend routes redirect users according to role.

Security expectations:

- Passwords must be hashed.
- JWT secret must remain in secrets management, not in source code.
- Candidate and HR routes must enforce ownership and role checks on the backend.
- AI scores should assist review but not become the only hiring decision.

## Data protection

| Data type | Protection requirement |
|---|---|
| CVs and documents | Store in private S3, authorize access, avoid logging full content |
| Applications | Store in PostgreSQL with ownership checks |
| Chat messages | Store in DynamoDB and authorize access through chat service |
| Outbox events | Avoid future sensitive payload logging; archive only intended event content |
| AI prompts | Do not log full CV text; AI service logs prompt hash and character counts |
| Secrets | Keep in GitHub secrets and Kubernetes Secret; never publish values |

## Security verification commands

```bash
aws iam get-role --role-name internship-github-deploy
aws iam get-role --role-name internship-eks-runtime
kubectl get serviceaccount internship-app -n internship -o yaml
kubectl describe secret internship-secrets -n internship
aws s3api get-public-access-block --bucket <FRONTEND_BUCKET_NAME>
aws sqs get-queue-attributes --queue-url <OUTBOX_QUEUE_URL> --attribute-names All --region ap-southeast-1
aws rds describe-db-instances --db-instance-identifier internship-prod-postgres --region ap-southeast-1
```

I do not print or paste secret values from Kubernetes, GitHub, or AWS into the documentation.

## Cost evidence source

I report cost data from the Week 8 AWS cost evidence. The evidence records July 1-28, 2026 month-to-date spend and a Billing and Cost Management credits screenshot. The finalized monthly bill and AWS Pricing Calculator estimate remain pending.

| Cost evidence | Observed value | Interpretation |
|---|---|---:|---|
| July 1-28, 2026 total spend | Current month-to-date cost | `$94.92` | Source-of-truth Week 8 cost summary |
| Highest daily spend | July 28, 2026 | `$31.83` | Largest daily spend in the July 1-28 period |
| Credits total amount used | Billing credits | `$27.90` | Billing credits screenshot |
| Credits total estimated amount used | Billing credits | `$140.65` | Billing credits screenshot |
| Credits total amount remaining | Billing credits | `$172.10` | Billing credits screenshot |
| Credits total estimated amount remaining | Billing credits | `$59.35` | Billing credits screenshot |

These values cover the July 1-28 period only. I do not treat them as the finalized monthly bill or steady-state production estimate until AWS Bills and AWS Pricing Calculator evidence are attached.

## Observed Week 8 service cost

The Week 8 cost summary identifies the following top cost drivers for July 1-28, 2026.

| Rank | Service | July 1-28 cost | Share of total |
|---:|---|---:|---:|
| 1 | Amazon RDS | `$29.69` | 31.3% |
| 2 | Amazon SageMaker | `$23.45` | 24.7% |
| 3 | Amazon VPC | `$14.11` | 14.9% |
| 4 | Amazon EC2 - Compute | `$12.42` | 13.1% |
| 5 | EC2 - Other | `$7.68` | 8.1% |
| 6 | Amazon EKS | `$5.64` | 5.9% |

These six services account for approximately 98% of the July 1-28 reported spend. The July 28 daily cost spike indicates that new production infrastructure, SageMaker endpoint uptime, and VPC/NAT-related networking should be monitored closely.

## Cost assumptions

Exact future monthly cost still requires AWS Pricing Calculator or a representative Cost Explorer period. The deployed configuration observed in the evidence folder is:

| Cost driver | Observed configuration | Monthly estimate input still required |
|---|---|---|
| EKS control plane | One production cluster in `ap-southeast-1` | Cluster runtime hours and current regional EKS hourly price |
| EC2 worker nodes | Two Ready Kubernetes worker nodes | Node instance type, EBS size, runtime hours |
| RDS PostgreSQL | Two private, encrypted PostgreSQL `db.t4g.micro` instances, 20 GiB each, Single-AZ | Backup storage, additional I/O, representative runtime |
| ElastiCache / Valkey | One available replication group with encryption at rest and in transit | Node type, node count, data transfer |
| Application Load Balancer | One active internet-facing ALB | ALB runtime hours and LCU usage |
| CloudFront | Application distribution plus report distribution evidence | Request count, data transfer out, invalidations, behavior export |
| S3 | Frontend bucket object evidence plus upload/archive/report bucket context | Storage GB, PUT/GET requests, lifecycle policy |
| DynamoDB | Chat and Lambda dedupe tables use on-demand billing in the Week 8 screenshot | Read/write request volume, storage, PITR if enabled |
| SQS | Main queue and DLQ had zero visible messages in the Week 8 screenshot | Request volume and payload size |
| Lambda | Outbox handler is Active, 256 MB memory, 20 second timeout | Invocations, average duration, errors/retries |
| SageMaker | Real-time endpoint is `InService` with one production variant | Instance type, endpoint uptime, data processed |
| CloudWatch | Logs and metrics are enabled through AWS and Kubernetes services | Log ingestion, retention, custom metrics, alarms |
| Data transfer | Cost Explorer shows data transfer adjustment in the captured period | CloudFront egress, ALB traffic, NAT processing, cross-AZ traffic |

## Cost estimation table

| Service | Estimation method | Current evidence status |
|---|---|---|
| Amazon EKS | Cluster hourly charge multiplied by runtime hours | Deployed; Week 8 cost summary reports `$5.64` |
| EC2 worker nodes | Node hourly price times two nodes plus EBS storage | Nodes verified; EC2 Compute reports `$12.42`, EC2 - Other reports `$7.68` |
| Amazon RDS PostgreSQL | `db.t4g.micro` hourly price, 20 GiB storage per instance, backup and I/O | Two private encrypted instances verified; Week 8 cost summary reports `$29.69` |
| Amazon ElastiCache / Valkey | Node hourly price times node count plus data transfer | Replication group verified; node type/count still needed |
| Application Load Balancer | ALB hourly charge plus LCU usage | Active ALB verified; target health still needs final healthy evidence |
| Amazon CloudFront | Requests plus data transfer out and invalidations | Monitoring screenshot available; behavior/origin export still required |
| Amazon S3 | Storage GB plus request volume and lifecycle transitions | Frontend bucket object screenshot available |
| Amazon DynamoDB | On-demand read/write requests plus storage | Table status screenshot available |
| Amazon SQS | Standard queue requests and payload volume | Queue and DLQ screenshot available |
| AWS Lambda | Request count plus GB-seconds | Function exists; invocation and trigger health still pending |
| Amazon SES | Email send count and attachments if any | Service planned through Lambda notification path |
| Amazon ECR | Image storage GB and data transfer if applicable | Not separated in the Week 8 top-driver table |
| Amazon SageMaker | Endpoint instance hours and invocation/data charges | Endpoint verified `InService`; Week 8 cost summary reports `$23.45` |
| Amazon CloudWatch | Log ingestion, retention, metrics, alarms | Retention and ingestion volume still required |
| Amazon VPC and data transfer | CloudFront egress, ALB traffic, NAT, and cross-AZ traffic | Week 8 cost summary reports Amazon VPC at `$14.11`; traffic breakdown still needed |
| Total | Use Pricing Calculator for forecast, then compare with representative billing evidence | Week 8 July 1-28 spend reports `$94.92`; finalized bill and steady-state estimate pending |

## Evidence hygiene

Before I use any AWS evidence image or log in the documentation, I redact AWS account IDs, access keys, secret keys, database passwords, connection strings, Kubernetes Secret values, GitHub tokens, presigned URLs, and logs containing credentials.

My evidence scan did not find obvious access keys or GitHub tokens, but `02-eks/pod-logs-tail.txt` contains a Redis connection URL with an embedded credential from chat-service startup logs. I do not upload or paste that raw file. I use only a summary or replace the whole value with `<REDACTED_REDIS_CONNECTION_STRING>`.

## Largest cost drivers

The highest-risk future cost areas are:

- SageMaker real-time endpoint uptime, especially if the selected endpoint instance is GPU-backed.
- EKS control plane and EC2 worker nodes running continuously.
- RDS and Redis always-on managed capacity.
- ALB hourly and LCU usage.
- CloudFront and data transfer when traffic grows.
- CloudWatch log ingestion and retention if verbose logs are kept.

The Week 8 evidence shows that cost is no longer near zero. SageMaker, RDS, VPC/NAT-related networking, EC2 worker nodes, and EKS should be treated as active cost drivers. SageMaker should be stopped or deleted when demos finish if real-time inference is not required.

## Cost optimization options

| Option | Effect |
|---|---|
| Delete or schedule SageMaker endpoint when idle | Reduces likely largest AI cost driver |
| Keep processing worker disabled when AI testing is not active | Avoids unnecessary retries and worker runtime |
| Right-size EKS node group | Reduces EC2 and EBS cost |
| Scale non-production workloads down after demos | Reduces always-on compute |
| Confirm whether NAT Gateway is required | Avoids NAT hourly and data-processing charges if private egress is not needed |
| Add VPC endpoints where appropriate | Reduces NAT data processing for AWS service traffic |
| S3 lifecycle rules | Move old uploads/archives to cheaper storage or expire test artifacts |
| ECR lifecycle policy | Delete old SHA images after the retention window |
| CloudWatch retention | Avoid indefinite high-volume log storage |
| DynamoDB on-demand during unstable traffic | Avoids over-provisioning early |
| AWS Budget and billing alert | Detects unexpected charges before they become large |

## Expected result

I consider the security and cost section complete when it identifies implemented controls, marks missing evidence clearly, avoids secret exposure, and gives a concrete cost-estimation method without inventing live AWS prices.

## Common errors

| Symptom | Cause | Resolution |
|---|---|---|
| Long-lived AWS key in CI | Static credentials used instead of OIDC | Remove key, rotate it, use OIDC role |
| Direct S3 public access | Bucket policy or public access block misconfigured | Restore public access block and CloudFront OAC policy |
| Lambda duplicate side effects | Missing event dedupe | Use DynamoDB conditional writes by `eventId` |
| Unexpected high bill | SageMaker/NAT/EKS left running | Check Cost Explorer and stop/delete idle high-cost resources |
| Cost table has fake totals | Pricing not exported | Use `Pricing evidence required` until AWS Pricing Calculator is attached |

## Outcome

The deployment follows an evidence-based security model and a practical cost model. Remaining security and cost facts require AWS CLI, Cost Explorer, or AWS Pricing Calculator exports before final numeric claims are made.
