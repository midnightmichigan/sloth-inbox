#!/usr/bin/env python3
"""test_flow.py — The Sloth Inbox checks. Run: python3 test_flow.py

Everything runs against MockModelAdapter (no local model needed).
Exit code 0 = all checks passed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from slothinbox.messages import Message
from slothinbox.classifier import TriageClassifier, CATEGORIES
from slothinbox.models import (
    ModelAdapter, MockModelAdapter, OllamaAdapter, SlothModelError,
)
from slothinbox.brief import triage, brief_to_json, build_brief
from slothinbox.demo_inbox import FIXTURE_MESSAGES, EXPECTED

CHECKS = []


def check(name, fn):
    try:
        fn()
        CHECKS.append((name, True, ""))
    except AssertionError as e:
        CHECKS.append((name, False, str(e) or "assert failed"))
    except Exception as e:  # noqa: BLE001
        CHECKS.append((name, False, f"{type(e).__name__}: {e}"))


def fixture_messages():
    return [Message.from_dict(dict(r)) for r in FIXTURE_MESSAGES]


CLF = TriageClassifier()
MOCK = MockModelAdapter()


# --- 1. fixture loads ---
def t_fixture_loads():
    msgs = fixture_messages()
    assert len(msgs) == 14, f"expected 14, got {len(msgs)}"
    assert all(isinstance(m, Message) for m in msgs)


# --- 2. classification accuracy on the labeled fixture ---
def t_accuracy_all_match():
    got = {c.message_id: c.category for c in CLF.classify_all(fixture_messages())}
    bad = {k: (EXPECTED[k], got.get(k)) for k in EXPECTED if got.get(k) != EXPECTED[k]}
    assert not bad, f"misclassified: {bad}"


# --- 3. confidence sane ---
def t_confidence_range():
    for c in CLF.classify_all(fixture_messages()):
        assert 0.0 <= c.confidence <= 1.0, (c.message_id, c.confidence)
        if c.category == "low":
            # "low" is the honest no-evidence default: zero signals, zero confidence
            assert c.confidence == 0.0, (c.message_id, c.confidence)
        else:
            assert c.confidence >= 0.6, (c.message_id, c.confidence)  # strong fixture signals


# --- 4. reasons are audit-grade ---
def t_reasons_present():
    for c in CLF.classify_all(fixture_messages()):
        assert isinstance(c.reasons, list) and len(c.reasons) >= 1, c.message_id
        assert c.category in CATEGORIES, c.category


# --- 5. determinism ---
def t_deterministic():
    a = [c.to_dict() for c in CLF.classify_all(fixture_messages())]
    b = [c.to_dict() for c in CLF.classify_all(fixture_messages())]
    assert a == b, "classifier is not deterministic"


# --- 6. empty inbox: no crash, honest brief ---
def t_empty_inbox():
    brief, ledger_json = triage([], MOCK)
    assert "Nothing arrived" in brief.headline, brief.headline
    assert len(brief.lines) <= 3
    ledger = json.loads(ledger_json)
    assert ledger["items"] == []
    assert brief.take_source.startswith("mock")


# --- 7. headline is 2-3 lines ---
def t_headline_length():
    brief, _ = triage(fixture_messages(), MOCK)
    assert 1 <= len(brief.lines) <= 3, brief.lines
    assert brief.headline == "\n".join(brief.lines)


# --- 8. brief.json schema ---
def t_brief_json_schema():
    brief, _ = triage(fixture_messages(), MOCK)
    data = json.loads(brief_to_json(brief))
    for key in ("generated_at", "adapter", "headline", "lines",
                "sections", "stats", "sloth_take", "take_source"):
        assert key in data, f"missing key {key}"
    assert data["stats"]["total"] == 14
    assert data["adapter"]["kind"] == "mock"
    assert set(data["sections"]) == set(CATEGORIES)


# --- 9. ledger covers every message ---
def t_ledger_complete():
    _, ledger_json = triage(fixture_messages(), MOCK)
    items = json.loads(ledger_json)["items"]
    assert len(items) == 14
    ids = {i["message_id"] for i in items}
    assert ids == set(EXPECTED), ids ^ set(EXPECTED)
    for i in items:
        assert i["reasons"], i["message_id"]


# --- 10. mock adapter honesty labels ---
def t_mock_labels():
    take = MOCK.sloth_take({"total": 14, "by_category": {"needs-you": 4}})
    assert take and "[mock take]" in take, take
    info = MOCK.adapter_info()
    assert info["kind"] == "mock" and info["local"] is True
    assert MOCK.probe() is True


# --- 11. adapter interface consistency ---
def t_adapter_interface():
    for cls in (MockModelAdapter, OllamaAdapter):
        for attr in ("kind", "model_name", "sloth_take", "probe", "adapter_info"):
            assert hasattr(cls, attr), f"{cls.__name__} missing {attr}"
    assert issubclass(MockModelAdapter, ModelAdapter)
    assert issubclass(OllamaAdapter, ModelAdapter)


# --- 12. OllamaAdapter degrades cleanly with no server ---
def t_ollama_no_server():
    ad = OllamaAdapter(model="gemma3", timeout=2.0)
    assert ad.probe() is False, "unexpected Ollama server in test env"
    try:
        ad.sloth_take({"total": 1, "by_category": {}})
    except SlothModelError as e:
        assert "gemma3" in str(e) or "Ollama" in str(e)
    else:
        raise AssertionError("expected SlothModelError with no server")
    # pipeline still produces a brief via template fallback
    brief, _ = triage(fixture_messages(), ad)
    assert brief.take_source == "template-fallback"
    assert len(brief.lines) <= 3


# --- 13. malformed rows tolerated ---
def t_malformed_rows():
    raws = [None, "nope", {}, {"id": "x"}, {"subject": "Payment due now!"}]
    msgs = [Message.from_dict(r) for r in raws]
    out = CLF.classify_all(msgs)
    assert len(out) == 5
    assert out[4].category == "needs-you", out[4].category


# --- 14. unicode / emoji subjects don't crash ---
def t_unicode_subject():
    m = Message(id="u1", sender="a@b.c", subject="Fw: Fw: funny sloth video 🦥💤",
                body="tömör levelek… slowly…")
    c = CLF.classify(m)
    assert c.category == "low", c.category
    brief, ledger_json = triage([m], MOCK)
    assert json.loads(ledger_json)["items"][0]["message_id"] == "u1"
    assert "🦥" in brief_to_json(brief)  # ensure_ascii=False keeps emoji readable


# --- 15. headline names real action items ---
def t_headline_names_action_items():
    brief, _ = triage(fixture_messages(), MOCK)
    line2 = brief.lines[1]
    assert "electric bill" in line2 or "water bill" in line2, line2


for _name, _fn in sorted(
    [(k, v) for k, v in list(globals().items()) if k.startswith("t_")]
):
    check(_name, _fn)

if __name__ == "__main__":
    failed = [c for c in CHECKS if not c[1]]
    for name, ok, err in CHECKS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + ("" if ok else f" — {err}"))
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed.")
    sys.exit(1 if failed else 0)
