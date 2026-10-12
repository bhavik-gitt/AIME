from __future__ import annotations

from datetime import datetime


def iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    return dt.isoformat()


def ok(data=None, **kwargs):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    payload.update(kwargs)
    return payload
