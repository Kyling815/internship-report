---
title: "Clean-up"
date: 2024-01-01
weight: 13
chapter: false
pre: " <b> 5.13. </b> "
---

## Objective

Provide a safe, dependency-aware cleanup sequence for the AWS production environment after testing or demonstration is complete.

## Warning

The commands in this chapter are destructive. Do not run them unless the project owner, AWS account owner, and team have approved cleanup. Export required evidence, logs, test results, cost reports, and final screenshots before deleting resources.

This chapter is documentation only. No cleanup commands were executed as part of preparing this report.

## Architecture context

Cleanup must follow dependency order. Deleting shared networking or IAM first can leave load balancers, ENIs, node groups, endpoints, queues, buckets, or log groups stuck. The safest approach is to stop producers, stop consumers, delete high-cost compute, then remove networking and IAM last.

## Pre-cleanup checklist

- [ ] Confirm the environment is no longer needed.
- [ ] Export CloudFront, ALB, EKS, RDS, Redis, DynamoDB, SQS, Lambda, SageMaker, and S3 evidence.
- [ ] Export AWS Cost Explorer or Pricing Calculator evidence.
- [ ] Export Lambda logs for the final smoke test.
- [ ] Export any required S3 event archive objects.
- [ ] Confirm no production users depend on the deployment.
- [ ] Confirm backups or snapshots are either retained or intentionally deleted.
- [ ] Confirm the active AWS account is the intended project account.
- [ ] Confirm the active region is `ap-southeast-1`.

Verification:

```bash
aws sts get-caller-identity
aws configure get region
kubectl config current-context
```

## Dependency-aware cleanup order

### 1. Disable the processing worker

Stop long-running AI work before deleting SageMaker or database resources:

```bash
kubectl scale deployment/backend-processing-worker --replicas=0 -n internship
kubectl delete hpa backend-processing-worker -n internship --ignore-not-found
kubectl delete pdb backend-processing-worker -n internship --ignore-not-found
kubectl rollout status deployment/backend-processing-worker -n internship --timeout=120s
```

### 2. Disable Lambda SQS event-source mapping

List mappings:

```bash
aws lambda list-event-source-mappings \
  --function-name internship-outbox-handler \
  --region ap-southeast-1
```

Disable each mapping:

```bash
aws lambda update-event-source-mapping \
  --uuid <EVENT_SOURCE_MAPPING_UUID> \
  --enabled false \
  --region ap-southeast-1
```

### 3. Delete SageMaker endpoint

SageMaker endpoint uptime can be a major cost driver:

```bash
aws sagemaker delete-endpoint \
  --endpoint-name internship-qwen3-4b \
  --region ap-southeast-1
```

Then inspect endpoint config and model resources before deleting them:

```bash
aws sagemaker list-endpoint-configs --region ap-southeast-1
aws sagemaker list-models --region ap-southeast-1
```

### 4. Delete Lambda function

Delete after disabling the event-source mapping:

```bash
aws lambda delete-function \
  --function-name internship-outbox-handler \
  --region ap-southeast-1
```

### 5. Delete Lambda event-source mapping

```bash
aws lambda delete-event-source-mapping \
  --uuid <EVENT_SOURCE_MAPPING_UUID> \
  --region ap-southeast-1
```

### 6. Inspect or purge test messages

Check queue state:

```bash
aws sqs get-queue-attributes \
  --queue-url <OUTBOX_QUEUE_URL> \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
  --region ap-southeast-1
```

If approved, purge test messages:

```bash
aws sqs purge-queue --queue-url <OUTBOX_QUEUE_URL> --region ap-southeast-1
```

### 7. Delete SQS queues

```bash
aws sqs delete-queue --queue-url <OUTBOX_QUEUE_URL> --region ap-southeast-1
aws sqs delete-queue --queue-url <OUTBOX_DLQ_URL> --region ap-southeast-1
```

### 8. Delete Kubernetes Ingress

Deleting the Ingress lets AWS Load Balancer Controller remove the ALB:

```bash
kubectl delete ingress internship-public -n internship --ignore-not-found
```

### 9. Wait for ALB deletion

```bash
aws elbv2 describe-load-balancers --region ap-southeast-1
aws elbv2 describe-target-groups --region ap-southeast-1
```

Wait until the internship ALB and target groups are gone.

### 10. Delete EKS workloads

```bash
kubectl delete -f k8s/app/autoscaling.yaml --ignore-not-found
kubectl delete -f k8s/app/ai-service.yaml --ignore-not-found
kubectl delete -f k8s/app/backend-processing-worker.yaml --ignore-not-found
kubectl delete -f k8s/app/backend-outbox-dispatcher.yaml --ignore-not-found
kubectl delete -f k8s/app/chat.yaml --ignore-not-found
kubectl delete -f k8s/app/backend.yaml --ignore-not-found
kubectl delete job backend-migrate chat-init -n internship --ignore-not-found
```

Delete namespace only after confirming no resources remain:

```bash
kubectl get all -n internship
kubectl delete namespace internship
```

### 11. Delete EKS node group

```bash
aws eks list-nodegroups \
  --cluster-name internship-prod \
  --region ap-southeast-1

aws eks delete-nodegroup \
  --cluster-name internship-prod \
  --nodegroup-name <NODEGROUP_NAME> \
  --region ap-southeast-1
```

Wait:

