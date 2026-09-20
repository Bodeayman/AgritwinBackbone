# AgriTwin Monorepo

Agricultural management system with disease detection, crop mix optimization, and yield prediction.

## Services

- **backbone/**: Main AgriTwin backend API (FastAPI + PostgreSQL + MinIO + RabbitMQ)
- **classical-classifier/**: Classical ML classifier service (placeholder)
- **vlm-classifier/**: Vision-Language Model classifier service (placeholder)

## Quick Start

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backbone
```

## Service Ports

- **backbone**: http://localhost:8000
- **classical-classifier**: http://localhost:8001
- **vlm-classifier**: http://localhost:8002
- **PostgreSQL**: localhost:5432
- **MinIO**: localhost:9000 (API), localhost:9001 (Console)
- **RabbitMQ**: localhost:5672 (AMQP), localhost:15672 (Management)

## Development

Each service can be developed independently. The backbone service contains the main AgriTwin application with all existing functionality.