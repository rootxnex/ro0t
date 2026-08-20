# Cocokerel Platform API

This service receives signed GitHub webhooks, persists delivery IDs in
PostgreSQL, and queues eligible pull-request scans through Celery/Redis.

Required environment variables:

```text
GITHUB_WEBHOOK_SECRET
DATABASE_URL
REDIS_URL
PUBLIC_BASE_URL
```

Initialize PostgreSQL with `schema.sql`, install `requirements.txt`, then run:

```bash
uvicorn platform_api.app:app --host 0.0.0.0 --port 8000
```

Configure the GitHub App webhook URL as:

```text
https://your-api-host.example/api/webhooks/github
```

The service intentionally disables interactive API documentation in production
and returns no internal exception details to webhook callers.
