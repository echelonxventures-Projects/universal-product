# Production Deployment Guide

## Overview

This guide covers deploying UCII Ω∞ to production environments.

## Prerequisites

- AWS account (or compatible cloud provider)
- Terraform 1.5+
- kubectl
- Docker

## Infrastructure Setup

### 1. Configure Environment

```bash
# Set environment variables
export TF_VAR_environment=production
export TF_VAR_tenant_id=your-tenant-id
export TF_VAR_region=us-east-1
```

### 2. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 3. Configure Kubernetes

```bash
kubectl apply -f infrastructure/k8s/base/
```

## Service Deployment

### Database Migration

```bash
npm run migrate:up
```

### Application Deployment

```bash
npm run build
docker build -t uci-platform:latest .
docker push uci-platform:latest
kubectl apply -f infrastructure/k8s/
```

## Monitoring

Access monitoring dashboards:

- Metrics: http://prometheus:9090
- Tracing: http://jaeger:16686

## Security Hardening

1. Enable SSL/TLS termination
2. Configure WAF rules
3. Set up DDoS protection
4. Enable audit logging

## Scaling

Adjust deployment replicas:

```yaml
# infrastructure/k8s/base/deployments/api.yaml
spec:
  replicas: 5
```

## Disaster Recovery

1. Enable database automated backups
2. Configure multi-region failover
3. Test restore procedures regularly
