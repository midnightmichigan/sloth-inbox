"""Deterministic rule+heuristic triage classifier (stdlib only).

Six buckets, scored in priority order; ties break to the higher-priority
category so results are fully deterministic. Every classification carries
its reasons (the keywords/rules that fired) for the audit ledger.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .messages import Message

CATEGORIES = ("needs-you", "newsletter", "promo", "receipt", "social", "low")

# keyword -> weight. Subject hits count double (checked separately).
_RULES: dict[str, list[tuple[str, int]]] = {
    "needs-you": [
        ("payment due", 5), ("past due", 5), ("overdue", 5), ("final notice", 5),
        ("action required", 5), ("action needed", 5), ("please reply", 4),
        ("rsvp", 4), ("appointment", 4), ("reminder:", 3), ("reminder ", 3),
        ("deadline", 4), ("due date", 4), ("due on", 3), ("due by", 3),
        ("bill", 3), ("invoice", 3), ("statement", 2), ("balance due", 4),
        ("school", 3), ("permission slip", 5), ("parent-teacher", 4),
        ("court", 4), ("jury duty", 5), ("doctor", 2), ("dentist", 2),
        ("w-2", 3), ("tax", 2), ("eviction", 5), ("shutoff", 5),
        ("respond by", 4), ("let me know", 2), ("confirm", 2),
    ],
    "newsletter": [
        ("newsletter", 5), ("weekly digest", 5), ("daily digest", 5),
        ("roundup", 4), ("this week in", 4), ("unsubscribe", 6),
        ("view in browser", 3), ("manage preferences", 4),
        ("you're receiving this because", 5), ("you are receiving this", 5),
    ],
    "promo": [
        ("sale", 3), ("discount", 3), ("coupon", 3), ("promo code", 4),
        ("% off", 4), ("deal", 2), ("clearance", 3), ("limited time", 3),
        ("exclusive offer", 4), ("buy one get", 4), ("free shipping", 3),
        ("shop now", 3), ("ends tonight", 3), ("doorbuster", 4),
    ],
    "receipt": [
        ("order confirmation", 5), ("your receipt", 5), ("receipt for", 4),
        ("shipped", 4), ("tracking number", 5), ("on its way", 3),
        ("delivered", 3), ("your order", 4), ("payment received", 4),
        ("thank you for your purchase", 5), ("billing receipt", 5),
    ],
    "social": [
        ("mentioned you", 5), ("tagged you", 5), ("liked your", 4),
        ("commented on", 4), ("new follower", 4), ("friend request", 4),
        ("replied to your", 4), ("invited you", 3), ("poked you", 5),
        ("notification", 2),
    ],
}

# Sender-domain hints: newsletters/promos usually come from bulk senders.
_BULK_HINTS = ("noreply", "no-reply", "donotreply", "news", "updates",
               "offers", "deals", "marketing", "info@")


@dataclass
class Classification:
    message_id: str
    category: str
    confidence: float            # 0.0 - 1.0
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "category": self.category,
            "confidence": round(self.confidence, 3),
            "reasons": self.reasons,
        }


class TriageClassifier:
    """Deterministic classifier. classify() is pure: same input, same output."""

    def classify(self, msg: Message) -> Classification:
        blob = msg.text_blob()
        subject = msg.subject.lower()
        sender = msg.sender.lower()
        reasons: list[str] = []

        # Hard structural signals first (deterministic, high weight).
        structural: dict[str, int] = {}
        meta = msg.meta or {}
        if meta.get("list_unsubscribe") or "unsubscribe" in blob:
            structural["newsletter"] = structural.get("newsletter", 0) + 6
            reasons.append("rule: unsubscribe signal -> newsletter")

        scores = {c: 0.0 for c in CATEGORIES}
        for cat, rules in _RULES.items():
            for kw, w in rules:
                if kw in subject:
                    scores[cat] += w * 2.0
                    reasons.append(f"subject hit: '{kw}' (+{w * 2}) -> {cat}")
                elif kw in blob:
                    scores[cat] += w * 1.0
                    reasons.append(f"body/sender hit: '{kw}' (+{w}) -> {cat}")

        for cat, bonus in structural.items():
            scores[cat] += bonus

        # Bulk-sender nudge: pushes ambiguous marketing mail to promo/newsletter.
        if any(h in sender for h in _BULK_HINTS) and scores["needs-you"] == 0:
            if scores["promo"] > 0 or scores["newsletter"] > 0:
                scores["promo"] += 1.0
                scores["newsletter"] += 1.0

        # Winner: highest score, ties break toward higher-priority category.
        best = "low"
        best_score = 0.0
        for cat in CATEGORIES:
            if scores[cat] > best_score:
                best, best_score = cat, scores[cat]
        if best_score == 0:
            best, reasons = "low", ["rule: no signals matched -> low"]

        total = sum(scores.values())
        confidence = min(1.0, (best_score / total) if total else 0.0)
        # Strong single-signal matches deserve high confidence.
        if best_score >= 8:
            confidence = max(confidence, 0.85)
        elif best_score >= 4:
            confidence = max(confidence, 0.6)

        return Classification(message_id=msg.id, category=best,
                              confidence=confidence, reasons=reasons)

    def classify_all(self, messages: list[Message]) -> list[Classification]:
        return [self.classify(m) for m in messages]
