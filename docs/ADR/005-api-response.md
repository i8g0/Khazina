# ADR 005: Standardized ApiResponse Envelope

**Status:** Accepted  
**Date:** Phase 1 — Sprint 1.3  
**Phase:** Foundation

## Decision

Every Khazina API endpoint returns responses wrapped in the `ApiResponse` generic envelope defined in `backend/app/schemas/response.py`.

## Why Every Endpoint Uses ApiResponse

Phase 1 established a single response contract before any business endpoints were implemented. The health endpoint at `GET /api/v1/health` was refactored to use this standard in Sprint 1.3.

Structure:

```json
{
  "success": true,
  "message": "Service is healthy",
  "data": { "status": "ok" },
  "errors": null
}
```

## Benefits

| Benefit | Description |
|---------|-------------|
| Predictability | Clients always parse the same top-level fields |
| Error uniformity | Global exception handlers return the same error shape |
| Versioning | API v2 can evolve data payloads while preserving the envelope |
| Documentation | OpenAPI schemas consistently describe response structure |
| Frontend integration | A single client response handler can process all API calls |

## Future Compatibility

- Pagination metadata will be added inside `data` or as an extended wrapper in a future ADR
- Authentication error responses will use the same envelope with appropriate HTTP status codes
- Breaking changes to the envelope itself would require a new API version (`/api/v2/`)

Global exception handlers in `app/core/exception_handlers.py` enforce this standard for `AppError`, `HTTPException`, validation errors, and unhandled exceptions.

**Related Documents**

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [API_CONTRACTS.md](../API_CONTRACTS.md)
