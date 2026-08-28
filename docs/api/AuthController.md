# Auth Controller

## Overview

The Auth controller handles user authentication and registration endpoints. It provides public endpoints for user registration and login, and generates JWT tokens for authenticated access to farmer-facing API endpoints.

## File Location

`app/api/v1/auth.py`

## Endpoints

### POST /api/v1/auth/register

Registers a new user account.

**Authentication:** None (public endpoint)

**Request Body:**
```json
{
  "email": "farmer@example.com",
  "password": "secure_password"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "farmer@example.com",
  "is_active": true,
  "role": "user"
}
```

**Error Responses:**
- **409 Conflict** - Email already registered
- **422 Unprocessable Entity** - Invalid input data

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@example.com","password":"secure_password"}'
```

---

### POST /api/v1/auth/login

Authenticates a user and returns a JWT access token.

**Authentication:** None (public endpoint)

**Request Body:**
```json
{
  "email": "farmer@example.com",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- **401 Unauthorized** - Invalid credentials
- **422 Unprocessable Entity** - Invalid input data

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@example.com","password":"secure_password"}'
```

---

## Using the Token

Once you have the access token, include it in the Authorization header for authenticated requests:

```bash
curl -X GET http://localhost:8000/api/v1/farms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Token Expiration

- Default expiration: 7 days (10080 minutes)
- Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable
- Token contains user ID in the `sub` claim

## Related Services

- `AuthService` - Handles user registration and authentication
- `get_password_hash()` - Password hashing
- `verify_password()` - Password verification
- `create_access_token()` - JWT token generation

## Security Notes

- Passwords are hashed using pbkdf2_sha256 before storage
- Never store plain text passwords
- Email addresses must be unique
- Use HTTPS in production to protect tokens
- Tokens should be stored securely on client side

## Schemas

### UserRegister
```python
class UserRegister(BaseModel):
    email: str
    password: str
```

### UserLogin
```python
class UserLogin(BaseModel):
    email: str
    password: str
```

### Token
```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

## Notes

- Registration endpoint is public (no authentication required)
- Login endpoint is public (no authentication required)
- All other `/api/v1/` endpoints require JWT authentication
- Token should be included in `Authorization: Bearer <token>` header
