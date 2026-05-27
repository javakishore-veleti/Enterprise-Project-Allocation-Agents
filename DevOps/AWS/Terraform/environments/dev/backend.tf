# Partial S3 backend — bucket/key/region supplied via `-backend-config` in CI
# (see .github/workflows/aws-terraform.yml). For local validation, run
# `terraform init -backend=false`.
terraform {
  backend "s3" {}
}
