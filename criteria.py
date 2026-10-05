"""Turns a scheme document into structured eligibility criteria.

- With an Anthropic API key: the LLM extracts criteria from free-form text (works on real, messy notices).
- Without a key: a regex parser reads the standard 'ELIGIBILITY:' block used in the sample files.
Results are cached so the LLM is called only once per document.
"""
import json
import re
from pathlib import Path
from rag import scheme_name, load_documents
import llm

CACHE = Path(__file__).parent / "data" / "criteria_cache.json"

SCHEMA_HELP = """Return ONLY a JSON object with keys:
name (string), categories (list of strings or null if open to all), max_income (number or null),
levels (list from Diploma/UG/PG or null), min_percentage (number or null),
genders (list of Male/Female/Other or null), domicile (string or null),
deadline (YYYY-MM-DD or null), documents (list of strings), benefit (string)."""


def _any(v):
    return None if v.strip().lower() in ("any", "all", "none", "") else v.strip()


def _list(v):
    v = _any(v)
    return None if v is None else [x.strip() for x in v.split(",") if x.strip()]


def regex_extract(text, fallback="Unknown"):
    def field(label):
        m = re.search(rf"^- {label}:\s*(.+)$", text, re.M | re.I)
        return m.group(1) if m else "any"

    def num(label):
        m = re.search(rf"^- {label}:\s*([\d.]+)", text, re.M | re.I)
        return float(m.group(1)) if m else None

    deadline = re.search(r"^DEADLINE:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    benefit = re.search(r"^BENEFIT:\s*(.+)$", text, re.M)
    docs_block = re.search(r"^DOCUMENTS:\n((?:- .+\n?)+)", text, re.M)
    docs = [d[2:].strip() for d in docs_block.group(1).strip().split("\n")] if docs_block else []
    return {
        "name": scheme_name(text, fallback),
        "categories": _list(field("Category")),
        "max_income": num("Maximum annual family income"),
        "levels": _list(field("Course level")),
        "min_percentage": num("Minimum percentage in previous exam"),
        "genders": _list(field("Gender")),
        "domicile": _any(field("Domicile")),
        "deadline": deadline.group(1) if deadline else None,
        "documents": docs,
        "benefit": benefit.group(1).strip() if benefit else "",
    }


def llm_extract(text):
    reply = llm.complete(
        "You extract scholarship eligibility rules from official notices. Never guess; use null when a rule is not stated.",
        f"{SCHEMA_HELP}\n\nNOTICE:\n{text}")
    return json.loads(re.search(r"\{.*\}", reply, re.S).group(0))


def load_all(use_llm=None):
    use_llm = llm.available() if use_llm is None else use_llm
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    out = {}
    for doc_id, text in load_documents().items():
        key = f"{doc_id}|{'llm' if use_llm else 'regex'}|{hash(text) & 0xffffffff}"
        if key not in cache:
            cache[key] = llm_extract(text) if use_llm else regex_extract(text, doc_id)
        out[doc_id] = cache[key]
    if use_llm:
        CACHE.write_text(json.dumps(cache, indent=1))
    return out
