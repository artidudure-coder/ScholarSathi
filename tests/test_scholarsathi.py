import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from datetime import date
import criteria, eligibility
from rag import Retriever

TODAY = date(2026, 10, 5)
C = criteria.load_all(use_llm=False)


def status(profile, scheme):
    r = [x for x in eligibility.rank(profile, C, TODAY) if x["scheme"] == scheme][0]
    return r["status"]


P1 = dict(category="OBC", income=450000, level="UG", percentage=72, gender="Female", domicile="Maharashtra")
P2 = dict(category="Open", income=900000, level="UG", percentage=58, gender="Male", domicile="Maharashtra")
P3 = dict(category="Open", income=250000, level="Diploma", percentage=60, gender="Male", domicile="Maharashtra")

CASES = [
    (P1, "Demo State Merit Scholarship", "ELIGIBLE"),
    (P1, "Demo Backward Class Tuition Fee Waiver", "ELIGIBLE"),
    (P1, "Demo Girls in Technology Fellowship", "ELIGIBLE"),
    (P1, "Demo EWS Hostel and Mess Aid", "NOT ELIGIBLE"),
    (P2, "Demo State Merit Scholarship", "NOT ELIGIBLE"),
    (P2, "Demo Girls in Technology Fellowship", "NOT ELIGIBLE"),
    (P3, "Demo EWS Hostel and Mess Aid", "ELIGIBLE"),
    (P3, "Demo Diploma Student Support Grant", "CLOSED"),
]
RETRIEVAL = [
    ("which documents are needed for caste certificate fee waiver", "Demo Backward Class Tuition Fee Waiver"),
    ("statement of purpose mentor fellowship for women", "Demo Girls in Technology Fellowship"),
    ("hostel and mess charges monthly aid", "Demo EWS Hostel and Mess Aid"),
    ("laptop books tools grant diploma", "Demo Diploma Student Support Grant"),
    ("merit scholarship Rs 25,000 per year", "Demo State Merit Scholarship"),
]

if __name__ == "__main__":
    ok = 0
    for p, s, exp in CASES:
        got = status(p, s); ok += got == exp
        print(("PASS" if got == exp else "FAIL"), s, "->", got, "(expected", exp + ")")
    print(f"Eligibility engine: {ok}/{len(CASES)} correct\n")
    R = Retriever(); hit = 0
    for q, exp in RETRIEVAL:
        top = R.search(q, 1)[0]["scheme"]; hit += top == exp
        print(("PASS" if top == exp else "FAIL"), q, "->", top)
    print(f"Retrieval hit@1: {hit}/{len(RETRIEVAL)}")
    assert ok == len(CASES) and hit == len(RETRIEVAL)
