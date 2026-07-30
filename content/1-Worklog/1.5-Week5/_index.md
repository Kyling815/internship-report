---
title: "Week 5 Worklog"
date: 2024-01-01
weight: 5
chapter: false
pre: " <b> 1.5. </b> "
---

# Week 5 - Local Kubernetes Deployment

## Objectives

Within the five-member team, my Week 5 objective was to move the integrated application from Compose-only development to a local Kubernetes environment using kind. I owned the deployment manifests and automation, while teammates supplied and checked their component-specific runtime configuration.

## My Contributions

| Status | My assigned contribution | Evidence basis |
|---|---|---|
| Completed | Added kind cluster configuration. | `k8s/cluster/kind-config.yaml` and commit `8dae02c`. |
| Completed | Added Kubernetes resources for backend, chat, PostgreSQL, Redis, DynamoDB Local, migration job, and chat initialization job. | `k8s/app/*.yaml`. |
| Completed | Added local deployment automation for PowerShell and shell users. | `scripts/k8s/deploy-local.ps1` and `scripts/k8s/deploy-local.sh`. |
| Completed | Added HPA and PDB definitions for app services. | `k8s/app/autoscaling.yaml`. |
| Completed | Added observability resources for Prometheus, Grafana, Loki, Tempo, Alloy, OTel collector, ServiceMonitors, and PrometheusRules. | `k8s/observability/*` and `observability/grafana/*`. |
| Partially completed | Captured live `kubectl` screenshots and command logs where available. | Evidence pending: I did not have the full screenshot/log artifact set in the local evidence archive. |

## Technical Implementation

The local Kubernetes path uses kind for the cluster, in-cluster PostgreSQL/Redis/DynamoDB Local for dependencies, and Kubernetes manifests under `k8s/app` for the workload layer.

{{< mermaid >}}
graph TB
  subgraph Kind["kind-internship-local"]
    subgraph Internship["namespace: internship"]
      Backend["Deployment/backend"]
      Chat["Deployment/chat-service"]
      Dispatcher["Deployment/backend-outbox-dispatcher"]
      Worker["Deployment/backend-processing-worker"]
      Postgres["Deployment/postgres"]
      Redis["Deployment/redis"]
      DDB["Deployment/dynamodb-local"]
      Migrate["Job/backend-migrate"]
      Init["Job/chat-init"]
    end
    subgraph Monitoring["namespace: monitoring"]
      Prom["Prometheus"]
      Grafana["Grafana"]
      Loki["Loki"]
      Tempo["Tempo"]
    end
  end
  Backend --> Postgres
  Backend --> DDB
  Backend --> Dispatcher
  Worker --> Backend
  Chat --> Redis
  Chat --> DDB
  Prom --> Backend
  Prom --> Chat
  Prom --> Dispatcher
{{< /mermaid >}}

The deployment scripts build local images, load them into kind, apply app manifests, run migration/init jobs, wait for rollouts, and print port-forward commands for backend, chat, and optional AI service checks.

## Problems and Solutions

| Problem | Root cause | Resolution | Status |
|---|---|---|---|
| Compose did not prove Kubernetes readiness. | Services could work locally while still missing probes, Services, Jobs, or ConfigMaps. | Added Kubernetes manifests and local deployment scripts. | Completed |
| Fresh local images might not be used by kind. | Building an image is not enough; kind nodes need the image loaded. | Scripts run `kind load docker-image` and restart deployments. | Completed |
| Migrations and chat table creation need ordered startup. | API/chat pods should not assume databases are initialized. | Added `backend-migrate` and `chat-init` Jobs. | Completed |
| Local observability required multiple supporting components. | Metrics, logs, and traces need separate platform services. | Added Helm-backed Prometheus/Grafana/Loki/Tempo/Alloy resources and local runbook guidance. | Completed |
| Live cluster screenshots are missing. | Runtime screenshots were not attached to the local evidence archive. | I kept Kubernetes evidence pending. | Blocked |

## Testing, Build and Deployment Results

| Area | Result | Evidence |
|---|---|---|
| Kubernetes manifests | Implemented | `k8s/app` includes Deployments, Services, Jobs, ConfigMaps, Secret examples, ingress, HPA, and PDB. |
| Local deployment scripts | Implemented | `scripts/k8s/deploy-local.ps1` and `.sh` automate cluster setup, image load, jobs, rollouts, and resource display. |
| Observability resources | Implemented | `k8s/observability` and `observability/grafana` include dashboards, datasources, rules, and collectors. |
| Runtime validation logs | Partially completed | Commands are scripted, but current report does not include saved `kubectl` output. |

## Evidence

### Screenshots

Evidence pending: add screenshots under `/images/worklog/week-05/`, for example:

- `/images/worklog/week-05/kubectl-get-nodes.png`
- `/images/worklog/week-05/kubectl-get-pods.png`
- `/images/worklog/week-05/grafana-dashboard.png`

### Commits and Pull Requests

| Commit | Description | Evidence | Pull Request |
|---|---|---|---|
| `8dae02c` | Added the first Kubernetes configuration for backend, chat, dependencies, jobs, namespace, and kind config. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/8dae02cc55c9782a390ac851126e79e25892070f) | Evidence pending |
| `7dbe7c6` | Added Kubernetes/EKS deployment platform, autoscaling, ingress, service accounts, observability, and deploy scripts. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/7dbe7c6555fbb1bebd218d9af149ab90ebdd999a) | Evidence pending |
| `4f37d4d` | Added Kubernetes deployment workflows. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/4f37d4db753c8646172cd17cd5f481b6c4e6a4d9) | Evidence pending |
| `7407fda` | Added tracing and chat initialization support. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/7407fda080ac210411f67985996772185c311b06) | Evidence pending |
| `3b6f346` | Added local terminal runbook and environment examples. | [View commit](https://github.com/Temp-orgo/AWS-Internship/commit/3b6f34675b11b9c2a8c66006e3d4eb7fe9ca2e6f) | Evidence pending |

### Test Logs

Evidence pending: attach actual local Kubernetes output from commands such as:

```bash
kubectl cluster-info
kubectl get nodes
kubectl get pods -n internship
kubectl get services -n internship
kubectl rollout status deployment/backend -n internship
kubectl rollout status deployment/chat-service -n internship
```

### Build Logs

Evidence pending: attach output from local image builds and `kind load docker-image` commands.

### Deployment Logs

Evidence pending: attach output from `scripts/k8s/deploy-local.ps1` or `scripts/k8s/deploy-local.sh`.

## Weekly Results

My Week 5 result was the local Kubernetes deployment path, including manifests, automation, scaling controls, and observability resources. Functional verification of backend, frontend, chat, and AI behavior was coordinated with the four component owners.

## Lessons Learned

Local Kubernetes validation is more than checking that pods start. Jobs, readiness probes, image freshness, DNS, service ports, ingress, HPA metrics, and observability scraping all need explicit checks.

## Next Week Plan

Prepare the AWS foundation: AWS CLI validation, region selection, GitHub OIDC, IAM deployment role, ECR repositories, and image build/push workflow.
