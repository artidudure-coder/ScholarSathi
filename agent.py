"""The agent: an LLM that plans and calls tools (retrieval, eligibility engine, document list).

Online  -> Claude decides which tools to call (tool-use loop) and writes a grounded answer.
Offline -> the same tools run in a fixed pipeline and results are formatted without an LLM.
"""
import json
import criteria
import eligibility
import llm
from rag import Retriever

SYSTEM = """You are ScholarSathi, an assistant that helps Indian college students find scholarships.
Rules: (1) Never decide eligibility yourself - call check_eligibility and report its result.
(2) Answer questions about scheme details only from search_schemes results and name the scheme.
(3) If a scheme is NOT ELIGIBLE, explain which rule failed and what could change it.
(4) Mention deadlines and days left. (5) Say clearly when information is not in the documents.
(6) Remind the student to verify on the official portal before applying."""

TOOLS = [
    {"name": "search_schemes", "description": "Search scheme documents for details (benefits, process, documents, rules).",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "check_eligibility", "description": "Run the eligibility engine on the student's saved profile for all schemes. Returns ranked results with passed/failed rules and deadlines.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_documents", "description": "Get the document checklist for one scheme by name.",
     "input_schema": {"type": "object", "properties": {"scheme": {"type": "string"}}, "required": ["scheme"]}},
]


class ScholarAgent:
    def __init__(self, profile):
        self.profile = profile
        self.retriever = Retriever()
        self.criteria = criteria.load_all()
        self.history = []

    # ---- tools ----
    def search_schemes(self, query):
        return self.retriever.search(query, k=3)

    def check_eligibility(self):
        return eligibility.rank(self.profile, self.criteria)

    def get_documents(self, scheme):
        for c in self.criteria.values():
            if scheme.lower() in c["name"].lower():
                return {"scheme": c["name"], "documents": c["documents"]}
        return {"error": f"No scheme matching '{scheme}'"}

    def _run_tool(self, name, args):
        return {"search_schemes": lambda: self.search_schemes(args["query"]),
                "check_eligibility": self.check_eligibility,
                "get_documents": lambda: self.get_documents(args["scheme"])}[name]()

    # ---- online mode ----
    def ask(self, question, max_steps=6):
        if not llm.available():
            return self.offline_answer(question)
        profile_txt = json.dumps(self.profile)
        self.history.append({"role": "user", "content": f"Student profile: {profile_txt}\n\nQuestion: {question}"})
        for _ in range(max_steps):
            r = llm.client().messages.create(model=llm.MODEL, max_tokens=1500, system=SYSTEM,
                                             tools=TOOLS, messages=self.history)
            self.history.append({"role": "assistant", "content": r.content})
            calls = [b for b in r.content if b.type == "tool_use"]
            if not calls:
                return "".join(b.text for b in r.content if b.type == "text")
            results = [{"type": "tool_result", "tool_use_id": b.id,
                        "content": json.dumps(self._run_tool(b.name, b.input), default=str)} for b in calls]
            self.history.append({"role": "user", "content": results})
        return "Sorry, I could not finish within the step limit."

    # ---- offline mode ----
    def offline_answer(self, question=""):
        lines = []
        for r in self.check_eligibility():
            if r["status"] == "ELIGIBLE":
                lines.append(f"[ELIGIBLE] {r['scheme']} - {r['benefit']}\n   Deadline: {r['deadline']} ({r['days_left']} days left)"
                             + ("  << APPLY SOON" if r["days_left"] is not None and r["days_left"] <= 21 else ""))
                lines += [f"   + {p}" for p in r["passed"]]
                lines.append("   Documents: " + "; ".join(r["documents"]))
            elif r["status"] == "NOT ELIGIBLE":
                lines.append(f"[NOT ELIGIBLE] {r['scheme']}")
                lines += [f"   - {f}" for f in r["failed"]]
            else:
                lines.append(f"[CLOSED] {r['scheme']} (deadline {r['deadline']} has passed)")
            lines.append("")
        if question.strip():
            lines.append(f"Most relevant text for: \"{question}\"")
            for h in self.search_schemes(question):
                lines.append(f"   ({h['scheme']}, score {h['score']}) {h['text']}")
        lines.append("\nPlease verify details on the official portal before applying.")
        return "\n".join(lines)
