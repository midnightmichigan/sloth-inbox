#!/usr/bin/env python3
"""run_sloth.py — overnight inbox triage from the command line.

Usage:
    python3 run_sloth.py --demo
    python3 run_sloth.py --inbox inbox.json --adapter mock --out ./out
    python3 run_sloth.py --demo --adapter ollama --model gemma3

Writes brief.json + ledger.json into --out and prints the morning brief.
The model adapter only ever receives aggregate stats, never raw email.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from slothinbox.messages import Message
from slothinbox.demo_inbox import FIXTURE_MESSAGES
from slothinbox.brief import triage, brief_to_json
from slothinbox.models import MockModelAdapter, OllamaAdapter, SlothModelError


def build_adapter(name: str, model: str):
    if name == "ollama":
        return OllamaAdapter(model=model)
    return MockModelAdapter()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The Sloth Inbox — overnight triage")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--demo", action="store_true", help="use the synthetic fixture inbox")
    src.add_argument("--inbox", help="path to a JSON inbox file")
    ap.add_argument("--adapter", choices=["mock", "ollama"], default="mock",
                    help="model adapter (default: mock)")
    ap.add_argument("--model", default=OllamaAdapter.DEFAULT_MODEL,
                    help="Ollama model name (default: gemma3)")
    ap.add_argument("--out", default="out", help="output directory for JSON")
    args = ap.parse_args(argv)

    if args.demo:
        messages = [Message.from_dict(r) for r in FIXTURE_MESSAGES]
    else:
        from slothinbox.messages import load_inbox
        messages = load_inbox(args.inbox)

    adapter = build_adapter(args.adapter, args.model)

    if args.adapter == "ollama" and not adapter.probe():
        print(f"warning: Ollama not reachable; brief will use template fallback "
              f"for the sloth take (classification is unaffected).", file=sys.stderr)

    brief, ledger_json = triage(messages, adapter)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "brief.json").write_text(brief_to_json(brief), encoding="utf-8")
    (outdir / "ledger.json").write_text(ledger_json, encoding="utf-8")

    print("=" * 60)
    print("🦥  THE SLOTH INBOX — morning brief")
    print("=" * 60)
    print(brief.headline)
    print("-" * 60)
    print(f"adapter : {brief.take_source}")
    print(f"ledger  : {outdir / 'ledger.json'} ({len(messages)} messages classified)")
    print(f"brief   : {outdir / 'brief.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
