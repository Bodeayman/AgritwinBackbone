# Multi-Server Architecture Strategy

## Executive Summary

AgriTwin Backend is currently implemented as a **modular monolith** with clear N-Tier separation. This document outlines the recommended scaling strategy, which prioritizes horizontal scaling of the monolith before considering microservices decomposition.

## Current Architecture Assessment

### Current State: Modular Monolith

**Architecture Type:** Modular Monolith with N-Tier Layering

**Strengths:**
- Simple deployment and operations
- Clear separation of concerns (API, Services, Repositories, Models)
- Fast development iteration
- Lower operational complexity
- Easier testing and debugging
- No network latency between components
- Single transaction boundary (simpler data consistency)

**Current Limitations:**
- Single point of failure (no horizontal scaling)
- Limited by single server resources
- All components must scale together
- Technology choices apply to entire application

**Conclusion:** The current architecture is appropriate for the current scale and team size. Continue with modular monolith approach until specific microservices drivers emerge.

## Scaling Strategy: Horizontal Scaling First

### Phase 1: Stateless Horizontal Scaling (Recommended First Step)

**Goal:** Deploy multiple instances of the monolith behind a load balancer.

#### Architecture Diagram

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │  (Nginx/HAProxy)│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │Backend 1 │   │Backend 2 │   │Backend 3 │
         │ Instance │   │ Instance │   │ Instance │
         └────┬────┘   └────┬────┘   └────┬────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │PostgreSQL│  │  MinIO  │  │  Redis  │
         │ (Primary)│  │         │  │         │
         └─────────┘   └─────────┘   └─────────┘
```

#### Implementation Steps

1. **Ensure Application is Stateless**
   - Current state: Application uses database and external storage (MinIO)
   - No in-memory session storage (good)
   - JWT tokens are stateless (good)
   - Action: Verify no local file dependencies that aren't in MinIO

2. **Load Balancer Configuration**
   - Use Nginx, HAProxy, or cloud load balancer (AWS ALB, GCP Load Balancing)
   - Configure round-robin or least-connections algorithm
   - Enable health checks on `/` endpoint
   - Configure sticky sessions if needed (not required for JWT-based auth)

3. **Multiple Backend Instances**
   - Deploy 2-4 instances initially
   - Use container orchestration: Docker Swarm or Kubernetes
   - Configure auto-scaling based on CPU/memory metrics
   - Use rolling deployments for zero-downtime updates

4. **Shared Database**
   - Single PostgreSQL instance with connection pooling
   - Configure PgBouncer for connection pooling (recommended)
   - Monitor connection counts and adjust pool size
   - Consider read replicas for read-heavy workloads (Phase 2)

5. **Shared Storage**
   - Single MinIO instance or cloud S3
   - All instances share the same storage backend
   - Implement CDN (CloudFront, Cloudflare) for static assets
   - Configure pre-signed URLs for direct access

6. **Caching Layer (Redis)**
   - Add Redis for:
     - API response caching (field data, satellite info)
     - Rate limiting
     - Distributed locking (for concurrent operations)
     - Session storage (if needed in future)
   - Configure Redis with persistence (AOF + RDB)
   - Use Redis Cluster for high availability

#### Load Balancer Configuration Example (Nginx)

```nginx
upstream agritwin_backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.agritwin.com;

    location / {
        proxy_pass http://agritwin_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /health {
        access_log off;
        proxy_pass http://agritwin_backend;
    }
}
```

#### Docker Compose for Horizontal Scaling

```yaml
version: "3.8"

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web1
      - web2
      - web3

  web1:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      # ... other env vars
    depends_on:
      - db
      - minio
      - redis

  web2:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      # ... other env vars
    depends_on:
      - db
      - minio
      - redis

  web3:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      # ... other env vars
    depends_on:
      - db
      - minio
      - redis

  db:
    image: postgis/postgis:15-3.4
    # ... configuration

  minio:
    image: minio/minio:RELEASE.2024-06-06T09-36-42Z
    # ... configuration

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data
```

### Phase 2: Database Scaling

**Goal:** Improve database performance and availability.

#### Strategies

1. **Connection Pooling**
   - Deploy PgBouncer in transaction pooling mode
   - Reduces database connection overhead
   - Allows more concurrent application connections

2. **Read Replicas**
   - Configure PostgreSQL streaming replication
   - Route read queries to replicas
   - Writes go to primary
   - Improves read-heavy workload performance

3. **Database Sharding (Future)**
   - Consider only if single instance cannot handle load
   - Shard by farm_id or field_id (natural domain boundaries)
   - Adds complexity - defer until necessary

### Phase 3: Async Processing with Message Queue

**Goal:** Offload long-running tasks from HTTP request cycle.

#### Current State
- RabbitMQ is configured but not actively used
- All processing is synchronous in HTTP handlers

#### Recommended Implementation

1. **Task Queue for Async Operations**
   - Image processing and analysis
   - Satellite data ingestion
   - AI model inference
   - Report generation

2. **Message Queue Architecture**

```
┌─────────────┐
│   Backend   │
│   (HTTP)    │
└──────┬──────┘
       │
       │ Publish tasks
       ▼
