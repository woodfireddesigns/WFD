#!/usr/bin/env python3
"""Space size x demand model for Little Shore Play Cafe.

Every cost that moves with square footage is scaled from one table of per-size
assumptions (all estimates unless noted), then each size is run at several demand
levels through founder-cfo's unit_economics.py.

    python3 sizes.py
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

# Per-size assumptions. Rent anchor: founder quote $2,700-3,000/mo for 1,800-2,500 sq ft
# (~$14.40/sq ft/yr). Everything else is an estimate to replace with quotes.
SIZES = {
    2500: dict(rent=3000, nnn=730, util=700, staff_hrs=84, insurance=450, cleaning=400,
               construction=70000, play=60000, furniture=15000, equipment=18000,
               play_floor_sqft=1375, party_rooms=1, deposit=7500),
    3500: dict(rent=4200, nnn=1020, util=980, staff_hrs=110, insurance=550, cleaning=550,
               construction=95000, play=85000, furniture=20000, equipment=18000,
               play_floor_sqft=1925, party_rooms=1, deposit=10000),
    4500: dict(rent=5400, nnn=1310, util=1260, staff_hrs=135, insurance=650, cleaning=700,
               construction=120000, play=105000, furniture=25000, equipment=20000,
               play_floor_sqft=2475, party_rooms=2, deposit=12500),
}
SQFT_PER_KID = 35        # calm density on the play floor (design target, not a fire-code number)
KIDS_PER_FAMILY = 1.3
AVG_STAY_HRS = 1.75
PEAK_TURNS = 3.5         # effective full turns a day, given demand bunches in mornings and weekends
WAGE_BURDENED = 15 * 1.12


def capacity(sz):
    kids = sz["play_floor_sqft"] / SQFT_PER_KID
    families_at_once = kids / KIDS_PER_FAMILY
    return round(kids), round(families_at_once), round(families_at_once * PEAK_TURNS)


def scenario(base, sqft, visits_per_day, members, parties):
    s = copy.deepcopy(base)
    sz = SIZES[sqft]
    kids, fams, cap = capacity(sz)
    s["capacity_per_day"] = cap
    m = s["steady_state_month"]
    m["member_families"] = members
    member_visits = members * m["visits_per_member_family"]
    total = visits_per_day * 26
    other = max(total - member_visits, 0)
    m["pack_visits"] = round(other * 0.36)          # same pack/drop-in split as the recommended plan
    m["family_visits_per_day"] = max(visits_per_day, member_visits / 26)
    m["parties_per_month"] = parties
    scale = m["family_visits_per_day"] / 38.0
    s["ramp_per_day"] = [v * scale for v in base["ramp_per_day"]]
    staff = sz["staff_hrs"] * 4.33 * WAGE_BURDENED
    repl = {
        "Rent, base": sz["rent"], "NNN / CAM": sz["nnn"], "Utilities": sz["util"],
        "Hired staff": round(staff), "Insurance": sz["insurance"], "Cleaning": sz["cleaning"],
    }
    for f in s["fixed_monthly"]:
        for k, v in repl.items():
            if f["label"].startswith(k):
                f["cost"] = v
    build = sz["construction"] + sz["play"]
    st = {"Lease deposit": sz["deposit"], "Construction": sz["construction"], "Custom play": sz["play"],
          "Furniture": sz["furniture"], "Cafe equipment": sz["equipment"], "Build-out contingency": round(build * 0.15)}
    for f in s["startup"]:
        for k, v in st.items():
            if f["label"].startswith(k):
                f["cost"] = v
    return s, (kids, fams, cap)


def run(s):
    n, mx = mix.build(s)
    a = ue.analyse(n)
    steady = a["plan_per_day"] * 26 * a["contribution"] - a["fixed_monthly"]
    return a, steady, mx


def main():
    base = json.load(open(os.path.join(HERE, "scenario-v4-all-levers.json")))
    for sqft in SIZES:
        s, (kids, fams, cap) = scenario(base, sqft, 38, 25, 10)
        a, steady, _ = run(s)
        print("\n%d sq ft: ~%d kids at once (%d families), ~%d family visits/day capacity, fixed $%s/mo, startup $%s" % (
            sqft, kids, fams, cap, "{:,.0f}".format(a["fixed_monthly"]), "{:,.0f}".format(a["startup"])))
        print("  %-28s %8s %10s %10s %11s %8s" % ("demand (steady)", "BE/day", "Y1 profit", "steady/mo", "cash need", "util"))
        for vpd, mem, parties in ((38, 25, 10), (50, 60, 12), (65, 100, 14), (80, 150, 16), (100, 200, 20)):
            if vpd > cap * 1.05:
                print("  %3d visits/day, %3d members   over capacity" % (vpd, mem))
                continue
            s, _ = scenario(base, sqft, vpd, mem, parties if sqft == 4500 else min(parties, 14))
            a, steady, mx = run(s)
            print("  %3d visits/day, %3d members %8.1f %10s %10s %11s %7.0f%%" % (
                vpd, mem, a["breakeven_per_day"], "{:,.0f}".format(a["year1_profit"]),
                "{:,.0f}".format(steady), "{:,.0f}".format(a["cash_needed"]), 100 * vpd / cap))


if __name__ == "__main__":
    main()
