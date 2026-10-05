"""Thin wrapper around the Anthropic API. Everything still works offline if no key is set."""
import os

MODEL = os.environ.get("SCHOLARSATHI_MODEL", "claude-sonnet-5-5")
_client = None


def available():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def complete(system, user, max_tokens=1500):
    r = client().messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                 messages=[{"role": "user", "content": user}])
    return "".join(b.text for b in r.content if b.type == "text")
