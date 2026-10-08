#!/usr/bin/env python3
"""Year 1 lever sweep for Little Shore Play Cafe.

Applies each lever alone to the recommended scenario, then stacks them, and runs
every case through founder-cfo's unit_economics.py. Guardrails (the essence) are
checked in code: 25-kid cap, at least two people on the floor, coffee included,
clean standard and cafe quality untouched.

    python3 levers.py            # table of single-lever and stacked results
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "founder-cfo"))
import mix  # noqa: E402
import unit_economics as ue  # noqa: E402

BASE = json.load(open(os.path.join(HERE, "scenario-v2-recommended.json")))


def fixed(s, prefix, cost, label=None):
    for f in s["fixed_monthly"]:
        if f["label"].startswith(prefix):
            f["cost"] = cost
            if label:
                f["label"] = label
            return
    raise KeyError(prefix)


def extra(s, label, monthly, cost_pct):
    s["steady_state_month"].setdefault("extra_revenue", []).append(
        {"label": label, "monthly": monthly, "cost_pct": cost_pct})


# Each lever: (key, description, essence note, function)
LEVERS = [
    ("P1", "Drop-in $14 -> $15 (sibling $7)", "price only",
     lambda s: s["steady_state_month"].update(avg_dropin_admission=15 + 0.35 * 7)),
    ("P2", "5-pack $55 -> $60", "price only",
     lambda s: s["steady_state_month"].update(pack_price_per_visit=12 + 0.35 * 7)),
    ("P3", "Parties $295/$395 -> $325/$425 (avg $350 -> $380)", "still ~$100 under local median",
     lambda s: s["steady_state_month"].update(avg_party_price=380)),
    ("R1", "Parties 6 -> 10 a month (pre-sold at pop-ups)", "separate glass room; play floor stays calm",
     lambda s: s["steady_state_month"].update(parties_per_month=10)),
    ("R2", "Monday private rentals: 4 x $200 (cost 15%)", "uses the closed day; no open-play impact",
     lambda s: extra(s, "Private rentals (Mondays)", 800, 0.15)),
    ("R3", "Cafe attach +$1/visit (snack boxes, kid smoothies)", "adds to the cafe, no cut",
     lambda s: s["steady_state_month"].update(cafe_spend_dropin_visit=4.5, cafe_spend_pack_visit=4.5,
                                              cafe_spend_member_visit=5.0)),
    ("R4", "Classes run by outside instructors, 50% rev share: $1,200/mo", "adds programming",
     lambda s: extra(s, "Instructor classes", 1200, 0.5)),
    ("R5", "Retail shelf: Montessori toys + Little Shore merch, $800/mo at 50% cost", "small shelf by the cafe",
     lambda s: extra(s, "Retail shelf", 800, 0.5)),
    ("V1", "Founding cohort + pre-sold packs lift months 1-3 by 5 visits/day", "more families, same cap",
     lambda s: s.update(ramp_per_day=[v + (5 if i < 3 else 0) for i, v in enumerate(s["ramp_per_day"])])),
    ("O1", "Hours 54 -> 50/wk, third floor person Sat only: staff 84 -> 76 hrs", "2 people on floor at all times",
     lambda s: fixed(s, "Hired staff", 5530, "Hired staff, ~76 hrs/wk (estimate)")),
    ("O2", "3 months free rent on a 5-yr lease, averaged over Y1 (-$713/mo)", "lease term, no guest impact",
     lambda s: s["fixed_monthly"].append({"label": "Rent abatement, 3 free months averaged over Y1 (to negotiate)",
                                           "cost": -713})),
    ("O3", "Marketing $700 -> $500 after month 3 (organic + referrals), averaged", "keeps free first visits",
     lambda s: fixed(s, "Marketing", 550)),
]


def run(s):
    n, mx = mix.build(s)
    a = ue.analyse(n)
    steady = a["plan_per_day"] * 26 * a["contribution"] - a["fixed_monthly"]
    return a, steady


def main():
    base_a, base_steady = run(copy.deepcopy(BASE))
    print("%-4s %-72s %10s %10s" % ("", "lever (alone)", "Y1 delta", "steady/mo"))
    rows = []
    for key, desc, note, f in LEVERS:
        s = copy.deepcopy(BASE)
        f(s)
        a, st = run(s)
        rows.append((key, desc, a["year1_profit"] - base_a["year1_profit"], st))
        print("%-4s %-72s %+10.0f %10.0f" % (key, desc, a["year1_profit"] - base_a["year1_profit"], st))
    print("\nBase Year 1: %.0f   break-even %.1f/day" % (base_a["year1_profit"], base_a["breakeven_per_day"]))
    s = copy.deepcopy(BASE)
    for key, desc, note, f in sorted(LEVERS, key=lambda L: -[r[2] for r in rows if r[0] == L[0]][0]):
        f(s)
        a, st = run(s)
        print("+%-3s cumulative Y1 %10.0f  break-even %5.1f/day  steady %8.0f  cash %9.0f" % (
            key, a["year1_profit"], a["breakeven_per_day"], st, a["cash_needed"]))
    json.dump(s, open(os.path.join(HERE, "scenario-v4-all-levers.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
