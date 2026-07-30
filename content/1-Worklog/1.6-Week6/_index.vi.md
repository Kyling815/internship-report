---
title: "Nhật ký tuần 6"
date: 2024-01-01
weight: 6
chapter: false
pre: " <b> 1.6. </b> "
---

# Tuần 6 - Nền tảng AWS, IAM, OIDC và ECR

## Mục tiêu

Trong nhóm 5 thành viên, mục tiêu tuần 6 của tôi là chuẩn bị nền tảng triển khai AWS dùng chung: region, xác thực GitHub OIDC, quyền IAM, ECR repository và CI job đẩy image của các service mà không sử dụng access key dài hạn.

## Phần việc cá nhân

| Trạng thái | Phần việc được phân công | Cơ sở minh chứng |
|---|---|---|
| Hoàn thành | Chuẩn hóa production region là `ap-southeast-1`. | Project context, CI/CD workflow và deployment script. |
| Hoàn thành | Bổ sung GitHub OIDC smoke workflow. | Commit `2777b56`. |
| Hoàn thành | Bổ sung workflow build và push application image lên ECR. | Commit `9f9fcf3`. |
| Hoàn thành | Đồng bộ AWS deployment workflow với production architecture. | Commit `7eb1a76`. |
| Hoàn thành | Bổ sung EKS access smoke-test workflow. | Commit `bfacd3a`. |
| Hoàn thành một phần | Thu thập IAM policy simulation, ECR digest và screenshot GitHub Actions hiện có. | Cần bổ sung minh chứng: chưa có đầy đủ runtime screenshot/log trong kho local. |

## Technical Implementation

The CI/CD path uses GitHub Actions OIDC to assume the AWS deployment role instead of storing long-lived AWS access keys. ECR image URIs are based on AWS account, region, repository name, and immutable Git SHA tags.

{{< mermaid >}}
graph LR
  GitHub["GitHub Actions"] --> OIDC["GitHub OIDC token"]
  OIDC --> IAM["IAM role: internship-github-deploy"]
  IAM --> ECR["Amazon ECR"]
  IAM --> EKS["Amazon EKS"]
  ECR --> BackendImage["internship-backend:<github.sha>"]
  ECR --> ChatImage["internship-chat:<github.sha>"]
  EKS --> Deploy["scripts/k8s/deploy-eks.sh"]
{{< /mermaid >}}

The source repository includes deployment scripts for both EKS application deployment and frontend deployment. I keep sensitive runtime values such as `DATABASE_URL`, `REDIS_URL`, and `SECRET_KEY` in environment variables or Kubernetes Secrets, not in published documentation.

## Problems and Solutions

| Problem | Root cause | Resolution | Status |
|---|---|---|---|
| AWS access must not depend on static access keys. | Static credentials are high-risk for CI/CD. | GitHub OIDC was introduced for role assumption. | Completed |
| ECR push requires authorization permissions. | The GitHub deployment role needs ECR token and repository permissions. | ECR build/push workflow and later permission verification commits were added. | Partially completed |
| Deployment needs deterministic image names. | Manually passing image URIs is error-prone. | Workflow builds/pushes SHA-tagged images and deployment scripts consume those values. | Completed |
| EKS access can be blocked by limited permissions. | Deployment role may lack cluster or Kubernetes RBAC permissions. | EKS access smoke workflow and later rollout tolerance were added. | Partially completed |
| Digest and policy screenshots are missing. | AWS console/CLI evidence was not attached locally. | I kept AWS evidence pending. | Blocked |

## Testing, Build and Deployment Results

| Area | Result | Evidence |
|---|---|---|
| OIDC workflow | Implemented | `.github/workflows/aws-oidc-smoke-test.yml` existed in commit `2777b56`; later consolidated into CI/CD. |
| ECR build/push workflow | Implemented | Commit `9f9fcf3` added AWS ECR build/push workflow. |
| Production deploy workflow | Implemented | Commit `7eb1a76` added `scripts/ci/deploy-eks-pipeline.sh` and `scripts/ci/deploy-frontend.sh`. |
| AWS CLI/runtime logs | Partially completed | I did not find local `aws sts`, `aws ecr`, or policy simulation output in the local evidence archive. |

## Evidence

### Screenshots

Evidence pending: add screenshots under `/images/worklog/week-06/`, for example:

- `/images/worklog/week-06/github-oidc-success.png`
- `/images/worklog/week-06/ecr-images.png`
- `/images/worklog/week-06/iam-role-policy.png`

### Commits and Pull Requests

| Commit | Description | Evidence | Pull Request |
|---|---|---|---|
| `2777b56` | Added AWS OIDC smoke test workflow. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/2777b56e0080518dbafc895c8bb5e751ead33dd9) | Evidence pending |
| `9f9fcf3` | Added ECR build and push workflow. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/9f9fcf39354fd80fdb3bd724415fd5238a6c2c41) | Evidence pending |
| `7eb1a76` | Aligned AWS deployment with production architecture. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/7eb1a7685df2582e59c7c180355e479efcafe06c) | Evidence pending |
| `bfacd3a` | Added EKS access smoke test workflow. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/bfacd3acc67aeba66cc7ad9071b10eb1c0145fe9) | Evidence pending |
| `404ba6c` | Reran deployment path with ECR verify permission. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/404ba6c8da2344e38edf10498cf904105a618545) | Evidence pending |

### Test Logs

Evidence pending: attach actual output from:

```bash
aws sts get-caller-identity
aws ecr describe-repositories --repository-names internship-backend internship-chat
aws ecr describe-images --repository-name internship-backend
aws ecr describe-images --repository-name internship-chat
```

### Build Logs

Evidence pending: attach GitHub Actions or terminal logs showing Docker image build, tag, push, and digest output.

### Deployment Logs

Evidence pending: attach OIDC, ECR, or EKS smoke workflow logs. Do not include secrets or database URLs.

## Weekly Results

Kết quả cá nhân tuần 6 là nền tảng định danh triển khai cloud và phân phối image dùng chung. Các thành viên chịu trách nhiệm về source code và tính đúng đắn của image; tôi phụ trách tích hợp OIDC, IAM, ECR và deployment workflow.

## Lessons Learned

AWS CI/CD work depends on both IAM and runtime evidence. A workflow file can be correct structurally, but I only mark authentication, image push, or cluster access as verified when the corresponding AWS/Actions log is available.

## Next Week Plan

Deploy and validate the managed AWS runtime: EKS cluster, namespace, RDS PostgreSQL, ElastiCache Redis, DynamoDB tables, SQS queue/DLQ, IRSA runtime role, and ALB ingress.
