"""Message model + inbox loading (stdlib only)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Message:
    """A single inbox message. `meta` may carry headers like List-Unsubscribe."""
    id: str
    sender: str = ""
    subject: str = ""
    body: str = ""
    date: str = ""          # ISO date string, optional
    meta: dict = field(default_factory=dict)

    def text_blob(self) -> str:
        """Lowercased subject+body+sender used by the classifier."""
        return f"{self.subject}\n{self.body}\n{self.sender}".lower()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "date": self.date,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Message":
        """Tolerant constructor: malformed rows never crash the run."""
        if not isinstance(raw, dict):
            raw = {}
        meta = raw.get("meta")
        return cls(
            id=str(raw.get("id") or f"msg-{abs(hash(json.dumps(raw, sort_keys=True, default=str))) % 10_000_000}"),
            sender=str(raw.get("sender") or raw.get("from") or ""),
            subject=str(raw.get("subject") or ""),
            body=str(raw.get("body") or raw.get("snippet") or ""),
            date=str(raw.get("date") or ""),
            meta=meta if isinstance(meta, dict) else {},
        )


def load_inbox(path: str | Path) -> list[Message]:
    """Load a JSON inbox: a list of message dicts, or {"messages": [...]}."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("messages"), list):
        rows = data["messages"]
    elif isinstance(data, list):
        rows = data
    else:
        raise ValueError("inbox JSON must be a list or an object with a 'messages' list")
    return [Message.from_dict(r) for r in rows]


def utcnow_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
