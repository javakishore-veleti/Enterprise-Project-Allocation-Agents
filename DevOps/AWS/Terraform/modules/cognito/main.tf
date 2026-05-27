# Cognito user pool + app client for the portals (admin + customer).
variable "name_prefix" { type = string }
variable "callback_urls" {
  type    = list(string)
  default = ["http://localhost:4200", "http://localhost:4201"]
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "aws_cognito_user_pool" "this" {
  name = "${var.name_prefix}-users"
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_uppercase = true
    require_symbols   = false
  }
  tags = var.tags
}

resource "aws_cognito_user_pool_client" "web" {
  name                                 = "${var.name_prefix}-web"
  user_pool_id                         = aws_cognito_user_pool.this.id
  generate_secret                      = false
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  callback_urls                        = var.callback_urls
  supported_identity_providers         = ["COGNITO"]
}

resource "aws_cognito_user_pool_domain" "this" {
  domain       = "${var.name_prefix}-auth"
  user_pool_id = aws_cognito_user_pool.this.id
}

output "user_pool_id" { value = aws_cognito_user_pool.this.id }
output "user_pool_client_id" { value = aws_cognito_user_pool_client.web.id }
output "user_pool_domain" { value = aws_cognito_user_pool_domain.this.domain }
