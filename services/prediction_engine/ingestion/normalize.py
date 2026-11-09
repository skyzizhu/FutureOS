"""Deterministic content/URL rules. No HTTP, persistence or model calls."""

import re
import unicodedata
from hashlib import sha256
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def canonical_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError("SOURCE_URL_INVALID")
    host = parsed.hostname.lower().encode("idna").decode()
    if ":" in host:
        host = f"[{host}]"
    port = parsed.port
    if port and (parsed.scheme, port) not in {("https", 443), ("http", 80)}:
        host += f":{port}"
    query = sorted(
        (
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}
        ),
        key=lambda pair: pair[0],
    )
    return urlunsplit((parsed.scheme, host, parsed.path or "/", urlencode(query), ""))


def content_hash(content: str) -> str:
    return sha256(content.encode()).hexdigest()


def normalized_text(content: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", content).casefold()).strip()


def likely_reprint(left: str, right: str) -> bool:
    a, b = normalized_text(left), normalized_text(right)
    if not a or not b:
        return False
    if a == b:
        return True
    if min(len(a), len(b)) < 100:
        return False
    x = {a[i : i + 5] for i in range(len(a) - 4)}
    y = {b[i : i + 5] for i in range(len(b) - 4)}
    return len(x & y) / len(x | y) >= 0.85
