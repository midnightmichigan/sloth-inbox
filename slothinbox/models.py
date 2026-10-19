"""Pluggable model layer (stdlib only).

The model NEVER sees raw email. It receives only aggregate stats
(counts per category + top subject lines of action items) and returns
a one-line "sloth take" for the morning brief. Privacy by architecture.

Adapters:
  MockModelAdapter  — deterministic canned take; used by tests and when
                       no local model is installed. Its output is clearly
                       labeled "mock" everywhere it appears.
  OllamaAdapter     — calls a local Ollama server (default model "gemma3",
                       Google's open-weight Gemma). No API keys, no network
                       beyond localhost, $0 forever.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error


class SlothModelError(RuntimeError):
    """Raised when the local model cannot be reached."""


class ModelAdapter:
    """Common interface. Every adapter reports its kind honestly."""

    kind = "base"
    model_name = "unknown"

    def adapter_info(self) -> dict:
        return {"kind": self.kind, "model": self.model_name, "local": True}

    def sloth_take(self, stats: dict) -> str:
        """One-line lazy verdict on the inbox, given aggregate stats."""
        raise NotImplementedError

    def probe(self) -> bool:
        """True if this adapter is usable right now."""
        return True


class MockModelAdapter(ModelAdapter):
    """Deterministic canned take. For tests and offline use only."""

    kind = "mock"
    model_name = "mock-canned-take-v1"

    def sloth_take(self, stats: dict) -> str:
        total = stats.get("total", 0)
        needs = stats.get("by_category", {}).get("needs-you", 0)
        if total == 0:
            return "Inbox: empty. The sloth approves of this development. [mock take]"
        if needs == 0:
            return (f"{total} messages, zero need you. "
                    "File them later. Nap now. [mock take]")
        return (f"{needs} of {total} need you; the rest can marinate. "
                "Handle the few, ignore the many. [mock take]")


class OllamaAdapter(ModelAdapter):
    """Local open-weight inference via Ollama. Default target: Gemma 3.

    Requires `ollama serve` running locally and a Gemma model pulled, e.g.:
        ollama pull gemma3
    """

    kind = "ollama"
    DEFAULT_MODEL = "gemma3"

    def __init__(self, model: str = DEFAULT_MODEL,
                 host: str = "http://localhost:11434",
                 timeout: float = 60.0):
        self.model_name = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def adapter_info(self) -> dict:
        info = super().adapter_info()
        info["host"] = self.host
        return info

    def probe(self) -> bool:
        """Check the Ollama server is up without generating anything."""
        req = urllib.request.Request(self.host + "/api/tags", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except (urllib.error.URLError, OSError, TimeoutError):
            return False

    def sloth_take(self, stats: dict) -> str:
        prompt = (
            "You are the Sloth, a laconic morning assistant. Given these inbox "
            "triage stats (JSON), write ONE short lazy-but-helpful verdict line "
            "(max 25 words) telling the human what deserves their energy today. "
            "Dry humor welcome. Do not invent specific emails; only use the counts.\n"
            f"STATS: {json.dumps(stats)}"
        )
        payload = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 60},
        }).encode("utf-8")
        req = urllib.request.Request(
            self.host + "/api/generate", data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            raise SlothModelError(
                f"Ollama not reachable at {self.host} "
                f"(is `ollama serve` running? model '{self.model_name}' pulled?). "
                f"Detail: {e}"
            ) from e
        text = str(data.get("response", "")).strip().replace("\n", " ")
        if not text:
            raise SlothModelError("Ollama returned an empty response.")
        return text
