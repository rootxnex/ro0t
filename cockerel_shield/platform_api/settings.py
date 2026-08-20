from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_webhook_secret: str
    database_url: str
    redis_url: str
    public_base_url: str
    github_app_id: str = ""
    github_app_private_key: str = ""

    @classmethod
    def from_environment(cls) -> "Settings":
        values = {
            "github_webhook_secret": os.environ.get("GITHUB_WEBHOOK_SECRET", ""),
            "database_url": os.environ.get("DATABASE_URL", ""),
            "redis_url": os.environ.get("REDIS_URL", ""),
            "public_base_url": os.environ.get("PUBLIC_BASE_URL", "").rstrip("/"),
            "github_app_id": os.environ.get("GITHUB_APP_ID", ""),
            "github_app_private_key": os.environ.get("GITHUB_APP_PRIVATE_KEY", "").replace("\\n", "\n"),
        }
        missing = [name.upper() for name, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"missing required configuration: {', '.join(missing)}")
        return cls(**values)