┌─────────────┐
│  RabbitMQ   │
└──────┬──────┘
       │
       │ Consume tasks
       ▼
┌─────────────┐
│   Workers   │
│ (Celery/    │
│  aio-pika)  │
└─────────────┘
```

3. **Implementation with Celery**

```python
# tasks.py
from celery import Celery

celery_app = Celery('agritwin', broker='pyamqp://guest@localhost//')

@celery_app.task
def process_satellite_imagery(observation_id: int):
    # Long-running image processing
    pass

@celery_app.task
def run_diagnosis_model(imagery_id: int, model_id: int):
    # AI model inference
    pass
```

4. **Benefits**
- Improved HTTP response times
- Better resource utilization
- Retry and error handling built-in
- Task prioritization

## When to Consider Microservices

### Microservices Drivers

**Consider splitting into microservices when:**

1. **Team Scaling**
   - Team size exceeds 10-15 developers
   - Multiple teams need independent deployment cycles
   - Different teams own different domains

2. **Different Scaling Requirements**
   - Image processing needs GPU instances
   - API endpoints need many CPU cores
   - Satellite ingestion needs high memory
   - Cannot efficiently scale all components together

3. **Different Deployment Frequencies**
   - AI models need daily updates
   - Core API needs weekly updates
   - UI/UX changes need frequent deployments

4. **Technology Divergence**
   - Image processing requires Python + PyTorch
   - Real-time API requires Go/Node.js
   - Data pipeline requires Scala/Spark

5. **Fault Isolation**
   - One component causing instability should not affect others
   - Need independent failure domains

### Potential Microservice Boundaries

If microservices become necessary, consider these boundaries:

#### 1. Image Processing Service
- **Responsibility:** Image upload, processing, analysis
- **Tech Stack:** Python + PyTorch/TensorFlow + GPU
- **Scaling:** GPU-intensive, separate scaling
- **Communication:** gRPC (high performance) or REST

#### 2. AI Model Inference Service
- **Responsibility:** AI model serving, predictions
- **Tech Stack:** Python + ONNX Runtime / TensorFlow Serving
- **Scaling:** GPU-intensive, separate scaling
- **Communication:** gRPC

#### 3. Satellite Data Ingestion Service
- **Responsibility:** Satellite data processing, normalization
- **Tech Stack:** Python + GeoPandas + Rasterio
- **Scaling:** High-throughput, CPU-intensive
- **Communication:** Message queue (RabbitMQ/Kafka)

#### 4. Notification Service
- **Responsibility:** Email, SMS, push notifications
- **Tech Stack:** Node.js or Go
- **Scaling:** Event-driven, burst traffic
- **Communication:** Message queue

### Microservices Challenges

**Operational Complexity:**
- Distributed system debugging
- Network latency and failures
- Service discovery
- Configuration management
- Monitoring and observability

**Data Consistency:**
- Distributed transactions (Saga pattern)
- Eventual consistency
- Data duplication across services

**Testing:**
- Integration testing complexity
- Contract testing
- End-to-end testing

**Deployment:**
- Orchestration complexity
- Version compatibility
- Rolling updates across services

### Recommendation: Defer Microservices

**Do NOT split prematurely.** Microservices add significant complexity. The modular monolith can scale horizontally to handle significant load before microservices are necessary.

**Continue with modular monolith until:**
- Clear business need for independent scaling
- Team size justifies operational overhead
- Specific components require different technology stacks
- Revenue justifies increased operational costs

## Service Communication

### Current: REST over HTTP

**Pros:**
- Simple, well-understood
- Good for public APIs
- Built-in JSON serialization
- Language-agnostic
- Easy to test and debug

**Cons:**
- Higher overhead than binary protocols
- No built-in streaming
- Verb-based (GET, POST, etc.)

### Future Options

#### gRPC (for Internal Service-to-Service)

**Use cases:**
- High-performance internal communication
- Strong typing with Protocol Buffers
- Bidirectional streaming
- Microservices architecture

**Example:**

```protobuf
// satellite_service.proto
service SatelliteService {
  rpc GetSatellite(GetSatelliteRequest) returns (Satellite);
  rpc ListSatellites(ListSatellitesRequest) returns (stream Satellite);
}
```

**Pros:**
- Binary serialization (faster)
- Strong typing
- Built-in code generation
- Bidirectional streaming
- Smaller payload size

**Cons:**
- More complex setup
- Not human-readable
- Requires Protocol Buffers knowledge

#### Message Queues (for Async Communication)

**Use cases:**
- Event-driven architecture
- Decoupling components
- Retry and error handling
- Backpressure handling

**Technologies:**
- RabbitMQ (current, configured)
- Apache Kafka (for high-throughput streaming)
- AWS SQS/SNS (cloud-native)

#### GraphQL (for Flexible Client Queries)

**Use cases:**
- Flexible client data requirements
- Reducing over-fetching/under-fetching
- Aggregating data from multiple sources

**Note:** Consider GraphQL as an API layer on top of the monolith, not a backend replacement.

## Deployment Architecture

### Development Environment

```
┌─────────────┐
│ Developer   │
│   Laptop    │
└──────┬──────┘
       │
       │ Docker Compose
       ▼
