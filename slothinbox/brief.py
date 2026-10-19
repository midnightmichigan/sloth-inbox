"""Template-based morning brief generator + JSON outputs (stdlib only).

The brief is assembled from deterministic templates over the
classification results — the model adapter contributes only the
one-line "sloth take", and its source is always labeled.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field

from .messages import Message, utcnow_iso
from .classifier import Classification, TriageClassifier, CATEGORIES
from .models import ModelAdapter, SlothModelError

_GREETINGS = [
    "Good morning, fellow sloth.",
    "Rise and... actually, no rush.",
    "The inbox did the overnight shift. You just woke up.",
]

_CATEGORY_LABELS = {
    "needs-you": "need you",
    "newsletter": "newsletters filed for later",
    "promo": "promos quarantined",
    "receipt": "receipts archived",
    "social": "social pings",
    "low": "low-priority drift",
}


@dataclass
class MorningBrief:
    generated_at: str
    adapter: dict
    headline: str                 # 2-3 line morning brief
    lines: list[str]
    sections: dict[str, list[dict]]  # category -> [{id, sender, subject}]
    stats: dict
    sloth_take: str
    take_source: str             # "mock" | "ollama:<model>" | "template-fallback"


def _by_id(messages: list[Message]) -> dict[str, Message]:
    return {m.id: m for m in messages}


def build_brief(messages: list[Message],
                classifications: list[Classification],
                adapter: ModelAdapter) -> MorningBrief:
    lookup = _by_id(messages)
    counts = Counter(c.category for c in classifications)
    total = len(messages)

    # Sections: top items per category (keep briefs short).
    sections: dict[str, list[dict]] = {}
    for cat in CATEGORIES:
        items = [c for c in classifications if c.category == cat]
        rows = []
        for c in items[:5]:
            m = lookup.get(c.message_id)
            rows.append({
                "id": c.message_id,
                "sender": m.sender if m else "",
                "subject": m.subject if m else "",
                "confidence": c.confidence,
            })
        sections[cat] = rows

    # Headline, line 1: greeting + count summary.
    greet = _GREETINGS[total % len(_GREETINGS)]
    if total == 0:
        line1 = f"{greet} Nothing arrived overnight. The branch is yours."
        line2 = "No triage needed. This is peak sloth."
        parts, line3 = [], None
    else:
        parts = [f"{counts[c]} {_CATEGORY_LABELS[c]}" for c in CATEGORIES if counts[c]]
        line1 = f"{greet} {total} message{'s' if total != 1 else ''} arrived overnight: " + ", ".join(parts) + "."
        need_items = [c for c in classifications if c.category == "needs-you"][:3]
        if need_items:
            names = "; ".join(
                (lookup.get(c.message_id).subject or "(no subject)").strip()[:60]
                for c in need_items
            )
            line2 = f"Worth your energy: {names}."
        else:
            line2 = "Nothing needs you. Genuinely. Check the newsletters never."

    # Sloth take: model adapter, with honest fallback labeling.
    stats = {"total": total, "by_category": {c: counts[c] for c in CATEGORIES}}
    try:
        take = adapter.sloth_take(stats)
        take_source = f"{adapter.kind}:{adapter.model_name}"
    except (SlothModelError, NotImplementedError, Exception):  # noqa: BLE001
        take = ("The sloth is unreachable; assume nothing is urgent "
                "until proven otherwise.")
        take_source = "template-fallback"

    line3 = f"Sloth take [{take_source}]: {take}"
    lines = [line1, line2, line3] if total else [line1, line2, line3]
    headline = "\n".join(lines[:3])

    return MorningBrief(
        generated_at=utcnow_iso(),
        adapter=adapter.adapter_info(),
        headline=headline,
        lines=lines,
        sections=sections,
        stats=stats,
        sloth_take=take,
        take_source=take_source,
    )


def brief_to_json(brief: MorningBrief) -> str:
    return json.dumps({
        "generated_at": brief.generated_at,
        "adapter": brief.adapter,
        "headline": brief.headline,
        "lines": brief.lines,
        "sections": brief.sections,
        "stats": brief.stats,
        "sloth_take": brief.sloth_take,
        "take_source": brief.take_source,
    }, indent=2, ensure_ascii=False)


def ledger_to_json(messages: list[Message],
                   classifications: list[Classification]) -> str:
    """Full audit ledger: every message, its bucket, confidence, reasons."""
    lookup = _by_id(messages)
    rows = []
    for c in classifications:
        m = lookup.get(c.message_id)
        row = c.to_dict()
        row["sender"] = m.sender if m else ""
        row["subject"] = m.subject if m else ""
        rows.append(row)
    return json.dumps({"generated_at": utcnow_iso(), "items": rows},
                      indent=2, ensure_ascii=False)


def triage(messages: list[Message], adapter: ModelAdapter) -> tuple[MorningBrief, str]:
    """One-call pipeline: classify -> brief -> (brief, ledger JSON)."""
    clf = TriageClassifier()
    classifications = clf.classify_all(messages)
    brief = build_brief(messages, classifications, adapter)
    return brief, ledger_to_json(messages, classifications)
