# terraform/variables.tf
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Domain name for the website"
  type        = string
  default     = "thabojafta.co.za"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}