┌─────────────┐
│  All-in-One │
│  Container  │
│  (db+app)   │
└─────────────┘
```

### Staging Environment

```
                    ┌─────────────┐
                    │ Load Balancer│
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         ┌────▼────┐              ┌────▼────┐
         │Backend 1│              │Backend 2│
         └────┬────┘              └────┬────┘
              │                         │
              └────────────┬────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         ┌────▼────┐              ┌────▼────┐
         │   DB    │              │  MinIO  │
         │ (Staging)│              │(Staging)│
         └─────────┘              └─────────┘
```

### Production Environment

```
                    ┌─────────────────┐
                    │  CDN / WAF      │
                    │ (CloudFlare/    │
                    │  AWS CloudFront)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Load Balancer  │
                    │  (AWS ALB/GCP)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │Backend 1│   │Backend 2│   │Backend N│
         │  (AZ 1) │   │  (AZ 2) │   │  (AZ 3) │
         └────┬────┘   └────┬────┘   └────┬────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │   DB    │   │  MinIO  │   │  Redis  │
         │ (Primary)│  │ (S3/MinIO)│  │(ElastiCache)│
         └────┬────┘   └─────────┘   └─────────┘
              │
         ┌────▼────┐
         │Read Replicas│
         │(Multi-AZ)   │
         └─────────────┘
