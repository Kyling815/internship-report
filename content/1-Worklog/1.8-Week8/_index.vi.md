---
title: "Nhật ký tuần 8"
date: 2024-01-01
weight: 8
chapter: false
pre: " <b> 1.8. </b> "
---

# Tuần 8 - Triển khai end-to-end và kiểm tra vận hành

## Mục tiêu

Trong tuần 8, tôi hoàn thiện phần đóng góp Cloud/DevOps của mình trong project nhóm 5 thành viên. Tôi tích hợp và kiểm tra mô hình production cho các service của nhóm trên Amazon EKS, Application Load Balancer, S3/CloudFront, các dịch vụ dữ liệu AWS managed, event-driven processing và cost tracking.

Tôi sử dụng thư mục minh chứng AWS tuần 08 làm nguồn dữ liệu cho phần này. Số liệu chi phí lấy từ tổng hợp ngày 01-28/07/2026, screenshot Billing credits và Cost Explorer. Hóa đơn tháng đã chốt và AWS Pricing Calculator vẫn chưa có.

## Phần việc cá nhân

| Trạng thái | Phần việc được phân công | Cơ sở minh chứng |
|---|---|---|
| Hoàn thành | Tích hợp AI service theo hướng SageMaker do thành viên AI cung cấp vào deployment path. | Source implementation và `sagemaker-health.png`. |
| Hoàn thành | Sửa image propagation của `deploy-app` và cách chọn ECR image xác định. | CI/CD workflow implementation. |
| Hoàn thành | Loại frontend khỏi Kubernetes runtime để phân phối qua S3 và CloudFront. | Deployment script và architecture note. |
| Hoàn thành | Kiểm tra trạng thái Amazon RDS PostgreSQL và ElastiCache Valkey từ screenshot AWS CLI. | `RDS-health.png`, `REDIS-health.png`. |
| Hoàn thành | Kiểm tra trạng thái SageMaker endpoint. | `sagemaker-health.png`. |
| Hoàn thành một phần | Kiểm tra EKS workload và ALB runtime. | EKS workload chạy nhưng screenshot ALB còn target không healthy. |
| Hoàn thành | Bổ sung minh chứng runtime CloudFront, S3, DynamoDB và SQS. | Các screenshot đã được xử lý thông tin nhạy cảm. |
| Hoàn thành một phần | Bổ sung minh chứng chi phí AWS ngày 01-28/07/2026. | Cost summary và screenshot; Pricing Calculator còn bị chặn. |

## Triển khai kỹ thuật

The final deployment model separates static frontend hosting from long-running service workloads. Backend, chat, worker, and AI services run on EKS. Static browser assets are intended to be served through S3 and CloudFront, while API, chat, and Socket.IO paths route through the ALB.

{{< mermaid >}}
graph LR
  Browser["User browser"] --> CF["CloudFront distribution"]
  CF --> S3["S3 frontend bucket"]
  CF --> ALB["ALB for /api, /chat, /socket.io"]
  ALB --> Backend["EKS backend"]
  ALB --> Chat["EKS chat-service"]
  Backend --> RDS["RDS PostgreSQL"]
  Chat --> Redis["ElastiCache Valkey"]
  Chat --> DDB["DynamoDB chat tables"]
  Backend --> Worker["processing worker"]
  Worker --> AI["ai-service"]
  AI --> SageMaker["SageMaker endpoint"]
  Backend --> Outbox["outbox dispatcher"]
  Outbox --> SQS["SQS queue"]
  SQS --> Lambda["Lambda notification handler"]
{{< /mermaid >}}

The CI/CD workflow supports deployment modes including `validate`, `deploy-app`, `deploy-public`, `deploy-frontend`, `rollout`, and `full`. Backend, chat, and AI images are tagged with the GitHub commit SHA. The frontend deployment path builds the Vite app, publishes static files to S3, and invalidates CloudFront when frontend deployment is enabled.

## Minh chứng vận hành AWS

The runtime evidence below uses only files that I placed in the Week 08 AWS evidence directory. I reviewed the following files:

