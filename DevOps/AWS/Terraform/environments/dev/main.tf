# EPAA dev environment. Module names below are the `-target`s used by the
# numbered AWS Deploy/Destroy workflows (001 vpc … 007 cloudfront).

module "vpc" {
  source      = "../../modules/vpc"
  name_prefix = var.name_prefix
}

module "bedrock" {
  source      = "../../modules/bedrock"
  name_prefix = var.name_prefix
}

module "rds" {
  source             = "../../modules/rds"
  name_prefix        = var.name_prefix
  vpc_id             = module.vpc.vpc_id
  vpc_cidr           = "10.20.0.0/16"
  private_subnet_ids = module.vpc.private_subnet_ids
  db_password        = var.db_password
}

module "sagemaker" {
  source                    = "../../modules/sagemaker"
  name_prefix               = var.name_prefix
  vpc_id                    = module.vpc.vpc_id
  subnet_ids                = module.vpc.private_subnet_ids
  bedrock_invoke_policy_arn = module.bedrock.bedrock_invoke_policy_arn
}

module "ecs" {
  source                    = "../../modules/ecs"
  name_prefix               = var.name_prefix
  bedrock_invoke_policy_arn = module.bedrock.bedrock_invoke_policy_arn
}

module "cognito" {
  source      = "../../modules/cognito"
  name_prefix = var.name_prefix
}

module "cloudfront_admin" {
  source      = "../../modules/cloudfront"
  name_prefix = var.name_prefix
  site_name   = "admin-portal"
}

module "cloudfront_projects" {
  source      = "../../modules/cloudfront"
  name_prefix = var.name_prefix
  site_name   = "projects-portal"
}
