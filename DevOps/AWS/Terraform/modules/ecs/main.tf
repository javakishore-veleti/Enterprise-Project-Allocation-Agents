# ECS Fargate cluster + shared roles/log group. Individual task definitions and
# services (agents, datalake, the 6 Spring services) are added per app on top of
# this foundation.
variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "bedrock_invoke_policy_arn" {
  type    = string
  default = null
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "aws_security_group" "service" {
  name        = "${var.name_prefix}-ecs-svc-sg"
  description = "EPAA ECS services"
  vpc_id      = var.vpc_id
  ingress {
    description = "intra-VPC service traffic"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

resource "aws_ecs_cluster" "this" {
  name = "${var.name_prefix}-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/ecs/${var.name_prefix}"
  retention_in_days = 14
  tags              = var.tags
}

data "aws_iam_policy_document" "assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${var.name_prefix}-ecs-exec"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task" {
  name               = "${var.name_prefix}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "task_bedrock" {
  count      = var.bedrock_invoke_policy_arn == null ? 0 : 1
  role       = aws_iam_role.task.name
  policy_arn = var.bedrock_invoke_policy_arn
}

output "cluster_arn" { value = aws_ecs_cluster.this.arn }
output "log_group_name" { value = aws_cloudwatch_log_group.this.name }
output "execution_role_arn" { value = aws_iam_role.execution.arn }
output "task_role_arn" { value = aws_iam_role.task.arn }
output "service_security_group_id" { value = aws_security_group.service.id }
