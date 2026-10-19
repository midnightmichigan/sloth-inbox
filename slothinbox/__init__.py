"""The Sloth Inbox — a local overnight inbox triager.

stdlib-only core. Private email never leaves the machine:
classification is deterministic rule+heuristic; the optional model
layer (Mock or local Ollama/Gemma) only writes a one-line sloth take.
"""
from .messages import Message, load_inbox
from .classifier import TriageClassifier, CATEGORIES
from .models import ModelAdapter, MockModelAdapter, OllamaAdapter, SlothModelError
from .brief import MorningBrief, build_brief, brief_to_json, ledger_to_json

__all__ = [
    "Message", "load_inbox",
    "TriageClassifier", "CATEGORIES",
    "ModelAdapter", "MockModelAdapter", "OllamaAdapter", "SlothModelError",
    "MorningBrief", "build_brief", "brief_to_json", "ledger_to_json",
]
__version__ = "0.1.0"
