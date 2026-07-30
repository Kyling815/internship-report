---
title: "Troubleshooting"
date: 2024-01-01
weight: 12
chapter: false
pre: " <b> 5.12. </b> "
---

## Objective

Record production troubleshooting cases, root causes, diagnostic commands, resolutions, and prevention steps.

## Architecture context

Most failures in this project happened at integration boundaries: VPC egress, EKS node readiness, AWS Load Balancer Controller, GitHub Actions variables, CloudFront routing, queue naming, DynamoDB expressions, IAM, and AI dependency readiness.

## Troubleshooting table

| Incident | Symptom | Root cause | Diagnostic command | Resolution | Prevention |
|---|---|---|---|---|---|
| NAT Gateway blackhole | Managed EKS nodes could not join cluster | Private subnet default route pointed to a deleted NAT Gateway and route state became `blackhole` | `aws ec2 describe-route-tables --region ap-southeast-1` | Created or restored NAT Gateway, updated private route tables, recreated or recovered node group | Check private subnet default routes before node group changes |
| AWS Load Balancer Controller crash | Controller could not create ALB resources | Controller could not obtain VPC ID through metadata; error included `failed to get VPC ID from instance metadata` and `context deadline exceeded` | `kubectl logs -n kube-system deployment/aws-load-balancer-controller --tail=200` | Added `--aws-region=ap-southeast-1` and `--aws-vpc-id=vpc-0cfee519122ae18b4` | Configure region and VPC ID explicitly in constrained metadata environments |
| GitHub Actions frontend job skipped | Frontend deployment did not run | A job-level `if` used GitHub environment variables before environment values were loaded | Inspect workflow job conditions and run summary | Required flags were also configured as repository variables; frontend deployment was separated from app deployment | Avoid environment-only variables in early job-level conditions |
| CloudFront architecture correction | API/chat routing was misunderstood | S3 was incorrectly described as behind ALB | `aws cloudfront get-distribution --id EQIGYNECXDYL8` | Corrected design: default behavior to S3, `/api/*`, `/chat/*`, `/socket.io/*` to ALB | Treat CloudFront distribution behaviors as source of truth |
| SQS queue mismatch | AWS CLI query returned no queue or wrong queue | CloudShell `OUTBOX_QUEUE_URL` was empty and wrong queue name `internship-outbox` was queried | `aws sqs list-queues --region ap-southeast-1` | Used current queue `internship-prod-outbox` | Store queue URL in deployment secrets and verify names before testing |
| SQS script/runtime mismatch | Provisioning script output did not match current runtime queue settings | Repository scripts default to `internship-outbox-events` and visibility timeout `60`; current runtime evidence shows `internship-prod-outbox` and visibility timeout `120` | Inspect `scripts/aws/provision-outbox-sqs.sh` and AWS queue attributes | I use runtime evidence for the deployed report state; script updates belong in a separate application change task | Keep infrastructure scripts synchronized with production names |
| Lambda DynamoDB reserved keyword | Lambda failed with DynamoDB `ValidationException` | UpdateExpression used reserved attribute name `result` directly | Inspect Lambda CloudWatch logs | Replaced `result` with `#result` and mapped `"#result": "result"` | Use expression attribute names for reserved words |
| IAM `PassRole` denial | Deployment or SageMaker operation failed | Role lacked `iam:PassRole` for the intended SageMaker execution role | Inspect GitHub Actions logs and CloudTrail | Grant scoped `iam:PassRole` only for required role and service | Add IAM preflight checks before deploy |
| ECR authorization or `DescribeImages` denial | Deploy job could not verify image tag | GitHub OIDC role lacked required ECR read action | `aws ecr describe-images --repository-name internship-backend --image-ids imageTag=<GITHUB_SHA>` | Add scoped ECR permissions for repository/image verification | Keep deploy role policy aligned with workflow checks |
| GitHub OIDC AssumeRoleWithWebIdentity failure | AWS credential step failed | OIDC trust policy, audience, branch/environment condition, or role ARN mismatch | Inspect `aws-actions/configure-aws-credentials` error and role trust policy | Correct trust policy and `AWS_ROLE_TO_ASSUME` | Test OIDC assume-role before adding deploy steps |
| Alembic database URL interpolation failure | Migration failed before connecting | Database URL contained characters interpreted by shell or config interpolation | `kubectl logs job/backend-migrate -n internship` | Store `DATABASE_URL` as secret and avoid rewriting it through unsafe interpolation | Treat database URLs as opaque secret values |
| Docker unavailable in WSL or local environment | CI/local validation could not build images | Docker daemon unavailable or Windows/WSL integration issue | `docker version` | Start Docker Desktop or use CI validation; report local Docker validation as not run if unavailable | Check Docker before image validation |
| ShellCheck SC2155 | Shell lint failed | Variable declaration and assignment combined in a way ShellCheck flags | `shellcheck scripts/*.sh` | Split declaration and assignment | Run shell lint before workflow dispatch |
| SageMaker endpoint not found | AI deploy or worker enablement failed | Endpoint name not created or not `InService` | `aws sagemaker describe-endpoint --endpoint-name internship-qwen3-4b --region ap-southeast-1` | Create/restore endpoint or keep worker disabled | Gate worker on endpoint `InService` |
| Frontend environment misconfiguration | Frontend called localhost in production | Missing `VITE_API_BASE_URL=/api` or wrong chat base URL | Inspect built app environment and browser network tab | Build with `VITE_API_BASE_URL=/api` and empty `VITE_CHAT_API_BASE_URL` | Keep frontend deploy variables in workflow |
| ALB certificate/domain handling | Public endpoint used default ALB/CloudFront domain | Custom domain and ACM certificate not configured | `aws elbv2 describe-listeners` and CloudFront viewer certificate config | Use CloudFront default certificate for default domain or add ACM/custom domain later | Separate default-domain deployment from custom-domain hardening |