```

## Infrastructure Recommendations

### Cloud Providers

**Recommended:**
- **AWS**: Most mature, extensive services (RDS, S3, ElastiCache, ALB)
- **GCP**: Good ML/AI integration (BigQuery, AI Platform)
- **Azure**: Good enterprise integration, hybrid cloud support

### Managed Services

**Database:**
- AWS RDS for PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL

**Storage:**
- AWS S3 (recommended)
- Google Cloud Storage
- Azure Blob Storage

**Caching:**
- AWS ElastiCache for Redis
- Google Memorystore
- Azure Cache for Redis

**Message Queue:**
- AWS SQS/SNS
- Google Pub/Sub
- Azure Service Bus

### Container Orchestration

**For Horizontal Scaling:**
- **Kubernetes**: Industry standard, steep learning curve
- **Docker Swarm**: Simpler, good for smaller deployments
- **Managed Kubernetes**: EKS, GKE, AKS (recommended)

## Monitoring and Observability

### Required Monitoring

1. **Application Metrics**
   - Request rate, latency, error rate
   - Database query performance
   - External service latency
   - Resource utilization (CPU, memory)

2. **Infrastructure Metrics**
   - Server health
   - Database connections
   - Disk usage
   - Network throughput

3. **Business Metrics**
   - Active users
   - API usage by endpoint
   - Data ingestion rates
   - Model inference latency

### Recommended Tools

- **Metrics:** Prometheus + Grafana
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana) or CloudWatch
- **Tracing:** Jaeger or OpenTelemetry
- **APM:** Datadog, New Relic, or Sentry

## Security Considerations

### Multi-Instance Security

1. **Service-to-Service Authentication**
   - mTLS between services
   - Shared secrets or JWT
   - Network policies (Kubernetes Network Policies)

2. **Network Segmentation**
   - Separate subnets for web, database, cache
   - Security groups / firewall rules
   - Private API endpoints for internal communication

3. **Secrets Management**
   - AWS Secrets Manager / Parameter Store
   - HashiCorp Vault
   - Kubernetes Secrets (with encryption)

4. **TLS/SSL**
   - HTTPS for all external endpoints
   - TLS for internal service communication
   - Certificate rotation automation

## Cost Optimization

### Strategies

1. **Right-Sizing Instances**
   - Monitor actual resource usage
   - Choose appropriate instance types
   - Use auto-scaling to scale down during low traffic

2. **Reserved Instances**
   - Commit to 1-3 year terms for predictable workloads
   - Significant cost savings (up to 70%)

3. **Spot Instances**
   - Use for fault-tolerant workloads (workers, batch jobs)
   - Up to 90% cost savings

4. **Storage Optimization**
   - Use S3 lifecycle policies
   - Move old data to cold storage (Glacier)
   - Compress logs and archives

## Migration Path

### Step-by-Step Migration to Multi-Instance

1. **Phase 1: Preparation (1-2 weeks)**
   - Ensure application is stateless
   - Add health check endpoints
   - Configure structured logging
   - Set up monitoring

2. **Phase 2: Infrastructure Setup (1-2 weeks)**
   - Set up load balancer
   - Configure Redis cache
   - Set up PgBouncer
   - Configure CI/CD for multi-instance deployment

3. **Phase 3: Testing (1 week)**
   - Deploy 2 instances behind load balancer
   - Run load tests
   - Verify session handling
   - Test failover scenarios

4. **Phase 4: Production Rollout (1-2 weeks)**
   - Gradual traffic shift
   - Monitor performance metrics
   - Scale to target instance count
   - Optimize based on real-world data

5. **Phase 5: Optimization (Ongoing)**
   - Implement caching strategies
   - Add read replicas if needed
   - Implement async processing
   - Continue monitoring and tuning

## Conclusion

**Recommendation:** Implement horizontal scaling of the modular monolith before considering microservices. This approach provides:

- Simpler operations
- Faster development
- Lower cost
- Adequate scaling for most use cases

**Microservices should be considered only when:**
- Clear business need for independent scaling
- Team size justifies operational overhead
- Specific components require different technology stacks

The current modular monolith architecture with N-Tier separation is well-designed and can scale horizontally to handle significant load. Focus on implementing horizontal scaling, caching, and async processing before exploring microservices decomposition.