- `ALB-target-health.png`
- `ALB-target.png`
- `Cloudfront-evidence.png`
- `Cost-evidence.png`
- `DynamoDB-evidenc.png`
- `eks-deployment-rollout-success.png`
- `eks-runtime-pods-2026-07-28.png`
- `lambda.png`
- `Lambda-evidence.png`
- `lambda-cloudwatch-evidence.png`
- `RDS-health.png`
- `REDIS-health.png`
- `S3-evidenc.png`
- `sagemaker-health.png`
- `SQS-evidence.png`
- `total-cost-july.png`

I did not find `.txt`, `.log`, `.json`, `.yaml`, or `.yml` evidence files in this directory, so I did not include long CLI log excerpts.

### Tổng hợp minh chứng vận hành

| AWS service | Evidence status | Runtime status | Evidence |
|---|---|---|---|
| Amazon EKS | Available | Partially verified: nodes, pods, jobs, and deployments were healthy; cluster `ACTIVE` status was not directly captured | `eks-runtime-pods-2026-07-28.png`, `eks-deployment-rollout-success.png` |
| Application Load Balancer | Available | Partially operational: load balancer was active and target groups existed, but target health was mixed and included unhealthy targets | `ALB-target-health.png`, `ALB-target.png` |
| Amazon CloudFront | Available | Partially verified: I captured monitoring metrics for requests, data transfer, and distribution error rates | `Cloudfront-evidence.png` |
| Amazon S3 | Available | Verified frontend bucket objects after account-suffix redaction | `S3-evidenc.png` |
| Amazon RDS | Available | Available | `RDS-health.png` |
| Amazon ElastiCache | Available | Available | `REDIS-health.png` |
| Amazon DynamoDB | Available | Verified: chat tables and Lambda dedupe table are Active and on-demand | `DynamoDB-evidenc.png` |
| Amazon SQS | Available | Verified: main queue and DLQ exist, show zero visible/in-flight messages, and use SSE-SQS | `SQS-evidence.png` |
| AWS Lambda | Available | Partially verified: function configuration, source view, and CloudWatch log group exist; invocation result still not verified | `lambda.png`, `Lambda-evidence.png`, `lambda-cloudwatch-evidence.png` |
| Amazon SageMaker | Available | InService | `sagemaker-health.png` |

### Amazon EKS

**Evidence status:** Available
**Runtime status:** Partially verified

I verified two Ready worker nodes, running application pods, completed migration/init jobs, and ready deployments in the `internship` namespace. The visible workloads include `ai-service`, `backend`, `backend-outbox-dispatcher`, `backend-processing-worker`, and `chat-service`.

The same evidence confirms deployment readiness:

- `ai-service`: 1/1 ready
- `backend`: 2/2 ready
- `backend-outbox-dispatcher`: 1/1 ready
- `backend-processing-worker`: 1/1 ready
- `chat-service`: 2/2 ready

I did not capture an `aws eks describe-cluster` output showing the EKS cluster status as `ACTIVE`. For that reason, I classify EKS as partially verified instead of claiming that full cluster-level evidence was captured.

![Amazon EKS runtime pods and services](/logs/worklog/week-08/aws/eks-runtime-pods-2026-07-28.png)

![Amazon EKS deployment rollout success](/logs/worklog/week-08/aws/eks-deployment-rollout-success.png)

### Application Load Balancer

**Evidence status:** Available
**Runtime status:** Partially operational

I captured an internet-facing Application Load Balancer in `active` state. However, the target health evidence still shows mixed target status:

- One backend target on port `8000` was healthy.
- Another backend target on port `8000` was unhealthy with failed health checks.
- Chat targets on port `3000` were unhealthy with timeout or failed health-check reasons.

Because of the unhealthy targets, I do not classify the ALB as fully healthy. The load balancer was deployed, active, and associated with target groups, but the target groups still require follow-up validation and remediation.

![Application Load Balancer target health](/logs/worklog/week-08/aws/ALB-target-health.png)

![Application Load Balancer target groups](/logs/worklog/week-08/aws/ALB-target.png)

### Amazon CloudFront và S3

**Evidence status:** Available
**Runtime status:** Partially verified

I captured CloudFront monitoring metrics for distribution `EQIGYNECXDYL8`, including requests, data transfer, and error-rate graphs over the selected three-day window. This confirms that the distribution was receiving telemetry.

I captured the frontend S3 bucket object listing after redacting the bucket name. The visible objects include `assets/`, `favicon.svg`, and `index.html`, which verifies that static frontend assets were present in S3.

