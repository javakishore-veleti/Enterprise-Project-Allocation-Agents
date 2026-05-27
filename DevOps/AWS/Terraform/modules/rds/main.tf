# Postgres for the app (pgvector available via `CREATE EXTENSION vector`).
variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "vpc_cidr" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "db_name" {
  type    = string
  default = "epaa"
}
variable "db_username" {
  type    = string
  default = "epaa"
}
variable "db_password" {
  type      = string
  sensitive = true
}
variable "instance_class" {
  type    = string
  default = "db.t4g.micro"
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-db-subnets"
  subnet_ids = var.private_subnet_ids
  tags       = var.tags
}

resource "aws_security_group" "db" {
  name   = "${var.name_prefix}-db-sg"
  vpc_id = var.vpc_id
  ingress {
    description = "Postgres from within the VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

resource "aws_db_instance" "this" {
  identifier              = "${var.name_prefix}-pg"
  engine                  = "postgres"
  engine_version          = "16.4"
  instance_class          = var.instance_class
  allocated_storage       = 20
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  skip_final_snapshot     = true
  publicly_accessible     = false
  backup_retention_period = 1
  tags                    = var.tags
}

output "db_endpoint" { value = aws_db_instance.this.address }
output "db_port" { value = aws_db_instance.this.port }
output "db_security_group_id" { value = aws_security_group.db.id }
