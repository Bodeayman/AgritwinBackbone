# User Model

## Overview

The `User` model represents farmer accounts in the AgriTwin system. It handles authentication and authorization for farmers accessing the API.

## File Location

`app/models/user.py`

## Table Schema

**Table Name:** `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt-hashed password |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status flag |
| `role` | VARCHAR(50) | DEFAULT 'user' | User role for authorization |

## Relationships

- **Owning:** `Farm` entities (one-to-many via `Farm.owner_id`)
- **Referenced by:** Authentication service and JWT token generation

## Cascade Behavior

- When a User is deleted, all associated Farms are deleted (CASCADE)

## Usage Examples

### Creating a User

```python
from app.models.user import User
from app.core.security import get_password_hash

user = User(
    email="farmer@example.com",
    hashed_password=get_password_hash("secure_password"),
    is_active=True,
    role="user"
)
```

### Authenticating a User

```python
from app.core.security import verify_password

# Verify password
if verify_password(plain_password, user.hashed_password):
    # Password is correct
    pass
```

## Security Notes

- **Never store plain text passwords** - Always use `get_password_hash()` from `app.core.security`
- **Use bcrypt** - Passwords are hashed using pbkdf2_sha256 algorithm
- **Unique emails** - Email addresses must be unique across the system
- **Role-based access** - The `role` field can be extended for RBAC (currently: 'user', 'admin')

## Related Services

- `AuthService` - Handles user registration and authentication
- `get_current_user` dependency - Validates JWT tokens and returns User

## Related API Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and receive JWT token
