# AuthService

## Overview

The `AuthService` handles user authentication, registration, and JWT token generation. It manages user account creation, password hashing, and token-based authentication for farmer-facing API endpoints.

## File Location

`app/services/auth_service.py`

## Responsibilities

- User registration with email uniqueness validation
- Password hashing and verification
- JWT token generation and validation
- User authentication

## Methods

### `register_user(email: str, password: str) -> User`

Registers a new user account.

**Parameters:**
- `email` - User's email address (must be unique)
- `password` - Plain text password (will be hashed)

**Returns:** Created `User` object

**Raises:**
- `HTTPException` (409 Conflict) - If email already exists

**Example:**
```python
from app.services.auth_service import AuthService

service = AuthService(db)
user = service.register_user(
    email="farmer@example.com",
    password="secure_password"
)
```

### `authenticate_user(email: str, password: str) -> User | None`

Authenticates a user with email and password.

**Parameters:**
- `email` - User's email address
- `password` - Plain text password

**Returns:** `User` object if authentication successful, `None` otherwise

**Example:**
```python
user = service.authenticate_user(
    email="farmer@example.com",
    password="secure_password"
)
if user:
    # Authentication successful
    pass
```

### `create_access_token(user: User) -> str`

Generates a JWT access token for a user.

**Parameters:**
- `user` - User object to generate token for

**Returns:** JWT token string

**Example:**
```python
from app.core.security import create_access_token

token = create_access_token(data={"sub": str(user.id)})
```

## Dependencies

- `UserRepository` - Data access for User entities
- `get_password_hash()` - Password hashing from `app.core.security`
- `verify_password()` - Password verification from `app.core.security`
- `create_access_token()` - JWT generation from `app.core.security`

## Related API Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and receive JWT token

## Security Notes

- Passwords are hashed using pbkdf2_sha256
- Never store plain text passwords
- Email addresses must be unique
- JWT tokens expire after 7 days (configurable)
- Use HTTPS in production to protect tokens

## Error Handling

- **409 Conflict** - Email already registered
- **401 Unauthorized** - Invalid credentials
- **422 Validation Error** - Invalid input data

## Notes

- JWT tokens contain user ID in the `sub` claim
- Token expiration is configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`
- Active users can authenticate; inactive users cannot