## Detailed incident notes

### NAT Gateway blackhole

Private EKS worker nodes need outbound connectivity to reach AWS APIs and pull images. When the private subnet default route points to a deleted NAT Gateway, the route state becomes `blackhole`. Nodes fail to join or remain unhealthy.

Useful commands:

```bash
aws ec2 describe-route-tables --region ap-southeast-1
aws ec2 describe-nat-gateways --region ap-southeast-1
aws eks describe-nodegroup --cluster-name internship-prod --nodegroup-name <NODEGROUP_NAME> --region ap-southeast-1
kubectl get nodes -o wide
```

### AWS Load Balancer Controller crash

The controller needed explicit region and VPC ID:

```text
--aws-region=ap-southeast-1
--aws-vpc-id=vpc-0cfee519122ae18b4
```

Useful commands:

```bash
kubectl get deployment,pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller -o wide
kubectl logs -n kube-system deployment/aws-load-balancer-controller --tail=200
kubectl describe ingress internship-public -n internship
```

### CloudFront routing correction

Correct current design:

```text
CloudFront default *        -> S3 frontend origin
CloudFront /api/*           -> ALB origin -> backend
CloudFront /chat/*          -> ALB origin -> chat-service
CloudFront /socket.io/*     -> ALB origin -> chat-service
```

Incorrect design to avoid:

```text
S3 behind ALB
frontend running in EKS
```

### Lambda DynamoDB reserved word

The failing expression used `result` directly. The fixed pattern uses an expression attribute name:

```json
{
  "UpdateExpression": "SET #result = :result",
  "ExpressionAttributeNames": {
    "#result": "result"
  }
}
```

The successful smoke-test event was:

```text
lambda-smoke-fixed-1785220478
```

Archive key:

```text
outbox-archive/2026/07/28/lambda-smoke-fixed-1785220478.json
```

## General diagnostic workflow

1. Confirm AWS account and region.
2. Confirm kube context and namespace.
3. Check CloudFront behavior and ALB Ingress status.
4. Check Kubernetes deployment rollouts and pod events.
5. Check application logs.
6. Check managed service health.
7. Check IAM AccessDenied errors and CloudTrail if available.
8. Check queue, Lambda, DLQ, and dedupe state for async failures.
9. Record exact timestamps, command outputs, and final resolution.

Commands:

```bash
aws sts get-caller-identity
kubectl config current-context
kubectl get deployments,pods,svc,endpoints,ingress -n internship -o wide
kubectl get events -n internship --sort-by=.lastTimestamp
kubectl logs deployment/backend -n internship --tail=200
kubectl logs deployment/chat-service -n internship --tail=200
kubectl logs deployment/backend-outbox-dispatcher -n internship --tail=200
aws logs tail /aws/lambda/internship-outbox-handler --since 1h --region ap-southeast-1
```

## Expected result

Each incident should end with:

- root cause identified
- command evidence captured
- fix applied
- verification result recorded
- prevention step documented

## Outcome

The troubleshooting record turns deployment failures into reusable operational knowledge and helps future maintainers diagnose networking, IAM, CloudFront, SQS, Lambda, and SageMaker issues faster.
