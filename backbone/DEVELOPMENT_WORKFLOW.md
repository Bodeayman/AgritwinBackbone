# Development Workflow Guide

This document outlines the recommended development workflow for the AgriTwin Backend team, covering Git practices, code review, testing, and deployment processes.

## Table of Contents

- [Git Workflow](#git-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Guidelines](#commit-guidelines)
- [Code Review Process](#code-review-process)
- [Testing Strategy](#testing-strategy)
- [Database Changes](#database-changes)
- [Deployment Process](#deployment-process)
- [Environment Management](#environment-management)
- [Collaboration Guidelines](#collaboration-guidelines)

## Git Workflow

### Repository Structure

- **Main Branch:** `master` - Production-ready code
- **Remote:** `origin` - https://github.com/Bodeayman/AgritwinBackbone.git

### Workflow Overview

```
master (production)
    ↑
    │ merge
    │
feature/branch
    ↑
    │ pull request
    │
developer (local)
```

### Basic Git Commands

```bash
# Clone repository
git clone https://github.com/Bodeayman/AgritwinBackbone.git
cd AgriTwin

# Update local master branch
git checkout master
git pull origin master

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature description"

# Push feature branch
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Branching Strategy

### Branch Types

#### 1. Feature Branches
- **Purpose:** Develop new features
- **Naming:** `feature/<description>`
- **Examples:**
  - `feature/satellite-imagery-integration`
  - `feature/diagnosis-api-enhancement`
  - `feature/user-dashboard`

**Lifecycle:**
```bash
# Create from master
git checkout master
git pull origin master
git checkout -b feature/satellite-imagery-integration

# Develop and test
# ... make changes ...

# Push and create PR
git push origin feature/satellite-imagery-integration
# Create PR on GitHub
```

#### 2. Bugfix Branches
- **Purpose:** Fix bugs in production
- **Naming:** `bugfix/<description>`
- **Examples:**
  - `bugfix/weather-fk-constraint`
  - `bugfix/authentication-timeout`
  - `bugfix/diagnosis-json-parsing`

**Lifecycle:**
```bash
# Create from master
git checkout master
git pull origin master
git checkout -b bugfix/weather-fk-constraint

# Fix bug and test
# ... make changes ...

# Push and create PR
git push origin bugfix/weather-fk-constraint
# Create PR on GitHub
```

#### 3. Hotfix Branches (Urgent Production Fixes)
- **Purpose:** Critical production fixes requiring immediate deployment
- **Naming:** `hotfix/<description>`
- **Examples:**
  - `hotfix/security-vulnerability`
  - `hotfix/database-corruption`

**Lifecycle:**
```bash
# Create from master
git checkout master
git pull origin master
git checkout -b hotfix/security-vulnerability

# Fix critical issue
# ... make changes ...

# Push and create PR with high priority
git push origin hotfix/security-vulnerability
# Create PR and request immediate review
```

### Branch Protection Rules (Recommended)

Configure these rules in GitHub repository settings:

**For `master` branch:**
- Require pull request reviews before merging
  - Required approving reviewers: 1
- Require status checks to pass before merging
  - Required checks: `pytest`, `build`
- Require branches to be up to date before merging
- Do not allow bypassing the above settings

## Commit Guidelines

### Conventional Commits

Use conventional commit format for better readability and automation:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

| Type | Description | Examples |
|------|-------------|----------|
| `feat` | New feature | `feat(satellites): add satellite registry endpoints` |
| `fix` | Bug fix | `fix(weather): add missing foreign key constraint` |
| `docs` | Documentation only | `docs(readme): update API documentation` |
| `style` | Code style changes (formatting) | `style(models): fix indentation` |
| `refactor` | Code refactoring | `refactor(services): extract common logic` |
| `perf` | Performance improvements | `perf(database): add index on field_id` |
| `test` | Adding or updating tests | `test(diagnosis): add boundary box tests` |
| `chore` | Maintenance tasks | `chore(deps): update fastapi version` |
| `ci` | CI/CD changes | `ci(github): add pytest workflow` |

### Commit Examples

**Good commits:**
```bash
feat(satellites): add satellite entity and API endpoints

- Add Satellite model with name, provider, status fields
- Create satellite_repository.py for data access
- Add satellite_service.py for business logic
- Implement CRUD endpoints in satellites.py
- Add tests for satellite operations

Closes #123
```

```bash
fix(diagnosis): add missing leaf_boundary_box field

Diagnosis service was not saving leaf_boundary_box from
incoming requests. Added field to service create method
and schema.

Fixes #145
```

**Bad commits:**
```bash
# Too vague
git commit -m "update stuff"

# Too long
git commit -m "changed the database and added new endpoints and fixed bugs and updated tests"

# Missing type
git commit -m "add satellite endpoints"
```

### Commit Message Format

**Subject line:**
- Use imperative mood ("add" not "added")
- No period at end
- Limit to 50 characters
- Reference issue number if applicable

**Body:**
- Explain what and why, not how
- Wrap at 72 characters
- Use bullet points for lists

**Footer:**
- Reference issues with `Closes #123` or `Fixes #456`
- Breaking changes: `BREAKING CHANGE: description`

## Code Review Process

### Pull Request Workflow

#### 1. Before Creating PR

```bash
# Ensure your branch is up to date with master
git checkout master
git pull origin master
git checkout feature/your-feature
git rebase master

# Run tests
pytest

# Check code style (if configured)
black app tests
ruff check app tests

# Ensure database migrations are generated if needed
alembic revision --autogenerate -m "description"
alembic upgrade head
```

#### 2. Creating Pull Request

**PR Title:** Follow commit message format
```
feat(satellites): add satellite entity and API endpoints
```

**PR Description Template:**

```markdown
## Summary
Brief description of changes (2-3 sentences).

## Changes Made
- [ ] Added Satellite model
- [ ] Created satellite_repository.py
- [ ] Implemented satellite_service.py
- [ ] Added CRUD endpoints
- [ ] Added tests

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Database Changes
- [ ] Migration created: `abc123_add_satellite_table.py`
- [ ] Migration tested locally
- [ ] No breaking changes

## Breaking Changes
List any breaking changes here.

## Related Issues
Closes #123
```

#### 3. Code Review Checklist

**Functionality:**
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No hardcoded values (use config)

**Code Quality:**
- [ ] Code is readable and maintainable
- [ ] Follows existing code style
- [ ] No commented-out code
- [ ] No debugging code (print statements)
- [ ] Functions are small and focused

**Testing:**
- [ ] Tests are added for new functionality
- [ ] Existing tests still pass
- [ ] Test coverage is adequate
- [ ] Tests are not flaky

**Security:**
- [ ] No secrets or credentials committed
- [ ] Input validation is present
- [ ] SQL injection prevention (ORM used)
- [ ] Authentication/authorization is correct

**Documentation:**
- [ ] Code is self-documenting (good names)
- [ ] Complex logic has comments
- [ ] API documentation is updated
- [ ] README is updated if needed

#### 4. Review Feedback

**For Reviewers:**
- Be constructive and specific
- Explain why changes are needed
- Offer suggestions, not just criticism
- Use inline comments for specific issues
- Use general PR comments for overall feedback

**For Authors:**
- Respond to all review comments
- Make requested changes or discuss alternatives
- Mark resolved comments after addressing
- Request re-review after changes

#### 5. Merging

**Before merging:**
- [ ] All review comments addressed
- [ ] All CI checks pass
- [ ] No merge conflicts
- [ ] Branch is up to date with master

**Merge method:**
- Use "Squash and merge" for clean history
- Or use "Rebase and merge" for linear history
- Avoid "Merge commit" for cleaner history

**After merging:**
```bash
# Delete local branch
git branch -d feature/your-feature

# Delete remote branch
git push origin --delete feature/your-feature

# Update local master
git checkout master
git pull origin master
```

## Testing Strategy

### Test Pyramid

```
         E2E Tests (10%)
        /              \
       /                \
    Integration Tests (30%)
   /                      \
  /                        \
Unit Tests (60%)
```

### Test Types

#### 1. Unit Tests

**Purpose:** Test individual functions and classes in isolation

**Location:** `tests/` directory, named after modules

**Examples:**
- `test_models.py` - Test model validations
- `test_repositories.py` - Test data access
- `test_services.py` - Test business logic

**Example:**
```python
def test_satellite_creation():
    satellite = Satellite(
        name="Sentinel-2",
        provider="ESA",
        status="active"
    )
    assert satellite.name == "Sentinel-2"
    assert satellite.status == "active"
```

#### 2. Integration Tests

**Purpose:** Test interaction between components

**Location:** `tests/` directory

**Examples:**
- `test_api.py` - Test API endpoints
- `test_internal_api.py` - Test internal API
- `test_auth.py` - Test authentication flow

**Example:**
```python
def test_create_satellite_via_api(client):
    response = client.post(
        "/api/satellites",
        json={"name": "Sentinel-2", "provider": "ESA"},
        headers={"X-API-Key": "secret-intern-4a-key"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Sentinel-2"
```

#### 3. End-to-End Tests

**Purpose:** Test complete user workflows

**Location:** `tests/e2e/` (if implemented)

**Examples:**
- Complete satellite ingestion workflow
- Full diagnosis pipeline
- User registration and data access

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_create_satellite

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "satellite"
```

### Test Configuration

Test configuration is in `tests/conftest.py`:
- Isolated test database (`agritwin_test`)
- Mocked MinIO storage
- Test client with dependency overrides
- Transaction rollback for isolation

### Writing Tests

**Guidelines:**
- Test one thing per test
- Use descriptive test names
- Arrange-Act-Assert pattern
- Mock external dependencies
- Clean up after tests

**Example:**
```python
def test_get_satellite_by_id(db_session):
    # Arrange
    satellite = Satellite(name="Sentinel-2", provider="ESA")
    db_session.add(satellite)
    db_session.commit()

    # Act
    repo = SatelliteRepository(db_session)
    result = repo.get(satellite.id)

    # Assert
    assert result is not None
    assert result.name == "Sentinel-2"
```

## Database Changes

### Migration Workflow

#### 1. Modify Models

```python
# app/models/satellite.py
class Satellite(Base):
    __tablename__ = "satellites"
    # ... add new fields ...
    launch_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
```

#### 2. Generate Migration

```bash
alembic revision --autogenerate -m "add launch_date to satellites"
```

#### 3. Review Migration

```python
# migrations/versions/abc123_add_launch_date_to_satellites.py
def upgrade():
    op.add_column('satellites', sa.Column('launch_date', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('satellites', 'launch_date')
```

#### 4. Test Migration

```bash
# Test on local database
alembic upgrade head

# Verify schema
alembic downgrade -1
alembic upgrade head
```

#### 5. Commit with Model Changes

```bash
git add app/models/satellite.py migrations/versions/abc123_add_launch_date_to_satellites.py
git commit -m "feat(satellites): add launch_date field"
```

### Migration Best Practices

- **Always review auto-generated migrations** - They may include unintended changes
- **Write reversible migrations** - Ensure `downgrade()` works
- **Use descriptive migration names** - `add_field_to_table` format
- **Test migrations on copy of production data** - For breaking changes
- **Never modify committed migrations** - Create new migration instead
- **Use batch operations for large datasets** - Avoid timeouts

### Data Migrations

For data changes (not schema):

```python
def upgrade():
    # Populate default values
    connection = op.get_bind()
    connection.execute(
        "UPDATE satellites SET launch_date = '2020-01-01' WHERE launch_date IS NULL"
    )

def downgrade():
    connection = op.get_bind()
    connection.execute(
        "UPDATE satellites SET launch_date = NULL WHERE launch_date = '2020-01-01'"
    )
```

## Deployment Process

### Environment Strategy

**Environments:**
1. **Development** - Local developer machines
2. **Staging** - Pre-production testing environment
3. **Production** - Live production environment

### Deployment Workflow

#### 1. Development Deployment

```bash
# Local development
docker compose up -d

# Apply migrations
docker compose exec web alembic upgrade head

# Verify
curl http://localhost:8000/
```

#### 2. Staging Deployment

**Automated via CI/CD:**

```yaml
# .github/workflows/deploy-staging.yml
on:
  push:
    branches: [master]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to staging
        run: |
          # Build and push to staging registry
          # Apply migrations
          # Restart services
```

**Manual staging deployment:**
```bash
# SSH to staging server
ssh staging-server

# Pull latest code
cd /app/agritwin
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
alembic upgrade head

# Restart application
sudo systemctl restart agritwin
```

#### 3. Production Deployment

**Production checklist:**
- [ ] All tests pass
- [ ] Code reviewed and approved
- [ ] Staging environment tested
- [ ] Database migrations tested
- [ ] Backup created (for breaking changes)
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Team notified

**Production deployment steps:**

```bash
# Create backup (for breaking changes)
pg_dump agritwin > backup_$(date +%Y%m%d_%H%M%S).sql

# SSH to production server
ssh production-server

# Deploy to production
cd /app/agritwin
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart agritwin

# Verify deployment
curl https://api.agritwin.com/health
```

**Rollback procedure:**
```bash
# Rollback code
git revert <commit-hash>
git push origin master

# Rollback migrations if needed
alembic downgrade -1

# Restart services
sudo systemctl restart agritwin
```

### Blue-Green Deployment (Advanced)

For zero-downtime deployments:

```
        Load Balancer
            │
      ┌─────┴─────┐
      │           │
   Blue (v1)  Green (v2)
      │           │
      └─────┬─────┘
            │
      Production DB
```

**Process:**
1. Deploy new version to Green environment
2. Run smoke tests on Green
3. Switch load balancer to Green
4. Monitor for issues
5. Keep Blue for rollback

## Environment Management

### Local Development

**Required:**
- Python 3.11+
- PostgreSQL 15 with PostGIS
- Docker and Docker Compose (optional)

**Setup:**
```bash
# Clone repository
git clone https://github.com/Bodeayman/AgritwinBackbone.git
cd AgriTwin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start database
docker compose up -d db

# Run migrations
alembic upgrade head

# Start application
uvicorn app.main:app --reload
```

### Environment Variables

**Never commit `.env` file.** Use `.env.example` as template.

**Required variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing secret
- `MINIO_*` - MinIO configuration
- `INTERN_*_API_KEY` - Internal API keys

**Local development:**
```bash
# Use .env file locally
cp .env.example .env
# Edit with local settings
```

**Production:**
- Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Or environment variables in deployment config
- Never hardcode secrets in code

### Configuration Management

**Development:**
- Use `.env` file
- Default values in `app/core/config.py`

**Staging/Production:**
- Use environment variables
- Inject via CI/CD or orchestration platform
- Different values per environment

## Collaboration Guidelines

### Communication

**Channels:**
- **GitHub Issues** - Bug reports, feature requests
- **Pull Requests** - Code review discussions
- **Team Chat** (Slack/Discord) - Quick questions, sync
- **Documentation** - Decisions, architecture

### Issue Tracking

**Issue template:**
```markdown
## Description
Clear description of the issue or feature request.

## Steps to Reproduce (for bugs)
1. Go to ...
2. Click on ...
3. See error ...

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g. Windows 10]
- Python version: [e.g. 3.11]
- Database version: [e.g. PostgreSQL 15]

## Additional Context
Screenshots, logs, or other relevant information.
```

### Code of Conduct

**Be respectful:**
- Treat others with respect and professionalism
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

**Collaborate:**
- Share knowledge and document decisions
- Review code promptly
- Ask for help when needed
- Celebrate successes

### Onboarding New Developers

**Setup checklist:**
- [ ] Grant GitHub repository access
- [ ] Grant database access (if needed)
- [ ] Share `.env` template (not actual secrets)
- [ ] Review README.md
- [ ] Review DEVELOPMENT_WORKFLOW.md
- [ ] Set up local development environment
- [ ] Run tests locally
- [ ] Join team communication channels
- [ ] Assign first small task

**First week:**
- Day 1: Setup environment, run tests
- Day 2: Review codebase, ask questions
- Day 3: Make first small bug fix
- Day 4: Create first feature branch
- Day 5: Submit first pull request

## Troubleshooting

### Common Issues

**Merge conflicts:**
```bash
# Fetch latest master
git fetch origin master

# Rebase your branch
git rebase origin/master

# Resolve conflicts in editor
# git add resolved files
git rebase --continue

# Force push (careful!)
git push origin feature/branch --force-with-lease
```

**Migration conflicts:**
```bash
# If two developers create migrations simultaneously
# Resolve by creating new migration

# Revert conflicting migration
alembic downgrade -1

# Pull latest migrations
git pull origin master

# Create new migration that resolves conflict
alembic revision -m "merge migration conflict"
```

**Test failures:**
```bash
# Run with verbose output
pytest -v

# Run specific failing test
pytest tests/test_api.py::test_specific_function

# Run in debugger
pytest --pdb
```

## Resources

**Documentation:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

**Tools:**
- [GitHub Documentation](https://docs.github.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

**Best Practices:**
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Code Style (PEP 8)](https://peps.python.org/pep-0008/)
- [Twelve-Factor App](https://12factor.net/)
