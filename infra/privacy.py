"""Local encryption key stays outside DB; AES-GCM binds ciphertext to entity/user context."""

import base64
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class PrivacyVault:
    def __init__(self, path: str, create: bool = False) -> None:
        target = Path(path)
        if not target.exists() and not create:
            raise ValueError("PRIVATE_KEY_MISSING_RESTORE_BACKUP")
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(target, os.O_RDWR | (os.O_CREAT if create else 0), 0o600)
        with os.fdopen(descriptor, "r+b") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            key = stream.read()
            if not key and create:
                key = AESGCM.generate_key(bit_length=256)
                stream.write(key)
                stream.flush()
                os.fsync(stream.fileno())
            if len(key) != 32 or target.stat().st_mode & 0o777 != 0o600:
                raise ValueError("PRIVATE_KEY_INVALID_OR_PERMISSIONS")
        self.key = key
        self.cipher = AESGCM(key)

    def lookup(self, email: str) -> str:
        return hmac.new(self.key, b"email-lookup-v1:" + email.encode(), hashlib.sha256).hexdigest()

    def seal(self, data: dict[str, Any], context: str) -> str:
        nonce = os.urandom(12)
        payload = json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        return base64.urlsafe_b64encode(
            nonce + self.cipher.encrypt(nonce, payload, context.encode())
        ).decode()

    def open(self, ciphertext: str, context: str) -> dict[str, Any]:
        raw = base64.urlsafe_b64decode(ciphertext.encode())
        payload = json.loads(self.cipher.decrypt(raw[:12], raw[12:], context.encode()))
        if not isinstance(payload, dict):
            raise ValueError("PRIVATE_PAYLOAD_INVALID")
        return payload
