from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    demo_mode: bool = True
    app_env: str = "development"
    database_url: str = "sqlite:///.local/futureos-demo.db"
    redis_url: str = "redis://127.0.0.1:6379/0"
    require_redis: bool = False
    demo_user_token: str = "demo-user-local-only"
    demo_admin_token: str = "demo-admin-local-only"
    demo_other_token: str = "demo-other-local-only"
    deepseek_api_key: SecretStr | None = None
    live_web_enabled: bool = False
    live_research_enabled: bool = False
    live_chat_enabled: bool = False
    chat_model_global_window_limit: int = Field(default=60, ge=1, le=10000)
    chat_model_global_inflight_limit: int = Field(default=8, ge=1, le=128)
    deepseek_research_model: str = "deepseek-flash"
    profile_key_path: str = ".local/private-profile.key"
    session_hours: int = 168
    auth_window_seconds: int = Field(default=900, ge=60, le=3600)
    auth_identity_attempts: int = Field(default=10, ge=1, le=100)
    auth_source_attempts: int = Field(default=30, ge=1, le=1000)
    auth_device_attempts: int = Field(default=20, ge=1, le=1000)
    auth_email_global_daily_sends: int = Field(default=120, ge=1, le=10000)
    auth_access_retention_days: int = Field(default=30, ge=1, le=90)
    auth_global_attempts: int = Field(default=60, ge=1, le=10000)
    demo_admin_enabled: bool = False
    admin_session_minutes: int = Field(default=30, ge=5, le=60)
    auth_mail_transport: Literal["local_preview", "smtp", "disabled"] = "local_preview"
    turnstile_enabled: bool = False
    turnstile_site_key: str = ""
    turnstile_secret_key: SecretStr | None = None
    turnstile_hostnames: tuple[str, ...] = ("localhost", "127.0.0.1")
    fetch_allowed_hosts: tuple[str, ...] = (
        "github.com",
        "api.github.com",
        "raw.githubusercontent.com",
        "api-docs.deepseek.com",
        "www.anthropic.com",
        "support.google.com",
        "docs.python.org",
    )
    queue_alert_seconds: int = 600
    queue_max_pending_per_user: int = 20
    export_max_bytes: int = 10000000
    sandbox_commerce_enabled: bool = False
    live_payments_enabled: bool = False
    billing_plans_path: str = "infra/billing_plans.json"
    scheduler_enabled: bool = True
    scheduler_tick_seconds: int = 30
    live_email_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from: str = "futureos@example.invalid"
    bounce_webhook_secret: SecretStr | None = None
    job_lease_seconds: int = 60
    job_max_attempts: int = 3

    @model_validator(mode="after")
    def isolation(self) -> "Settings":
        if not self.demo_mode or self.app_env not in {"development", "test"}:
            raise ValueError(
                "Local development only; production deployment has not passed release gates"
            )
        if self.live_email_enabled:
            raise ValueError("Live email transport has not passed production release gates")
        if self.turnstile_enabled and (
            not self.turnstile_site_key
            or not self.turnstile_secret_key
            or not self.turnstile_hostnames
        ):
            raise ValueError("Turnstile requires site key, secret and explicit hostname allowlist")
        if self.auth_mail_transport == "smtp" and not all(
            [self.smtp_host, self.smtp_username, self.smtp_password, self.smtp_from]
        ):
            raise ValueError("Authentication email requires configured TLS SMTP credentials")
        if self.live_payments_enabled:
            raise ValueError("Live payment provider is not implemented or approved")
        tokens = [self.demo_user_token, self.demo_admin_token, self.demo_other_token]
        if len(set(tokens)) != 3 or any(len(t) < 16 for t in tokens):
            raise ValueError("distinct local demo tokens of at least 16 characters required")
        if not 1 <= self.session_hours <= 720:
            raise ValueError("session_hours must be between 1 and 720")
        if self.job_lease_seconds < 5 or self.job_max_attempts < 1:
            raise ValueError("invalid worker policy")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
