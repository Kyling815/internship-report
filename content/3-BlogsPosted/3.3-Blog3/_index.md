---
title: "Blog 3"
date: 2026-07-28
weight: 3
chapter: false
pre: " <b> 3.3. </b> "
---

# A Few Takeaways from My Software Engineering Journey: From Writing Code to Breaking the System and Fixing It Myself

## Introduction

I once believed that the main responsibility of a Software Engineer was to receive requirements, write code, complete features, and push the source code to a repository. However, after working directly on a relatively complete system, I realized that writing functional code is only the first step.

The more difficult challenge is ensuring that the code operates reliably within a real system containing multiple interconnected components, including a frontend, backend APIs, databases, message queues, containers, Kubernetes, CI/CD pipelines, and AWS infrastructure.

While developing the AI-Powered Internship Application Tracker, I worked with FastAPI, React, PostgreSQL, Redis, DynamoDB, Amazon SQS, Docker, Kubernetes, GitHub Actions, and several AWS services. This experience did not simply introduce me to more technologies. It also changed how I understand software development, deployment, failure, and recovery.


## Running Locally Does Not Mean Running Successfully in Production

In a local environment, system components are usually close together and relatively easy to control. The database may run inside Docker Compose, Redis may share the same network, and environment variables may be stored in a local `.env` file.

When the system is moved to Kubernetes or AWS, communication becomes more complex. A service must use the correct DNS name, namespace, port, and network configuration to reach another service. A pod connecting to a database requires the correct connection string, security group, and network route. Applications in private subnets also need an appropriate outbound path to access external services.

This experience helped me understand that an application does not operate based on source code alone. Its reliability also depends on the environment surrounding it.

## Docker and the Runtime Environment

Docker helps standardize the runtime environment across different machines, but containerization also introduces new types of problems.

A container may be running while its health check is failing. An application may start before its database becomes available. Environment variables may exist on the host machine but may not be passed correctly into the container. Port conflicts, missing volumes, Docker Desktop settings, and WSL integration can also prevent the system from operating even when the code has not changed.

These situations encouraged me to examine more than the application code:

- Which environment variables does the container actually receive?
- Are the required dependencies ready?
- Are the services connected to the correct network?
- Are ports exposed and mapped properly?
- What behavior is the health check validating?

## CI/CD Is Not a Magical YAML File

GitHub Actions can automate linting, testing, image building, security scanning, and deployment. However, a pipeline works only when all of its assumptions are correct.

A workflow may fail because a secret is missing, a branch condition is incorrect, an image tag is inconsistent, or the runner does not contain the required tools. A deployment job may also be skipped because an environment variable or execution condition has not been configured correctly.

Through troubleshooting failed workflows, I learned that CI/CD is not simply about creating a configuration file. Developers need to understand what each step does, what data is passed between jobs, and what state the destination system must be in before deployment can proceed.

## IAM and the Importance of Verifying Permissions

AWS IAM was one of the areas that required the most troubleshooting. Initially, I assumed that a missing permission could be fixed by adding a policy containing the required action.

In practice, AWS permissions also depend on trust policies, principals, conditions, repositories, branches, resource ARNs, and whether a particular action supports resource-level permissions.

A policy may appear secure and carefully restricted but still fail to operate. Some actions require the resource to be set to `"*"`, while others can be limited to a specific ARN.

Instead of continuing to guess, I began using policy simulation tools to verify each action. The main lesson was straightforward:

> Permissions should not be guessed. Each required action should be verified to determine whether it is allowed or denied.

## Kubernetes: Running Does Not Always Mean Healthy

Kubernetes may report a pod as `Running`, but that status only confirms that the container currently exists. It does not guarantee that the application inside it is functioning correctly.

A running pod may still fail to connect to Redis, wait for an unfinished migration, return no API response, or lack outbound network access. Therefore, system validation should include more than pod status:

- Application logs.
- Readiness and liveness probes.
- Kubernetes Services and Ingress.
- Database migrations.
- Network connectivity.
- Dependent services.

This taught me not to rely only on infrastructure status. The actual behavior of the application must also be tested through endpoints and real user flows.

## The NAT Gateway Incident and Network Architecture

One of the most memorable incidents occurred when I disabled the NAT Gateway to reduce operating costs. Afterward, pods in private subnets could no longer access the Internet, some connections to AWS services were interrupted, and deployment processes began to fail.

Because the source code, IAM configuration, and security groups had not changed, the cause was initially difficult to identify. After reviewing the network architecture, I discovered that the outbound route had disappeared when the NAT Gateway was disabled.

This incident gave me a much clearer understanding of public subnets, private subnets, Internet Gateways, NAT Gateways, route tables, and VPC Endpoints. Concepts that had previously existed only in architecture diagrams became practical knowledge after I experienced and resolved the failure myself.

## Database Concurrency and Idempotency

Many backend problems do not appear when only one user is testing the system. They become visible when two or more requests arrive at nearly the same time.

For example, two requests may both check that a record does not exist and then attempt to insert it. Without proper constraints and transaction handling, duplicate data may be created.

To reduce these risks, the system can use:

- Database unique constraints.
- Transactions and rollback handling.
- HTTP 409 responses for conflicts.
- Optimistic locking.
- Idempotency keys for important operations.

An internship application should not be created twice simply because the user clicked a button multiple times or because the client retried the request.

## Message Queues and the Transactional Outbox Pattern

Another challenge appears when a system must update a database and publish a message to a queue as part of the same logical operation.

If the database commit succeeds but message delivery fails, the data exists while the event is lost. Sending the message first is also unsafe because the database transaction may later fail.

The transactional outbox pattern addresses this issue by storing both the main data and its event within the same database transaction. A separate dispatcher then reads the outbox records and sends them to Amazon SQS. Failed deliveries can be retried, while consumers should support deduplication to prevent the same event from being processed repeatedly.

This is an example of an engineering effort that users may never see directly but that significantly improves system reliability.

## A Systematic Debugging Approach

The most valuable lesson was not memorizing a large number of commands. It was learning how to divide a problem into smaller layers.

When an error occurs, I now begin with questions such as:

1. Is the issue located in the application or the infrastructure?
2. Did it occur before or after deployment?
3. Are the container and pod running?
4. Is the service exposing the correct port?
5. Can DNS resolve the required hostname?
6. Does the network provide the necessary route?
7. Does IAM allow the required action?
8. Are the database and other dependencies ready?
9. What was the last step that completed successfully?

Instead of changing several components at once, I try to identify the first point of failure in the processing chain. This approach makes troubleshooting more structured and reduces the time spent making random changes.

## Conclusion

This journey significantly changed how I understand Software Engineering.

Previously, my first response to a system failure was to modify the code. I now understand that a failure may originate from configuration, environment variables, containers, networking, databases, permissions, infrastructure, or CI/CD.

I also consider questions beyond whether a feature simply works:

- What happens when a request is submitted twice?
- What happens if the database commits but the queue fails?
- How are simultaneous updates handled?
- How does the system recover when a pod restarts?
- Can a failed deployment be rolled back safely?

A Software Engineer is not someone who never causes a system failure. More importantly, a Software Engineer learns from each failure, understands the system more deeply, resolves issues systematically, and designs the system so that the same failure is less likely to occur again.

## Publication Information

- **Topic:** Practical lessons from developing, deploying, and operating a software system.
- **Published date:** July 28, 2026.
- **Platform:** AWS Study Groups.
- **Status:** Pending.
- **Public link:** [Blog 3 on AWS Study Groups](https://www.facebook.com/groups/awsstudygroupfcj/permalink/2227122848052675/#)
