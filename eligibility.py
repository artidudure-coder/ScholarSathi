"""Deterministic, explainable eligibility engine (no LLM guesswork in the final decision)."""
from datetime import date, datetime

PROFILE_FIELDS = ["category", "income", "level", "percentage", "gender", "domicile"]


def check(profile, c, today=None):
    today = today or date.today()
    passed, failed = [], []

    def rule(ok, good, bad):
        (passed if ok else failed).append(good if ok else bad)

    if c.get("categories"):
        rule(profile["category"] in c["categories"],
             f"Category {profile['category']} is covered",
             f"Only for categories: {', '.join(c['categories'])} (you: {profile['category']})")
    if c.get("max_income") is not None:
        rule(profile["income"] <= c["max_income"],
             f"Income Rs {profile['income']:,.0f} is within the Rs {c['max_income']:,.0f} limit",
             f"Family income must be at most Rs {c['max_income']:,.0f} (you: Rs {profile['income']:,.0f})")
    if c.get("levels"):
        rule(profile["level"] in c["levels"],
             f"Course level {profile['level']} is covered",
             f"Only for course levels: {', '.join(c['levels'])} (you: {profile['level']})")
    if c.get("min_percentage") is not None:
        rule(profile["percentage"] >= c["min_percentage"],
             f"{profile['percentage']}% meets the {c['min_percentage']:.0f}% minimum",
             f"Needs at least {c['min_percentage']:.0f}% in the previous exam (you: {profile['percentage']}%)")
    if c.get("genders"):
        rule(profile["gender"] in c["genders"],
             "Gender criterion satisfied", f"Only for: {', '.join(c['genders'])}")
    if c.get("domicile"):
        rule(profile["domicile"].lower() == c["domicile"].lower(),
             f"Domicile {c['domicile']} matches", f"Only for domicile of {c['domicile']} (you: {profile['domicile']})")

    days_left = None
    if c.get("deadline"):
        days_left = (datetime.strptime(c["deadline"], "%Y-%m-%d").date() - today).days
    closed = days_left is not None and days_left < 0
    status = "CLOSED" if closed else ("ELIGIBLE" if not failed else "NOT ELIGIBLE")
    return {"scheme": c["name"], "status": status, "passed": passed, "failed": failed,
            "days_left": days_left, "deadline": c.get("deadline"), "benefit": c.get("benefit", ""),
            "documents": c.get("documents", [])}


def rank(profile, all_criteria, today=None):
    """Eligible first (soonest deadline first), then not eligible by fewest failed rules, closed last."""
    results = [check(profile, c, today) for c in all_criteria.values()]
    order = {"ELIGIBLE": 0, "NOT ELIGIBLE": 1, "CLOSED": 2}
    return sorted(results, key=lambda r: (order[r["status"]],
                                          r["days_left"] if r["status"] == "ELIGIBLE" and r["days_left"] is not None else 9999,
                                          len(r["failed"])))
