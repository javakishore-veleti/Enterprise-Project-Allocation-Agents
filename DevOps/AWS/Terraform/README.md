# AWS Terraform (dev)

Modular IaC for the EPAA cloud deployment. Applied module-by-module via the
numbered GitHub Actions workflows (`.github/workflows/00N-AWS-Deploy-*.yml` /
`00N-AWS-Destroy-*.yml`).

## Modules

| # | Module | What it provisions |
|---|--------|--------------------|
| 001 | `vpc` | VPC, 2 public + 2 private subnets, IGW, NAT, route tables |
| 002 | `bedrock` | IAM policy to invoke Bedrock foundation/embedding models |
| 003 | `rds` | Postgres (pgvector-capable) + SG + subnet group (in the VPC) |
| 004 | `sagemaker` | Studio domain + execution role (HF model experiments) |
| 005 | `ecs` | Fargate cluster, exec/task roles, log group (services layered on top) |
| 006 | `cognito` | User pool + app client for the portals |
| 007 | `cloudfront` | S3 (private) + CloudFront (OAC) per portal — instantiated twice |

Composition: `environments/dev` (module names are the `-target`s the workflows use).

## Deploy order

Workflows are numbered by dependency order; deploy ascending, destroy descending.
`terraform validate` + `terraform fmt` are clean.

## CI auth & state (AWS access keys in GitHub Secrets)

The AWS Deploy/Destroy workflows are **manual only** (`workflow_dispatch`) and
authenticate with AWS access keys stored in GitHub repository secrets:

| Secret | Purpose |
|--------|---------|
| `AWS_ACCESS_KEY_ID` | IAM user access key id (deploy permissions) |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret access key |
| `TF_STATE_BUCKET` | S3 bucket for remote state |
| `TF_LOCK_TABLE` | DynamoDB table for state locking |
| `EPAA_DB_PASSWORD` | RDS master password (`TF_VAR_db_password`) |

One-time bootstrap (outside these workflows): the deploy IAM user + keys, the S3
state bucket, and the DynamoDB lock table.

> Access keys are simpler than OIDC but are long-lived — scope the IAM user
> tightly and rotate the keys periodically.

## Local

```bash
cd environments/dev
terraform init -backend=false      # validate only (no remote state)
terraform validate
terraform fmt -recursive ../..
```
