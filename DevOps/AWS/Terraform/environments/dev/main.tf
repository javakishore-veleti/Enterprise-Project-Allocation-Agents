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
  vpc_id                    = module.vpc.vpc_id
  bedrock_invoke_policy_arn = module.bedrock.bedrock_invoke_policy_arn
}

# Per-app Fargate services on the cluster. Images come from ECR (push via CI);
# set the *_image vars at apply time.
module "svc_agents" {
  source             = "../../modules/ecs-service"
  name_prefix        = var.name_prefix
  service_name       = "agents"
  cluster_arn        = module.ecs.cluster_arn
  image              = var.agents_image
  container_port     = 8001
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_id  = module.ecs.service_security_group_id
  execution_role_arn = module.ecs.execution_role_arn
  task_role_arn      = module.ecs.task_role_arn
  log_group          = module.ecs.log_group_name
  region             = var.region
  environment = {
    POSTGRES_HOST = module.rds.db_endpoint
    POSTGRES_DB   = "epaa"
  }
}

module "svc_datalake" {
  source             = "../../modules/ecs-service"
  name_prefix        = var.name_prefix
  service_name       = "datalake-api"
  cluster_arn        = module.ecs.cluster_arn
  image              = var.datalake_image
  container_port     = 8000
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_id  = module.ecs.service_security_group_id
  execution_role_arn = module.ecs.execution_role_arn
  task_role_arn      = module.ecs.task_role_arn
  log_group          = module.ecs.log_group_name
  region             = var.region
  environment = {
    POSTGRES_HOST = module.rds.db_endpoint
    POSTGRES_DB   = "epaa"
  }
}

module "svc_gateway" {
  source             = "../../modules/ecs-service"
  name_prefix        = var.name_prefix
  service_name       = "api-gateway"
  cluster_arn        = module.ecs.cluster_arn
  image              = var.gateway_image
  container_port     = 8080
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_id  = module.ecs.service_security_group_id
  execution_role_arn = module.ecs.execution_role_arn
  task_role_arn      = module.ecs.task_role_arn
  log_group          = module.ecs.log_group_name
  region             = var.region
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
