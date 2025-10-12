# Authentication & Security

## JWT Authentication

**Algorithm**: HS256

**Token Expiration**: 60 minutes

**Protected Endpoints**:

- `GET /api/v1/communications`
- `GET /api/v1/devices/{device_id}/communications`

**Public Endpoints** (No auth required):

- `GET /health`
- `GET /api/v1/communications/stream`
- `GET /api/v1/devices/{device_id}/communications/stream`

## Authentication Flow

1. Client obtains JWT token (authentication endpoint not in scope of this API)
2. Client includes token in Authorization header: `Authorization: Bearer <token>`
3. API validates token signature and expiration
4. If valid, request proceeds; if invalid, return 401 Unauthorized

## Security Requirements

- JWT secret key must be stored securely in environment variables
- Tokens must be validated on every protected endpoint request
- Expired tokens must be rejected with appropriate error message
- Invalid tokens must be rejected with appropriate error message

## CORS Configuration

- Configurable via environment variable `ALLOWED_ORIGINS`
- Default: `*` (allow all origins)
- Production should restrict to specific domains
- Credentials allowed
- All HTTP methods allowed
- All headers allowed
