import asyncio
from unittest.mock import MagicMock, patch

import pytest
from prediction_engine.contracts.providers import EmailProvider

from infra.providers.mail import SMTPMailProvider
from infra.settings import Settings

PAYLOAD = {
    "subject": "Private report update",
    "summary": "Log in to see your report",
    "link": "https://example.invalid/reports/private",
    "unsubscribe_link": "https://example.invalid/unsubscribe?token=synthetic",
}


def test_demo_never_connects_to_smtp():
    config = Settings(_env_file=None)
    provider: EmailProvider = SMTPMailProvider(config)
    with patch("infra.providers.mail.smtplib.SMTP") as smtp:
        with pytest.raises(ValueError, match="EXTERNAL_EMAIL_DISABLED"):
            asyncio.run(
                provider.send("private-report-v1", "test@example.invalid", PAYLOAD, "test-key")
            )
        smtp.assert_not_called()


def test_explicit_smtp_adapter_uses_tls_and_stable_message_id_without_network():
    config = Settings(_env_file=None).model_copy(
        update={"demo_mode": False, "live_email_enabled": True, "smtp_host": "smtp.example.invalid"}
    )
    provider: EmailProvider = SMTPMailProvider(config)
    fake = MagicMock()
    with patch("infra.providers.mail.smtplib.SMTP", return_value=fake):
        first = asyncio.run(
            provider.send("private-report-v1", "test@example.invalid", PAYLOAD, "test-key")
        )
        second = asyncio.run(
            provider.send("private-report-v1", "test@example.invalid", PAYLOAD, "test-key")
        )
    assert first == second
    fake.__enter__.return_value.starttls.assert_called()
    sent = fake.__enter__.return_value.send_message.call_args.args[0]
    assert sent["To"] == "test@example.invalid" and "unsubscribe" in sent.get_content()
