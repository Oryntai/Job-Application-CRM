# API Examples

Base URL: `/api/v1/`

## JWT
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo12345"}'
```

## Applications CRUD
```bash
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/applications/
```

```bash
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "company": 1,
    "role_title": "Backend Engineer",
    "source": "LINKEDIN",
    "status": "APPLIED",
    "priority": "HIGH",
    "applied_date": "2026-02-10"
  }'
```

## Nested events
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/applications/1/events/
```

## Nested reminders
```bash
curl -X POST http://localhost:8000/api/v1/applications/1/reminders/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "remind_at": "2026-02-18T10:30:00Z",
    "channel": "EMAIL",
    "message": "Follow up with recruiter"
  }'
```

## Analytics
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  "http://localhost:8000/api/v1/analytics/funnel?from=2026-01-01&to=2026-02-16"
```

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/analytics/time-in-stage
```
