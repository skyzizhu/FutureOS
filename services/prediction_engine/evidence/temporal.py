from datetime import UTC, datetime


def utc(value: datetime) -> datetime:
    """SQLite stores naive UTC; external contracts still require aware datetimes."""
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def known_by(available_at: datetime | None, as_of: datetime) -> bool:
    return available_at is not None and utc(available_at) <= utc(as_of)
