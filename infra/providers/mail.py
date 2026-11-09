"""SMTP implementation of the EmailProvider port; never selected by DEMO workers."""

import asyncio
import hashlib
import smtplib
import ssl
from email.message import EmailMessage

from infra.settings import Settings


class SMTPMailProvider:
    def __init__(self, config: Settings) -> None:
        self.config = config

    async def send(
        self, template_id: str, recipient: str, payload: dict[str, str], dedupe_key: str
    ) -> str:
        if template_id != "private-report-v1":
            raise ValueError("MAIL_TEMPLATE_UNSUPPORTED")
        return await asyncio.to_thread(self._send, recipient, payload, dedupe_key)

    def _send(self, recipient: str, payload: dict[str, str], dedupe_key: str) -> str:
        config = self.config
        if config.demo_mode or not config.live_email_enabled or not config.smtp_host:
            raise ValueError("EXTERNAL_EMAIL_DISABLED")
        identifier = hashlib.sha256(dedupe_key.encode()).hexdigest()
        message = EmailMessage()
        message["From"] = config.smtp_from
        message["To"] = recipient
        message["Subject"] = payload["subject"]
        message["Message-ID"] = "<" + identifier + "@futureos.local>"
        message.set_content(
            payload["summary"] + "\n" + payload["link"] + "\n退订：" + payload["unsubscribe_link"]
        )
        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=20) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            if config.smtp_username and config.smtp_password:
                smtp.login(config.smtp_username, config.smtp_password.get_secret_value())
            smtp.send_message(message)
        return identifier
