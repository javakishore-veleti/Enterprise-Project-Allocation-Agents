# SageMaker Studio domain + execution role (for hosting/experimenting with HF
# models as a Bedrock alternative). Bedrock invoke policy is attached so notebooks
# can call Bedrock too.
variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "bedrock_invoke_policy_arn" {
  type    = string
  default = null
}
variable "tags" {
  type    = map(string)
  default = {}
}

data "aws_iam_policy_document" "assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["sagemaker.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${var.name_prefix}-sagemaker-exec"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "sagemaker_full" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy_attachment" "bedrock" {
  count      = var.bedrock_invoke_policy_arn == null ? 0 : 1
  role       = aws_iam_role.execution.name
  policy_arn = var.bedrock_invoke_policy_arn
}

resource "aws_sagemaker_domain" "this" {
  domain_name = "${var.name_prefix}-studio"
  auth_mode   = "IAM"
  vpc_id      = var.vpc_id
  subnet_ids  = var.subnet_ids

  default_user_settings {
    execution_role = aws_iam_role.execution.arn
  }
  tags = var.tags
}

output "sagemaker_domain_id" { value = aws_sagemaker_domain.this.id }
output "sagemaker_execution_role_arn" { value = aws_iam_role.execution.arn }
