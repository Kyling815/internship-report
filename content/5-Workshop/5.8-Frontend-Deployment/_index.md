---
title: "Frontend Deployment"
date: 2024-01-01
weight: 8
chapter: false
pre: " <b> 5.8. </b> "
---

## Objective

Build the React/Vite frontend, publish it to a private S3 bucket, and serve it through CloudFront.

## Architecture context

The frontend is currently deployed as static files, not as an EKS workload. The old frontend Kubernetes Deployment, Service, HPA, PDB, and frontend ALB Ingress were removed so future EKS app deployments cannot recreate them.

Current public entry point:

```text
https://dhm2rz5nmsibj.cloudfront.net
```

Current CloudFront distribution:

```text
EQIGYNECXDYL8
```

## Vite environment configuration

The frontend production build uses:

| Variable | Production value | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Makes backend API calls go through CloudFront and ALB |
| `VITE_CHAT_API_BASE_URL` | empty string | Allows browser runtime to use `/chat` outside localhost |

The frontend API client defaults to local development when not configured:

- API default: `http://localhost:8001`
- Chat default in local browser: `http://localhost:3000`
- Chat default outside localhost: `/chat`
- Socket.IO path: `/socket.io`

## Build commands

From the application repository:

```bash
cd frontend
npm ci
VITE_API_BASE_URL=/api VITE_CHAT_API_BASE_URL= npm run build
```

Expected output directory:

```text
frontend/dist
```

The deployment script detects `frontend/dist` or `frontend/build`, but the current Vite output is `frontend/dist`.

## S3 publishing

The production helper is:

```bash
bash scripts/ci/deploy-frontend.sh
```

Required variables:

| Variable | Purpose |
|---|---|
| `FRONTEND_DEPLOY_ENABLED` | Must be `true` |
| `FRONTEND_BUCKET` | Target bucket, for example `internship-prod-frontend-<AWS_ACCOUNT_ID>` |
| `CLOUDFRONT_DISTRIBUTION_ID` | Distribution to invalidate |
| `VITE_API_BASE_URL` | `/api` |
| `VITE_CHAT_API_BASE_URL` | empty string |

The script keeps the bucket private:

```bash
aws s3api put-public-access-block \
  --bucket internship-prod-frontend-<AWS_ACCOUNT_ID> \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

Static assets are uploaded with long cache headers:

```bash
aws s3 sync frontend/dist s3://internship-prod-frontend-<AWS_ACCOUNT_ID> \
  --delete \
  --exclude index.html \
  --cache-control public,max-age=31536000,immutable
```

`index.html` is uploaded separately with no-cache semantics:

```bash
aws s3 cp frontend/dist/index.html s3://internship-prod-frontend-<AWS_ACCOUNT_ID>/index.html \
  --cache-control no-cache \
  --content-type text/html
```

## CloudFront configuration

The helper `scripts/aws/ensure-cloudfront.sh` validates or creates the distribution. The current design uses:

| Behavior | Origin | Notes |
|---|---|---|
| Default `*` | S3 frontend bucket | Static frontend and SPA assets |
| `/api/*` | ALB | Backend API |
| `/chat/*` | ALB | Chat REST API |
| `/socket.io/*` | ALB | Socket.IO traffic |

CloudFront also configures SPA fallback:

| Error | Response path | Response code |
|---|---|---|
| 403 | `/index.html` | 200 |
| 404 | `/index.html` | 200 |

CloudFront invalidation:

```bash
aws cloudfront create-invalidation \
  --distribution-id EQIGYNECXDYL8 \
  --paths "/*"
```

## GitHub Actions frontend deployment

Use workflow dispatch mode:

```text
GitHub -> Actions -> CI/CD -> Run workflow -> mode: deploy-frontend
```

The `deploy-frontend` job:

1. Configures AWS credentials through OIDC.
2. Sets Node.js from workflow `NODE_VERSION`.
3. Verifies ALB health at `/api/health/ready` and `/chat/health/ready`.
4. Runs `scripts/ci/deploy-frontend.sh`.
5. Uploads frontend files to S3.
6. Creates a CloudFront invalidation.

## Verification

Check CloudFront:

```bash
curl -I https://dhm2rz5nmsibj.cloudfront.net/
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/api/health/ready
curl -fsS https://dhm2rz5nmsibj.cloudfront.net/chat/health/ready
```

Check S3 bucket privacy:

```bash
aws s3api get-public-access-block \
  --bucket internship-prod-frontend-<AWS_ACCOUNT_ID>
```

Check distribution:

```bash
aws cloudfront get-distribution --id EQIGYNECXDYL8
aws cloudfront list-invalidations --distribution-id EQIGYNECXDYL8
```

## Expected result

- The frontend loads through CloudFront.
- Direct frontend S3 bucket public access remains blocked.
- `/api/*`, `/chat/*`, and `/socket.io/*` routes use the ALB origin.
- SPA deep links return `index.html`.
- A new CloudFront invalidation is created after deployment.

## Common errors

| Symptom | Cause | Resolution |
|---|---|---|
| Frontend job skipped | `FRONTEND_DEPLOY_ENABLED` not true in the context used by the job | Configure the flag in GitHub variables as required by the workflow |
| API calls go to localhost in production | Missing `VITE_API_BASE_URL=/api` | Rebuild with production Vite variables |
| CloudFront returns old UI | Cached assets or missing invalidation | Check invalidation status and `index.html` cache control |
| S3 access denied through CloudFront | Missing OAC bucket policy | Run `ensure-cloudfront.sh` with correct account and distribution |
| Direct S3 website endpoint fails | Expected current behavior | Frontend bucket is private and should be accessed through CloudFront |
| Socket.IO fails | Missing `/socket.io/*` CloudFront behavior or ALB route | Verify CloudFront behavior and Ingress path |

## Removal of old Kubernetes frontend resources

The current architecture intentionally removes frontend Kubernetes resources. Do not recreate:

- `Deployment/frontend`
- `Service/frontend`
- frontend HPA
- frontend PDB
- frontend-specific ALB Ingress
- `FRONTEND_IMAGE` deployment path for EKS app deploy

The frontend is built once and served as static files from S3 and CloudFront.

## Outcome

Frontend deployment is complete when the Vite build is in S3, CloudFront has invalidated cached objects, public users can load the application through `https://dhm2rz5nmsibj.cloudfront.net`, and dynamic routes reach backend/chat through CloudFront and the ALB.
