# Auth Service

Authentication and Authorization microservice using Google OAuth and JWT tokens.

## Features

- Google OAuth 2.0 integration
- JWT access and refresh tokens
- User management
- Token refresh and revocation
- PostgreSQL with async SQLAlchemy

## API Endpoints

- `POST /auth/google/callback` - Google OAuth callback
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout and revoke token
- `GET /health` - Health check

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
# Build image
docker build -t auth-service .

# Run container
docker run -p 8000:8000 --env-file .env auth-service
```