These screenshots support frontend hosting evidence, but they do not replace a full CloudFront behavior/origin configuration export or a browser smoke test through the CloudFront URL.

![CloudFront monitoring evidence](/logs/worklog/week-08/aws/Cloudfront-evidence.png)

![S3 frontend bucket object evidence](/logs/worklog/week-08/aws/S3-evidenc.png)

### Amazon RDS

**Evidence status:** Available
**Runtime status:** Available

I verified the PostgreSQL database instance `internship-prod-postgres` in status `available`. The captured output also includes PostgreSQL engine metadata, encrypted storage, non-public accessibility, and allocated storage.

![Amazon RDS PostgreSQL health](/logs/worklog/week-08/aws/RDS-health.png)

### Amazon ElastiCache

**Evidence status:** Available
**Runtime status:** Available

I verified the ElastiCache replication group `internship-prod-redis` with Valkey engine status `available`. The captured evidence also confirms encryption at rest and in transit.

![Amazon ElastiCache Valkey health](/logs/worklog/week-08/aws/REDIS-health.png)

### Amazon DynamoDB

**Evidence status:** Available
**Runtime status:** Verified Active

I verified four DynamoDB tables in `Active` status:

- `ChatGroups`
- `ChatMessages`
- `ChatUsers`
- `InternshipLambdaEventDedupe`

The captured table list also shows on-demand read and write capacity mode. This verifies that the AWS DynamoDB tables existed and were active at the time of evidence collection.

![DynamoDB table status evidence](/logs/worklog/week-08/aws/DynamoDB-evidenc.png)

### Amazon SQS

**Evidence status:** Available
**Runtime status:** Verified available

I verified two Amazon SQS standard queues:

- `internship-prod-outbox`
- `internship-prod-outbox-dlq`

Both queues had zero visible messages and zero in-flight messages in the captured evidence. The queues use Amazon SQS managed server-side encryption.

![SQS queue evidence](/logs/worklog/week-08/aws/SQS-evidence.png)

### AWS Lambda

**Evidence status:** Available
**Runtime status:** Partially verified

I verified a Lambda function named `internship-outbox-handler` with a Python runtime and environment configuration. This confirms that the function existed in the selected AWS region.

The screenshot was sanitized before publication by redacting account-scoped ARNs, the IAM role ARN account segment, the bucket value containing an account identifier, and the sender email address.

Additional Lambda evidence captures the function source view and a CloudWatch log group named `/aws/lambda/internship-outbox-handler`. These items confirm that the function code view and log group existed. They do not prove a successful invocation, SQS trigger execution, or SES delivery result, so I keep Lambda runtime execution as partially verified.

![AWS Lambda function configuration](/logs/worklog/week-08/aws/lambda.png)

![AWS Lambda source evidence](/logs/worklog/week-08/aws/Lambda-evidence.png)

![AWS Lambda CloudWatch log group evidence](/logs/worklog/week-08/aws/lambda-cloudwatch-evidence.png)

### Amazon SageMaker

**Evidence status:** Available
**Runtime status:** InService

I verified the SageMaker endpoint `internship-qwen3-4b` in status `InService`. This is sufficient to show that the endpoint existed and was serving at the time of evidence collection.

![Amazon SageMaker endpoint status](/logs/worklog/week-08/aws/sagemaker-health.png)

## Minh chứng chi phí AWS

> **Status: Partially available**

The July 1-28, 2026 AWS cost summary reported a month-to-date spend of **$94.92**. I also included a Billing and Cost Management credits screenshot stored as `total-cost-july.png` and a Cost Explorer overview screenshot stored as `Cost-evidence.png`.

The credits screenshot records AWS credits rather than a grouped Cost Explorer service chart. The Cost Explorer screenshot is useful as a billing-console overview, but it uses a different report configuration and is not a Pricing Calculator estimate. Therefore, I keep the service-level cost breakdown tied to the July 1-28 cost summary.

![AWS Billing credits summary for July 2026](/logs/worklog/week-08/aws/total-cost-july.png)

![AWS Cost Explorer overview evidence](/logs/worklog/week-08/aws/Cost-evidence.png)

### Tổng hợp chi phí từ ngày 1 đến 28 tháng 7

