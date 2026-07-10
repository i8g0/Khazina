# Khazina API Contracts

This document defines the API standards for all Khazina REST endpoints. These conventions apply to current and future endpoints under `/api/v1/`.

For implementation details, see [ARCHITECTURE.md](ARCHITECTURE.md). For the architectural decision behind the response envelope, see [ADR 005: ApiResponse Standard](ADR/005-api-response.md).

No endpoints are listed here. This document describes standards only.

---

## API Versioning

All API endpoints are versioned under `/api/v1/`.

| Rule | Detail |
|------|--------|
| Prefix | `/api/v1` |
| Router | `app/api/v1/router.py` aggregates version-specific routes |
| Breaking changes | Require a new version (e.g., `/api/v2/`) |
| Current endpoints | `GET /api/v1/health` |

New endpoints must be added to the appropriate version router, never directly to the application root.

---

## ApiResponse Structure

Every endpoint returns the `ApiResponse` generic envelope:

```json
{
  "success": true,
  "message": "Service is healthy",
  "data": { "status": "ok" },
  "errors": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation succeeded |
| `message` | string | Human-readable summary |
| `data` | T or null | Response payload on success |
| `errors` | list of strings or null | Error details when `success` is false |

Helpers in `backend/app/schemas/response.py`:

- `success_response(data, message)` — success envelope
- `error_response(message, errors)` — error envelope

All new endpoints must return `ApiResponse` unless Tech Lead approves an exception.

---

## HTTP Status Conventions

| Status | Usage |
|--------|-------|
| `200 OK` | Successful read or update operations |
| `201 Created` | Resource successfully created |
| `204 No Content` | Successful delete with no response body (rare; prefer `200` with `ApiResponse` when a message is needed) |
| `400 Bad Request` | Client error, business rule violation (`AppError` default) |
| `401 Unauthorized` | Authentication required (Phase 4) |
| `403 Forbidden` | Authenticated but not permitted (Phase 4) |
| `404 Not Found` | Resource or route not found |
| `422 Unprocessable Entity` | Request validation failure |
| `500 Internal Server Error` | Unhandled server error |

The HTTP status code reflects the outcome category. The response body always uses the `ApiResponse` envelope regardless of status.

---

## Pagination Conventions

List endpoints will use cursor- or offset-based pagination inside the `data` field. Standard shape (future):

```json
{
  "success": true,
  "message": "Records retrieved",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 100,
      "total_pages": 5
    }
  },
  "errors": null
}
```

Query parameters (future):

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | `1` | Page number (1-based) |
| `page_size` | integer | `20` | Items per page (max enforced by backend) |

Exact pagination implementation will be finalized when the first list endpoint is introduced in a future phase.

---

## Filtering

Filter parameters use snake_case query parameters matching resource field names:

```
GET /api/v1/resources?status=active&category=report
```

Rules:

- Only documented filter fields are accepted
- Unknown filter parameters are ignored or rejected with `422` (decision at endpoint implementation)
- Date ranges use ISO 8601 format: `created_after=2026-01-01T00:00:00Z`

---

## Sorting

Sort parameters (future):

```
GET /api/v1/resources?sort_by=created_at&sort_order=desc
```

| Parameter | Values | Default |
|-----------|--------|---------|
| `sort_by` | Allowed field name | Resource-specific default |
| `sort_order` | `asc`, `desc` | `asc` |

Only whitelisted sort fields are permitted to prevent SQL injection through sort clauses.

---

## Authentication Header (Reserved for Phase 4)

Authentication is not implemented in Phase 1 or Phase 2. The following convention is reserved for Phase 4:

```
Authorization: Bearer <token>
```

Until Phase 4:

- No authentication middleware is active
- Endpoints are publicly accessible in local development
- Error responses for missing auth will follow the standard `ApiResponse` envelope with HTTP `401`

---

## Error Response Format

All errors use the `ApiResponse` envelope with `success: false`:

```json
{
  "success": false,
  "message": "Resource not found",
  "data": null,
  "errors": ["No record with id 42"]
}
```

| Exception Type | HTTP Status | Handler |
|----------------|-------------|---------|
| `AppError` | Custom (default 400) | Global exception handler |
| `HTTPException` | As raised | Global exception handler |
| `RequestValidationError` | 422 | Global exception handler |
| Unhandled `Exception` | 500 | Global exception handler |

Internal exception details are suppressed in production (`debug=false`).

---

## Validation Response Format

Pydantic validation errors return HTTP `422` with field-level details in `errors`:

```json
{
  "success": false,
  "message": "Validation error",
  "data": null,
  "errors": [
    "body.email: value is not a valid email address",
    "body.amount: Input should be greater than 0"
  ]
}
```

Field paths use dot notation prefixed with the request location (`body`, `query`, `path`).

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| URL path segments | kebab-case, plural nouns for collections | `/api/v1/financial-reports` |
| Query parameters | snake_case | `?page_size=20&sort_by=created_at` |
| JSON request/response fields | snake_case | `"created_at"`, `"total_amount"` |
| Route handler functions | snake_case | `get_financial_report` |
| Pydantic models | PascalCase | `FinancialReportCreate` |
| Resource IDs in paths | `{resource_id}` | `/api/v1/reports/{report_id}` |

HTTP methods:

| Method | Usage |
|--------|-------|
| `GET` | Read single resource or list |
| `POST` | Create resource |
| `PUT` | Full replace of resource |
| `PATCH` | Partial update of resource |
| `DELETE` | Remove resource |

---

## Related Documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — API versioning, error handling, response standard
- [ADR/005-api-response.md](ADR/005-api-response.md) — ApiResponse architectural decision
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development workflow and validation
