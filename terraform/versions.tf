# terraform/versions.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

# Provider configuration for us-east-1 (required for ACM certificates)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}