```bash
aws eks wait nodegroup-deleted \
  --cluster-name internship-prod \
  --nodegroup-name <NODEGROUP_NAME> \
  --region ap-southeast-1
```

### 12. Delete EKS cluster

```bash
aws eks delete-cluster \
  --name internship-prod \
  --region ap-southeast-1
```

### 13. Delete RDS

Decide whether to keep a final snapshot:

```bash
aws rds delete-db-instance \
  --db-instance-identifier internship-prod-postgres \
  --final-db-snapshot-identifier internship-prod-postgres-final-<DATE> \
  --region ap-southeast-1
```

Only skip the snapshot when explicitly approved:

```bash
aws rds delete-db-instance \
  --db-instance-identifier internship-prod-postgres \
  --skip-final-snapshot \
  --region ap-southeast-1
```

### 14. Delete ElastiCache

```bash
aws elasticache delete-replication-group \
  --replication-group-id internship-prod-redis \
  --region ap-southeast-1
```

### 15. Delete DynamoDB tables

Delete only after confirming no data retention is required:

```bash
aws dynamodb delete-table --table-name ChatUsers --region ap-southeast-1
aws dynamodb delete-table --table-name ChatGroups --region ap-southeast-1
aws dynamodb delete-table --table-name ChatMessages --region ap-southeast-1
aws dynamodb delete-table --table-name InternshipLambdaEventDedupe --region ap-southeast-1
```

### 16. Empty and delete S3 buckets

Inspect first:

```bash
aws s3 ls s3://internship-prod-frontend-<AWS_ACCOUNT_ID> --recursive --summarize
aws s3 ls s3://internship-prod-uploads-<AWS_ACCOUNT_ID> --recursive --summarize
```

Empty and delete after approval:

```bash
aws s3 rm s3://internship-prod-frontend-<AWS_ACCOUNT_ID> --recursive
aws s3 rb s3://internship-prod-frontend-<AWS_ACCOUNT_ID>
aws s3 rm s3://internship-prod-uploads-<AWS_ACCOUNT_ID> --recursive
aws s3 rb s3://internship-prod-uploads-<AWS_ACCOUNT_ID>
```

If versioning is enabled, delete object versions and delete markers before removing the bucket.

### 17. Disable and delete CloudFront

CloudFront must be disabled before deletion:

```bash
aws cloudfront get-distribution-config --id EQIGYNECXDYL8
```

Update the distribution config with `Enabled=false`, keep the current `ETag`, then wait:

```bash
aws cloudfront wait distribution-deployed --id EQIGYNECXDYL8
```

Delete:

```bash
aws cloudfront delete-distribution \
  --id EQIGYNECXDYL8 \
  --if-match <ETAG>
```

### 18. Delete NAT Gateway

```bash
aws ec2 describe-nat-gateways --region ap-southeast-1
aws ec2 delete-nat-gateway --nat-gateway-id <NAT_GATEWAY_ID> --region ap-southeast-1
```

### 19. Release Elastic IP

Release the NAT Gateway Elastic IP only after the NAT Gateway is deleted:

```bash
aws ec2 release-address --allocation-id <ALLOCATION_ID> --region ap-southeast-1
```

### 20. Delete IAM roles and policies

Delete IAM roles last, after workloads that use them are gone:

```bash
aws iam detach-role-policy --role-name internship-github-deploy --policy-arn <POLICY_ARN>
aws iam delete-role --role-name internship-github-deploy
```

Repeat for project-specific roles only after confirming no shared resource depends on them.

### 21. Delete remaining VPC resources

Inspect and remove:

- security groups
- route tables
- subnets
- Internet Gateway
- NAT routes
- VPC endpoints
- leftover ENIs

Commands:

```bash
aws ec2 describe-network-interfaces --region ap-southeast-1
aws ec2 describe-security-groups --region ap-southeast-1
aws ec2 describe-route-tables --region ap-southeast-1
aws ec2 describe-internet-gateways --region ap-southeast-1
aws ec2 describe-vpc-endpoints --region ap-southeast-1
```

### 22. Verify billing resources are gone

Final checks:

```bash
aws eks list-clusters --region ap-southeast-1
aws elbv2 describe-load-balancers --region ap-southeast-1
aws rds describe-db-instances --region ap-southeast-1
aws elasticache describe-replication-groups --region ap-southeast-1
aws sqs list-queues --region ap-southeast-1
aws lambda list-functions --region ap-southeast-1
aws sagemaker list-endpoints --region ap-southeast-1
aws cloudfront list-distributions
```

Review AWS Billing and Cost Explorer the next day because some usage records appear after a delay.

## Common errors

| Symptom | Cause | Resolution |
|---|---|---|
| VPC cannot be deleted | ENIs, ALB, NAT, endpoints, or security groups remain | Inspect ENIs and dependent resources |
| S3 bucket cannot be deleted | Versioned objects or delete markers remain | Delete all object versions and markers |
| CloudFront cannot be deleted | Distribution still enabled or ETag mismatch | Disable, wait for deployed state, use latest ETag |
| IAM role cannot be deleted | Policies still attached | Detach inline and managed policies first |
| SQS messages keep reappearing | Lambda event source still enabled | Disable/delete event-source mapping before queue deletion |

## Outcome

Cleanup is complete only when high-cost services, queues, buckets, databases, load balancers, endpoints, IAM roles, and VPC resources are removed or intentionally retained with written approval.
