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

locals {
  tags = {
    Project     = "enterprise-project-allocation-agents"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