| Metric | Reported value |
|---|---:|
| Total spend, July 1-28 | $94.92 |
| Highest daily spend | $31.83 on July 28 |
| AWS credits total amount used | $27.90 |
| AWS credits total estimated amount used | $140.65 |
| AWS credits total amount remaining | $172.10 |
| AWS credits total estimated amount remaining | $59.35 |

### Xu hướng chi phí hằng ngày

| Period | Daily spend |
|---|---:|
| July 1-8 | Approximately $2.20/day |
| July 9-25 | Approximately $1.60/day |
| July 26 | $5.61 |
| July 27 | $11.60 |
| July 28 | $31.83 |

The July 28 daily cost was the largest reported daily spend in the July 1-28 period and was much higher than the earlier baseline.

### Các dịch vụ phát sinh chi phí cao nhất

| Rank | Service | Month-to-date cost | Share of total |
|---:|---|---:|---:|
| 1 | Amazon RDS | $29.69 | 31.3% |
| 2 | Amazon SageMaker | $23.45 | 24.7% |
| 3 | Amazon VPC | $14.11 | 14.9% |
| 4 | Amazon EC2 - Compute | $12.42 | 13.1% |
| 5 | EC2 - Other | $7.68 | 8.1% |
| 6 | Amazon EKS | $5.64 | 5.9% |

These six services account for approximately 98% of the July 1-28 reported spend.

### Các bất thường về chi phí

Five active anomalies were reported around July 26-28 in `ap-southeast-1`:

| Service | Anomaly impact | Reported context |
|---|---:|---|
| Amazon EBS | +$6.02, +15,050% versus expected | NAT Gateway activity in `ap-southeast-1` |
| Amazon EC2 - Compute | +$2.56, +400% versus expected | New `t3.medium` instances in `ap-southeast-1` |
| Amazon RDS | +$1.12, +138% versus expected | New `db.t4g.micro` instance activity in `ap-southeast-1` |
| Amazon VPC | +$0.47, +98% versus expected | VPC/NAT Gateway infrastructure in `ap-southeast-1` |
| AWS Secrets Manager | +$0.01, +50% versus expected | Minor secret-management cost tied to new infrastructure |

| Cost evidence | Status | Reported value |
|---|---|---:|
| July 1-28 cost summary | Available | $94.92 |
| AWS Billing credits screenshot | Available | $27.90 total amount used; $140.65 total estimated amount used |
| Cost Explorer overview screenshot | Available | Included as console evidence; not used as the final service-level breakdown |
| AWS Bills finalized monthly invoice | Pending | Not available |
| AWS Pricing Calculator | Blocked | Not available |
| Actual month-to-date cost | Reported for July 1-28 | $94.92 |
| Estimated monthly cost | Not calculated | N/A |

## Kết quả kiểm thử, build và triển khai

| Area | Result | Evidence |
|---|---|---|
| EKS workload rollout | Partially verified | I captured successful rollout output for all listed deployments. |
| EKS runtime pods and services | Partially verified | I captured Ready nodes, Running pods, Completed jobs, ready deployments, and services/ingress. |
| ALB deployment | Partially operational | I captured ALB state `active`, but target health still includes unhealthy targets. |
| RDS PostgreSQL | Verified available | I captured RDS status `available`. |
| ElastiCache Valkey | Verified available | I captured ElastiCache status `available`. |
| SageMaker endpoint | Verified InService | I captured SageMaker endpoint status `InService`. |
| Lambda function listing | Partially verified | Screenshots confirm function configuration, source view, and CloudWatch log group; invocation and trigger health are not verified. |
| CloudFront and S3 frontend delivery | Partially verified | CloudFront monitoring and S3 object listing screenshots are available; full behavior/origin export and browser smoke proof remain pending. |
| DynamoDB and SQS | Verified available | DynamoDB tables are Active; SQS main queue and DLQ are listed with zero messages and SSE-SQS. |
| Cost evidence | Partially available | July 1-28 cost summary, credits screenshot, and Cost Explorer overview are available; finalized bill and Pricing Calculator remain pending/blocked. |

## Vấn đề và giải pháp

### Các nhóm đích ALB chưa hoàn toàn khỏe mạnh

