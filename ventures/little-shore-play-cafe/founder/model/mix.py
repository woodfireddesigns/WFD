#!/usr/bin/env python3
"""Revenue-mix bridge for Little Shore Play Cafe.

founder-cfo's unit_economics.py models ONE unit at ONE price. A play cafe sells
memberships, drop-ins, cafe drinks, parties and programs. This script turns a
steady-state month of that mix into one unit, a "paying family visit", with a
blended price and a blended variable cost, then writes a numbers.json the CFO
tool can run. Every input is in the scenario file and labelled with its source.

    python3 mix.py scenario.json --out ../numbers.json
"""
import argparse
import json


def build(s):
    m = s["steady_state_month"]
    days = s["days_per_month"]
    visits = m["family_visits_per_day"] * days

    mem_fam = m["member_families"]
    mem_visits = mem_fam * m["visits_per_member_family"]
    pack_visits = m.get("pack_visits", 0)
    drop_visits = visits - mem_visits - pack_visits
    if drop_visits < 0:
        raise SystemExit("member + pack visits exceed total visits")

    rev = {
        "Memberships": mem_fam * m["avg_member_dues"],
        "Visit packs": pack_visits * m.get("pack_price_per_visit", 0),
        "Drop-in admissions": drop_visits * m["avg_dropin_admission"],
        "Cafe": drop_visits * m["cafe_spend_dropin_visit"]
                + mem_visits * m["cafe_spend_member_visit"]
                + pack_visits * m.get("cafe_spend_pack_visit", m["cafe_spend_dropin_visit"]),
        "Parties": m["parties_per_month"] * m["avg_party_price"],
        "Programs and events": m["programs_revenue"],
    }
    for e in m.get("extra_revenue", []):
        rev[e["label"]] = e["monthly"]
    total = sum(rev.values())
    c = s["cost_rates"]
    var = {
        "Cafe cost of goods": rev["Cafe"] * c["cafe_cogs_pct"],
        "Included drinks (drop-in/pack)": (drop_visits + pack_visits) * c.get("included_drink_cost", 0),
        "Party direct costs": rev["Parties"] * c["party_cost_pct"],
        "Program materials": rev["Programs and events"] * c["program_cost_pct"],
        "Card processing": total * c["card_fee_pct"],
        "Per-visit supplies (sanitizer, wipes, toy wear)": visits * c["supplies_per_visit"],
    }
    for e in m.get("extra_revenue", []):
        var["Direct costs: " + e["label"]] = e["monthly"] * e["cost_pct"]
    price = total / visits
    variable = [{"label": k, "cost": round(v / visits, 2)} for k, v in var.items() if v]
    out = {
        "business": s["business"],
        "unit": "family visit",
        "price": round(price, 2),
        "variable": variable,
        "fixed_monthly": s["fixed_monthly"],
        "startup": s["startup"],
        "days_per_month": days,
        "capacity_per_day": s["capacity_per_day"],
        "plan_per_day": m["family_visits_per_day"],
        "ramp_per_day": s["ramp_per_day"],
    }
    mix = {
        "visits_per_month": visits, "member_visits": mem_visits, "pack_visits": pack_visits,
        "dropin_visits": drop_visits, "revenue": {k: round(v) for k, v in rev.items()},
        "revenue_total": round(total), "price_per_visit": round(price, 2),
        "variable_per_visit": round(sum(var.values()) / visits, 2),
    }
    return out, mix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = json.load(open(a.scenario))
    out, mix = build(s)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(mix, indent=1))


if __name__ == "__main__":
    main()
