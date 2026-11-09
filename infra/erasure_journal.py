"""Signed, fsynced tombstones kept outside database backups; no email/profile content."""

import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID

from infra.privacy import PrivacyVault


def append_tombstone(key_path: str, user_id: UUID, erasure_id: UUID, erased_at: str) -> None:
    vault = PrivacyVault(key_path)
    path = Path(key_path).parent / "erasure-journal.jsonl"
    body = {"user_id": str(user_id), "erasure_id": str(erasure_id), "erased_at": erased_at}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    signature = hmac.new(vault.key, b"erasure-v1:" + canonical, hashlib.sha256).hexdigest()
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        if path.stat().st_mode & 0o777 != 0o600:
            raise ValueError("ERASURE_JOURNAL_PERMISSIONS")
        stream.write(json.dumps({"body": body, "signature": signature}) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def read_tombstones(key_path: str) -> list[dict[str, Any]]:
    path = Path(key_path).parent / "erasure-journal.jsonl"
    if not path.exists():
        return []
    vault = PrivacyVault(key_path)
    rows = []
    for line in path.read_text().splitlines():
        entry = json.loads(line)
        canonical = json.dumps(entry["body"], sort_keys=True, separators=(",", ":")).encode()
        expected = hmac.new(vault.key, b"erasure-v1:" + canonical, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, entry["signature"]):
            raise ValueError("ERASURE_JOURNAL_TAMPERED")
        rows.append(entry["body"])
    return rows