**Problem:**
I captured the load balancer in `active` state, but target health still included unhealthy backend and chat targets.

**Impact:**
API or chat traffic through the public ALB could fail intermittently or return gateway errors until every required target group becomes healthy.

**Current resolution:**
I classify the ALB as partially operational rather than fully healthy.

**Next action:**
Collect updated target health evidence after fixing health-check failures or deployment readiness issues.

### Minh chứng chi phí AWS đã có nhưng chưa đầy đủ

**Problem:**
A July 1-28 cost summary and credits screenshot are available, but the evidence set still does not include a finalized monthly bill or AWS Pricing Calculator estimate.

**Impact:**
I can show the July 1-28 month-to-date spend and major cost drivers, but I cannot conclude the final monthly bill or steady-state monthly cost yet.

**Current resolution:**
I classify cost evidence as partially available, report only the July 1-28 figures, and keep monthly estimate fields pending.

**Next action:**
Collect the finalized AWS Bills view and build an AWS Pricing Calculator estimate for the production architecture.

### Đã bổ sung minh chứng vận hành cho một số dịch vụ AWS

**Problem:**
The first Week 8 evidence set did not include CloudFront, S3, DynamoDB, or SQS screenshots.

**Impact:**
Without screenshots or sanitized CLI output, I could not classify those services as runtime evidenced.

**Current resolution:**
Sanitized screenshots were added for CloudFront monitoring, the S3 frontend bucket object list, DynamoDB table status, and SQS queue status.

**Next action:**
For final production evidence, add CloudFront behavior/origin configuration export and a browser smoke test through the CloudFront URL.

### Ảnh chụp Lambda cần được xử lý thông tin nhạy cảm

**Problem:**
The Lambda screenshot contained account-scoped ARNs, an IAM role ARN, a bucket name containing an account identifier, and an email address.

**Impact:**
Embedding the screenshot directly would publish sensitive or semi-sensitive operational values.

**Current resolution:**
I sanitized and embedded the screenshot as Lambda deployment evidence. It confirms the function listing/configuration, but not invocation success.

**Next action:**
Collect a separate invocation, trigger, or CloudWatch event-detail screenshot if Lambda runtime execution must be marked fully verified.

## Kết quả trong tuần

Phần đóng góp cá nhân tuần 8 tạo được bộ minh chứng AWS runtime cho compute và data path chính:

- EKS workloads were running and deployments had rolled out.
- I verified RDS PostgreSQL as available.
- I verified ElastiCache Valkey as available.
- CloudFront monitoring and S3 frontend object evidence were added.
- DynamoDB tables and SQS queues were verified from AWS console screenshots.
- SageMaker endpoint evidence showed `InService`.
- Sanitized Lambda evidence confirms the function, source view, and CloudWatch log group, while invocation proof remains pending.

Ứng dụng end-to-end vẫn là kết quả chung của nhóm. Trong phạm vi của tôi, các khoảng trống còn lại được ghi rõ: ALB target chưa hoàn toàn healthy, còn thiếu CloudFront behavior/origin export và browser smoke test, đồng thời số liệu chi phí cần hóa đơn đã chốt và Pricing Calculator.

## Công việc còn lại

- [x] Add the July 1-28 AWS cost summary.
- [x] Add the AWS Billing credits screenshot.
- [x] Add a Cost Explorer overview screenshot.
- [ ] Capture the finalized AWS Billing summary.
- [ ] Build an AWS Pricing Calculator estimate. This is currently blocked.
- [x] Capture CloudFront monitoring evidence.
- [x] Capture S3 frontend bucket object evidence.
- [x] Capture Amazon DynamoDB table status evidence.
- [x] Capture Amazon SQS queue and message-count evidence.
- [ ] Capture updated ALB target health after every required target is healthy.
- [ ] Capture CloudFront behavior/origin configuration or browser smoke proof.
- [x] Add a sanitized Lambda screenshot.

## Bài học rút ra

Implementation evidence and runtime evidence answer different questions. A deployment script proves that a path exists in source control, but screenshots, AWS CLI output, and health checks prove what actually ran in AWS.

Cost reporting needs the same discipline. The July 1-28 summary is useful month-to-date evidence, but the final monthly bill and steady-state monthly estimate still require separate billing and Pricing Calculator evidence.
