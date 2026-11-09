import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


class ProviderUnavailable(Exception):
    pass


@dataclass(frozen=True)
class ProviderPolicy:
    timeout_seconds: float = 2.0
    attempts: int = 2
    retry_delay_seconds: float = 0.02
    min_interval_seconds: float = 0.01
    breaker_failures: int = 3
    recovery_seconds: float = 30.0


class ProviderRunner:
    """Per-adapter bounded calls, rate limit and circuit state; no error payload logging."""

    def __init__(self, policy: ProviderPolicy | None = None) -> None:
        self.policy = policy or ProviderPolicy()
        self.failures = 0
        self.open_until = 0.0
        self.last_call = 0.0

    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        if time.monotonic() < self.open_until:
            raise ProviderUnavailable("circuit_open")
        for attempt in range(self.policy.attempts):
            delay = self.policy.min_interval_seconds - (time.monotonic() - self.last_call)
            if delay > 0:
                await asyncio.sleep(delay)
            self.last_call = time.monotonic()
            try:
                value = await asyncio.wait_for(operation(), self.policy.timeout_seconds)
                self.failures = 0
                return value
            except (TimeoutError, ConnectionError, OSError) as exc:
                self.failures += 1
                if self.failures >= self.policy.breaker_failures:
                    self.open_until = time.monotonic() + self.policy.recovery_seconds
                    raise ProviderUnavailable("circuit_open") from exc
                if attempt + 1 == self.policy.attempts:
                    raise ProviderUnavailable("retry_exhausted") from exc
                await asyncio.sleep(self.policy.retry_delay_seconds * 2**attempt)
        raise ProviderUnavailable("invalid_policy")
