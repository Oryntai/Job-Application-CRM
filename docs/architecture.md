# Architecture

## Apps
- `accounts`: profile + notification preferences + timezone.
- `companies`: `Company`, `Contact`.
- `applications`: `JobApplication`, `Tag`, `ApplicationTag`, `StatusHistory`, `Attachment`.
- `pipeline`: `EventType`, `ApplicationEvent`, event recording service.
- `reminders`: `Reminder`, `NotificationLog`, scheduling service, Celery tasks.
- `analytics`: selectors for funnel, conversion, time-in-stage, source stats.
- `api`: unified `/api/v1` endpoints and analytics API.
- `core`: settings, celery app, logging, base models, pagination, permissions.

## Data Ownership
Every business entity includes `owner` and all read/write paths scope by `request.user`.

## Domain Flows
1. Create `JobApplication`.
2. Status updates via `applications.services.change_status` with audit log in one transaction.
3. Record timeline events via `pipeline.services.record_event`; status can auto-advance.
4. Schedule follow-ups via `reminders.services.schedule_followup`; updates `next_action_at/text`.
5. Celery beat runs:
   - `reminders.tasks.send_due_reminders`
   - `reminders.tasks.daily_digest`

## Async
- Broker/result backend: Redis.
- Worker: `celery -A core worker`
- Beat: `celery -A core beat`

## Observability
- JSON logs via `python-json-logger`.
- Sentry placeholder via `SENTRY_DSN`.
