terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "region" {
  type = string
  default = "us-east-1"
}

module "vpc" {
  source = "./modules/vpc"
  environment = var.environment
  tenant_id = var.tenant_id
}

module "kubernetes" {
  source = "./modules/kubernetes"
  environment = var.environment
  vpc_id = module.vpc.id
}

module "database" {
  source = "./modules/database"
  environment = var.environment
  vpc_id = module.vpc.id
}

module "monitoring" {
  source = "./modules/monitoring"
  environment = var.environment
}
