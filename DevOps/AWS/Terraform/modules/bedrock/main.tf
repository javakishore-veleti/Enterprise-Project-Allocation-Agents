# Bedrock model access is granted at the account level (console / CLI). This
# module provisions the IAM policy that workloads (ECS tasks, SageMaker) attach
# to invoke the foundation + embedding models.
variable "name_prefix" { type = string }
variable "tags" {
  type    = map(string)
  default = {}
}

data "aws_iam_policy_document" "bedrock_invoke" {
  statement {
    sid    = "InvokeBedrockModels"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = ["arn:aws:bedrock:*::foundation-model/*"]
  }
}

resource "aws_iam_policy" "bedrock_invoke" {
  name   = "${var.name_prefix}-bedrock-invoke"
  policy = data.aws_iam_policy_document.bedrock_invoke.json
  tags   = var.tags
}

output "bedrock_invoke_policy_arn" { value = aws_iam_policy.bedrock_invoke.arn }
