---
title: "Week 6 Worklog"
date: 2024-01-01
weight: 6
chapter: false
pre: " <b> 1.6. </b> "
---

# Week 6 - AWS Foundation, IAM, OIDC and ECR

## Objectives

Within the five-member team, my Week 6 objective was to prepare the shared AWS deployment foundation: region configuration, GitHub OIDC authentication, IAM deployment permissions, ECR image repositories, and CI jobs that publish the team's service images without long-lived AWS credentials.

## My Contributions

| Status | My assigned contribution | Evidence basis |
|---|---|---|
| Completed | Standardized production region as `ap-southeast-1`. | `PROJECT_CONTEXT.md`, `.github/workflows/cicd.yml`, and deployment scripts. |
| Completed | Added GitHub OIDC smoke workflow. | Commit `2777b56`. |
| Completed | Added ECR build and push workflow for application images. | Commit `9f9fcf3`. |
| Completed | Aligned AWS deployment workflow with production architecture. | Commit `7eb1a76`. |
| Completed | Added EKS access smoke test workflow. | Commit `bfacd3a`. |

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

## Testing, Build and Deployment Results

| Area | Result | Evidence |
|---|---|---|
| OIDC workflow | Implemented | `.github/workflows/aws-oidc-smoke-test.yml` existed in commit `2777b56`; later consolidated into CI/CD. |
| ECR build/push workflow | Implemented | Commit `9f9fcf3` added AWS ECR build/push workflow. |
| Production deploy workflow | Implemented | Commit `7eb1a76` added `scripts/ci/deploy-eks-pipeline.sh` and `scripts/ci/deploy-frontend.sh`. |
| AWS CLI/runtime logs | Partially completed | I did not find local `aws sts`, `aws ecr`, or policy simulation output in the local evidence archive. |

## Evidence

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

My Week 6 result was the cloud deployment identity and image-delivery foundation used by the whole team. The teammates remained responsible for their service code and image correctness; I owned the OIDC, IAM, ECR, and deployment-workflow integration.

## Lessons Learned

AWS CI/CD work depends on both IAM and runtime evidence. A workflow file can be correct structurally, but I only mark authentication, image push, or cluster access as verified when the corresponding AWS/Actions log is available.

## Next Week Plan

Deploy and validate the managed AWS runtime: EKS cluster, namespace, RDS PostgreSQL, ElastiCache Redis, DynamoDB tables, SQS queue/DLQ, IRSA runtime role, and ALB ingress.
