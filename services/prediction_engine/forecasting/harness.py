"""Small deterministic checks for untrusted text crossing Agent boundaries."""

import re
from unicodedata import normalize

_CREDENTIAL = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(?:-----END [A-Z ]*PRIVATE KEY-----|\Z)"
    r"|\b(?:sk-|ghp_|github_pat_|AKIA)[A-Za-z0-9_-]{16,}"
    r"|\bBearer\s+[A-Za-z0-9_.=-]{12,}"
    r"|\b(?:api[_ -]?key|password|access[_ -]?token|authorization)"
    r"\s*[:=]\s*[\w/+.-]{8,}",
    re.IGNORECASE,
)
_EMAIL = re.compile(r"\b[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_ACTIVE_CONTENT = re.compile(
    r"<\s*(?:script|iframe|object|embed|svg|img)\b|(?:javascript|data)\s*:",
    re.IGNORECASE,
)


def has_credential(text: str) -> bool:
    return bool(_CREDENTIAL.search(normalize("NFKC", text)))


def external_text(text: str) -> str:
    normalized = normalize("NFKC", text).encode("utf-8", "replace").decode()
    return _EMAIL.sub("[邮箱已隐藏]", _CREDENTIAL.sub("[凭据已隐藏]", normalized))


def unsafe_output(text: str) -> bool:
    return has_credential(text) or bool(_ACTIVE_CONTENT.search(normalize("NFKC", text)))


def public_search_term(text: str) -> bool:
    normalized = normalize("NFKC", text)
    return not (
        has_credential(normalized)
        or _EMAIL.search(normalized)
        or re.search(r"https?://|://|[<>\x00-\x1f\x7f]", normalized, re.IGNORECASE)
    )
