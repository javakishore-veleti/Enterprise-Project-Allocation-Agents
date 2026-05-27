output "vpc_id" { value = module.vpc.vpc_id }
output "rds_endpoint" { value = module.rds.db_endpoint }
output "ecs_cluster_arn" { value = module.ecs.cluster_arn }
output "bedrock_invoke_policy_arn" { value = module.bedrock.bedrock_invoke_policy_arn }
output "sagemaker_domain_id" { value = module.sagemaker.sagemaker_domain_id }
output "cognito_user_pool_id" { value = module.cognito.user_pool_id }
output "admin_portal_cdn" { value = module.cloudfront_admin.distribution_domain }
output "projects_portal_cdn" { value = module.cloudfront_projects.distribution_domain }
