---
title: "Workshop"
date: 2024-01-01
weight: 5
chapter: false
pre: " <b> 5. </b> "
includeContainerContentInReport: true
---

## Overview

This workshop presents the complete deployment process of the Internship Application Tracker on AWS.

The workshop covers source code preparation, cloud infrastructure provisioning, database deployment, application deployment, AI processing, event-driven notification, monitoring, testing, troubleshooting, and resource clean-up.

The final architecture uses:

- Amazon CloudFront and Amazon S3 for frontend delivery.
- Application Load Balancer for public API and realtime traffic.
- Amazon EKS for backend, chat, worker and AI adapter workloads.
- Amazon RDS PostgreSQL for transactional business data.
- Amazon ElastiCache Redis for realtime Socket.IO pub/sub.
- Amazon DynamoDB for chat persistence and Lambda event deduplication.
- Amazon SQS for asynchronous event delivery.
- AWS Lambda and Amazon SES for notifications.
- Amazon SageMaker for AI inference.
- GitHub Actions and AWS OIDC for continuous deployment.

## Learning objectives

After completing this workshop, the reader should be able to:

1. Prepare a multi-service application for AWS deployment.
2. Deploy containerized services to Amazon EKS.
3. Deploy a static React frontend through Amazon S3 and CloudFront.
4. Connect EKS workloads to RDS, Redis, DynamoDB, SQS and SageMaker.
5. Implement asynchronous processing with workers and transactional outbox.
6. Process SQS events with AWS Lambda.
7. Implement idempotent Lambda processing using DynamoDB.
8. Configure CI/CD using GitHub Actions and AWS OIDC.
9. Validate the complete system through end-to-end testing.
10. Diagnose common networking, IAM and deployment failures.

## Target audience

This workshop is intended for:

- Cloud engineering interns.
- Backend and DevOps students.
- Developers learning Amazon EKS.
- Developers implementing event-driven AWS architectures.
- Students preparing an AWS internship or graduation project report.

## Architecture summary

![Internship Application Tracker architecture on AWS](/images/5-Workshop/infra.png)

The browser connects to Amazon CloudFront through HTTPS.

CloudFront routes:

- static frontend requests to Amazon S3
- `/api/*` requests to the backend through the Application Load Balancer
- `/chat/*` requests to the chat service
- `/socket.io/*` requests to the realtime Socket.IO service

The backend, chat service, processing worker, AI service and outbox dispatcher run inside Amazon EKS.

PostgreSQL stores transactional business data and processing jobs. DynamoDB stores chat data. Redis provides pub/sub between chat pods.

The processing worker calls the AI service, which invokes the SageMaker endpoint.

The outbox dispatcher publishes business events to Amazon SQS. AWS Lambda consumes these events, performs deduplication in DynamoDB, archives events to Amazon S3 and sends notifications through Amazon SES.

## Chapters

| Chapter | Title | Description | Status |
|---|---|---|---|
| 5.1 | Overview | Workshop objectives, scope and final architecture | Complete |
| 5.2 | Architecture | Detailed AWS architecture and request flows | Complete |
| 5.3 | Prerequisites | Required accounts, tools and local configuration | Complete |
| 5.4 | Source Code Preparation | Repository structure, environment variables and validation | Complete |
| 5.5 | AWS Infrastructure | Networking, IAM, EKS, ECR, ALB and CloudFront | Complete |
| 5.6 | Database Deployment | PostgreSQL, Redis and DynamoDB deployment | Complete |
| 5.7 | Backend Deployment | Backend, chat, dispatcher, AI service and worker deployment | Complete |
| 5.8 | Frontend Deployment | React build, S3 upload and CloudFront distribution | Complete |
| 5.9 | Monitoring and Logging | Logs, health checks, metrics and alarms | Complete |
| 5.10 | End-to-End Testing | Application, chat, AI and Lambda verification | Complete |
| 5.11 | Security and Cost | IAM, encryption, OIDC and cost assumptions | Complete |
| 5.12 | Troubleshooting | Resolved deployment and runtime failures | Complete |
| 5.13 | Clean-up | Safe resource deletion procedure | Complete |

## Final outcome

At the end of the workshop, the Internship Application Tracker is available through CloudFront and supports:

- static frontend delivery
- backend APIs
- realtime chat
- persistent data storage
- asynchronous AI processing
- transactional outbox publishing
- Lambda-based event notifications
- automated deployment through GitHub Actions
