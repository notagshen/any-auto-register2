from __future__ import annotations

from typing import Optional
from urllib.parse import unquote, urlsplit, urlunsplit


def normalize_proxy_url(proxy_url: Optional[str]) -> Optional[str]:
    """规范化代理 URL。"""
    if proxy_url is None:
        return None

    value = str(proxy_url).strip()
    if not value:
        return None

    parts = urlsplit(value)
    normalized_parts = parts
    changed = False

    # 兼容 http://:@host:port 这类空账号密码写法，避免底层客户端把它当成异常代理。
    if parts.username == "" and parts.password == "" and "@" in parts.netloc:
        normalized_parts = normalized_parts._replace(netloc=parts.netloc.split("@", 1)[1])
        changed = True

    if (normalized_parts.scheme or "").lower() == "socks5":
        normalized_parts = normalized_parts._replace(scheme="socks5h")
        changed = True

    if changed:
        return urlunsplit(normalized_parts)
    return value


def build_requests_proxy_config(proxy_url: Optional[str]) -> Optional[dict[str, str]]:
    normalized = normalize_proxy_url(proxy_url)
    if not normalized:
        return None
    return {"http": normalized, "https": normalized}


def build_playwright_proxy_config(proxy_url: Optional[str]) -> Optional[dict[str, str]]:
    normalized = normalize_proxy_url(proxy_url)
    if not normalized:
        return None

    parts = urlsplit(normalized)
    if not parts.scheme or not parts.hostname or parts.port is None:
        return {"server": normalized}

    config = {"server": f"{parts.scheme}://{parts.hostname}:{parts.port}"}
    if parts.username:
        config["username"] = unquote(parts.username)
    if parts.password:
        config["password"] = unquote(parts.password)
    return config
