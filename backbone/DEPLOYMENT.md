# AgriTwin Backend - EC2 Deployment Guide

## Table of Contents

- [Prerequisites](#prerequisites)
- [EC2 Instance Setup](#ec2-instance-setup)
- [Security Group Rules](#security-group-rules)
- [Server Initial Configuration](#server-initial-configuration)
- [Environment Variables](#environment-variables)
- [First Deployment](#first-deployment)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)
- [Operations](#operations)
- [Troubleshooting](#troubleshooting)
- [Rollback](#rollback)

---

## Prerequisites

- An AWS EC2 Ubuntu instance (Ubuntu 22.04 LTS or 24.04 LTS recommended)
- A GitHub repository with the AgriTwin Backend code
- SSH key pair for EC2 access
- Domain name (optional, for HTTPS)

---

## EC2 Instance Setup

### Recommended Instance Type

- **t3.medium** (2 vCPU, 4 GB RAM) minimum for all services
- **t3.large** or **c5.large** for production workloads
- EBS volume: 30 GB minimum ( gp3 recommended)

### Launch Configuration

1. AMI: Ubuntu Server 22.04 LTS or 24.04 LTS
2. Instance type: t3.medium or larger
3. Key pair: Create or select an existing key pair
4. Storage: 30 GB gp3

---

## Security Group Rules

Create a security group with the following rules:

### Inbound

| Type       | Port  | Source          | Purpose                     |
|------------|-------|-----------------|-----------------------------|
| SSH        | 22    | Your IP only    | SSH access                  |
| HTTP       | 80    | 0.0.0.0/0       | HTTP (if using reverse proxy) |
| HTTPS      | 443   | 0.0.0.0/0       | HTTPS (if using reverse proxy) |
| Custom TCP | 8000  | Your IP only    | API (direct access, optional) |

### Outbound

| Type   | Port | Destination | Purpose         |
|--------|------|-------------|-----------------|
| All    | All  | 0.0.0.0/0   | Outbound access |

### Internal Services (NOT exposed to internet)

These ports are bound to `127.0.0.1` inside Docker Compose and are only accessible from the EC2 host itself:

- PostgreSQL: `127.0.0.1:5432`
- MinIO API: `127.0.0.1:9000`
- MinIO Console: `127.0.0.1:9001`
- RabbitMQ: `127.0.0.1:5672`
- RabbitMQ Management: `127.0.0.1:15672`

---

## Server Initial Configuration

SSH into the EC2 instance and run these commands:

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify Docker installation
docker --version
docker compose version

# Create deployment directory
sudo mkdir -p /opt/agritwin-backend
sudo chown $USER:$USER /opt/agritwin-backend
```

---

## Environment Variables

### Create the environment file on the EC2 server

```bash
cd /opt/agritwin-backend
cp .env.example .env
nano .env
```

### Required Variables

Fill in all `CHANGE_ME` values in `.env`. At minimum, you must configure:

| Variable | How to Generate |
|----------|-----------------|
| `POSTGRES_PASSWORD` | `openssl rand -base64 32` |
| `JWT_SECRET_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `MINIO_ROOT_PASSWORD` | `openssl rand -base64 32` |
| `RABBITMQ_DEFAULT_PASS` | `openssl rand -base64 32` |
| `INTERN_*_API_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |

### Important Notes

- `DATABASE_URL` for the web service is constructed automatically in `docker-compose.yml` using Docker service names
- Set `BACKEND_CORS_ORIGINS` to your actual domain(s) in production
- Never commit `.env` to version control

---

## First Deployment

### Clone the repository

```bash
cd /opt/agritwin-backend
git clone https://github.com/Bodeayman/AgritwinBackbone.git .
```

### Start all services

```bash
docker compose up -d --build
```

### Run database migrations

```bash
docker compose exec web alembic upgrade head
```

### Verify all services are running

```bash
docker compose ps
```

Expected output: all 4 services (db, minio, rabbitmq, web) should show `Up` status.

### Check application health

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status": "healthy", "project": "AgriTwin Backend", "version": "1.0.0"}
```

---

## CI/CD with GitHub Actions

### Required GitHub Secrets

Configure these in your GitHub repository under **Settings > Secrets and variables > Actions**:

| Secret | Description | Example |
|--------|-------------|---------|
| `EC2_HOST` | EC2 public IP or hostname | `54.123.45.67` |
| `EC2_USERNAME` | SSH username | `ubuntu` |
| `EC2_SSH_KEY` | Private SSH key (full PEM) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### How It Works

1. Push to `main` branch triggers the workflow
2. Tests run first (can be skipped with manual trigger)
3. Docker image is built locally
4. Image is copied to EC2 via SCP
5. Image is loaded on EC2 and the web service is recreated
6. Health check verifies the deployment
7. If health check fails, automatic rollback occurs

### Manual Deployment (without tests)

1. Go to **Actions > Deploy to EC2**
2. Click **Run workflow**
3. Check **Skip tests** if needed
4. Click **Run workflow**

---

## Operations

### Viewing Logs

```bash
# All services
docker compose logs

# Web service (follow mode)
docker compose logs -f web

# Database logs
docker compose logs -f db

# Last 100 lines
docker compose logs --tail 100 web
```

### Restarting Services

```bash
# Restart all services
docker compose restart

# Restart only the web service
docker compose restart web

# Full stop and start
docker compose down && docker compose up -d
```

### Checking Container Status

```bash
docker compose ps
docker stats --no-stream
```

### Updating the Deployment

```bash
cd /opt/agritwin-backend

# Pull latest code
git pull origin main

# Rebuild and restart
docker compose up -d --build --force-recreate web

# Run migrations if needed
docker compose exec web alembic upgrade head
```

### Stopping Services

```bash
docker compose down

# With volume removal (WARNING: destroys data)
docker compose down -v
```

---

## Rollback

### Automatic Rollback

The GitHub Actions deploy workflow automatically rolls back if the health check fails after deployment.

### Manual Rollback

If you need to rollback to a previous Docker image:

```bash
cd /opt/agritwin-backend

# Check available images
docker images agritwin-web

# Stop current web
docker compose down web

# Start with a specific image tag
DOCKER_IMAGE=agritwin-web:<previous-commit-sha> docker compose up -d web

# Or edit docker-compose.yml to use a specific image tag
# and run:
docker compose up -d web
```

### Rolling Back Code Changes

```bash
cd /opt/agritwin-backend

# Revert to a previous commit
git log --oneline -10
git checkout <commit-hash> -- .

# Rebuild and restart
docker compose up -d --build web

# Rollback database if needed
docker compose exec web alembic downgrade -1
```

---

## Troubleshooting

### Container won't start

```bash
# Check container logs
docker compose logs web

# Check if port is in use
sudo lsof -i :8000

# Inspect container
docker inspect agritwin_web
```

### Database connection errors

```bash
# Verify database is running
docker compose ps db

# Test connection from inside the web container
docker compose exec web python -c "from sqlalchemy import create_engine; e = create_engine('postgresql://postgres:PASSWORD@db:5432/agritwin'); e.connect()"

# Check database logs
docker compose logs db
```

### MinIO connection errors

```bash
# Check MinIO is running
docker compose ps minio

# Test MinIO health
curl http://localhost:9000/minio/health/live
```

### Application health check fails

```bash
# Check web container logs for errors
docker compose logs web

# Verify the web container is listening
docker compose exec web ss -tlnp

# Check if uvicorn is running inside the container
docker compose exec web ps aux
```

### Disk space issues

```bash
# Check disk usage
df -h

# Clean up Docker resources
docker system prune -f

# Remove old images
docker image prune -f
```

### Out of memory

```bash
# Check memory usage
docker stats --no-stream

# Check system memory
free -h

# Restart services if needed
docker compose restart
```

---

## EC2 Directory Structure

### Manual first deployment (full source)

```
/opt/agritwin-backend/
├── docker-compose.yml
├── .env                    # Environment variables (not in git)
├── .env.example            # Template
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── app/
├── migrations/
├── tests/
└── .git/
```

### After GitHub Actions CI/CD deployment

The workflow copies only the Compose file and the pre-built Docker image
tarball. Only `docker-compose.yml` and `.env` are required on the server;
the application code runs from the Docker image:

```
/opt/agritwin-backend/
├── docker-compose.yml
├── .env                    # Environment variables (not in git)
├── .previous_image         # Reference to the image before last deploy (rollback)
└── agritwin-image.tar.gz   # (temporary, removed after loading)
```

---

## Architecture Overview

```
Internet
    │
    ▼
┌─────────────────────────────────┐
│  EC2 Instance (Ubuntu)          │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Docker Network: agritwin │  │
│  │                           │  │
│  │  ┌─────────┐ ┌─────────┐ │  │
│  │  │   web   │ │   db    │ │  │
│  │  │ :8000*  │ │ :5432   │ │  │
│  │  └────┬────┘ └─────────┘ │  │
│  │       │                   │  │
│  │  ┌────┴────┐ ┌─────────┐ │  │
│  │  │  minio  │ │rabbitmq │ │  │
│  │  │ :9000*  │ │ :5672   │ │  │
│  │  └─────────┘ └─────────┘ │  │
│  └───────────────────────────┘  │
│                                 │
│  * Ports bound to 127.0.0.1    │
│    (internal only)              │
└─────────────────────────────────┘
```

Only port 8000 (or 443 with a reverse proxy) is accessible from outside.
