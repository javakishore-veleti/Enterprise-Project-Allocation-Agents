variable "region" {
  type    = string
  default = "us-east-1"
}

variable "name_prefix" {
  type    = string
  default = "epaa-dev"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "change-me-in-tfvars"
}

# Container images (ECR URIs); set at apply time after CI pushes them.
variable "agents_image" {
  type    = string
  default = "public.ecr.aws/docker/library/busybox:latest"
}
variable "datalake_image" {
  type    = string
  default = "public.ecr.aws/docker/library/busybox:latest"
}
variable "gateway_image" {
  type    = string
  default = "public.ecr.aws/docker/library/busybox:latest"
}

locals {
  tags = {
    Project     = "enterprise-project-allocation-agents"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
