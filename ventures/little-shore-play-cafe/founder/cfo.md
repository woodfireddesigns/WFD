# The numbers: Little Shore Play Cafe

## The CFO's note

**How this is modeled.** The founder-cfo tool takes one unit at one price. A play cafe sells memberships, drop-ins, packs, coffee, parties and programs, so `model/mix.py` turns one steady-state month of that mix into a **paying family visit**: a blended price of **$20.82** and blended direct costs of **$3.77**. All inputs are in `model/scenario-v2-recommended.json`; the tool output below runs on `numbers.json`. This version includes the ops corrections: about 84 hired hours a week (not 63), Wicomico admissions and amusement tax (~$580/mo, rate to confirm), 3.5% card fees and a 15% build-out contingency. **Owner pay and loan payments are not in fixed costs**; they are shown separately because they decide whether this works.

**The margin.** Each family visit leaves **$17.05** (82%) after its own costs. Fixed costs are **$13,190 a month**. Break-even is **30 paying family visits a day**. At the plan of 38 a day, the profit margin is **18%**, about **$3,650 a month** at steady state.

**Year 1.** **$188k** revenue and an **operating loss of $4,012**, with losses in months 1 to 5. The $221,500 startup spend (incl. contingency) is not earned back in Year 1. **Cash needed before it pays for itself: $238,244.**

**The line to watch: volume, then debt and owner pay.**

| what-if (tool runs) | break-even a day | Year 1 | steady month |
| --- | ---: | ---: | ---: |
| Base plan (38/day at steady state) | 30 | -$4,012 | $3,655 |
| Visits -20% | 30 | -$35,082 | $263 |
| + loan payment on $200k (~$2,588/mo, 10 yrs, ~9.5%, estimate) | 36 | -$35,068 | $1,067 |
| + loan + $3,000/mo owner pay for Jordan (placeholder) | 42 | -$71,068 | -$1,933 |
| 48 visits a day, no loan, no owner pay | 30 | $36,814 | $8,113 |

**Read this plainly:** at 38 family visits a day this is a job that does not pay its operator, on top of a $200k+ debt. It works only if the pop-ups prove demand well above the plan.

**Three ways to improve the margin (each run through the tool):**

1. **Drop-in $14 → $15, pack $55 → $60:** Year 1 -$4,012 → **+$3,408**, break-even 30 → 29. The re-test ceiling is about $16.
2. **Parties 6 → 10 a month:** Year 1 → **+$4,494**. Highest-margin line; pre-sell them.
3. **Staff 84 → 76 hired hours** (third person only Saturday peak): Year 1 → **+$2,948**, break-even 28.

**The biggest lever is the startup bill.** A leaner build-out (construction $45k, catalog play houses $35k, contingency $12k) plus **$15k in signed sponsorships** cuts cash needed from **$238,244 to $165,744** with no change to operations.

**What it takes to pay a lender and Jordan** (all three levers + lean build-out + $15k signed sponsors + a $150k loan at ~$1,941/mo + $3,000/mo owner pay):

| steady paying family visits a day | break-even a day | Year 1 | steady month after loan and owner pay |
| ---: | ---: | ---: | ---: |
| 38 | 37 | -$47,379 | $453 |
| 42 | 37 | -$30,164 | $2,333 |
| 45 | 37 | -$17,314 | $3,736 |
| 48 | 37 | -$4,306 | $5,157 |

**So the go/no-go number for the pop-ups is about 45 paying family visits a day of proven demand**, about 70% of the 65-a-day capacity. Anything that shows the demand sits near 38 a day means the business, as designed, cannot carry debt plus a salary.

**The board's money conditions:**

- [ ] Survives Year 1 with zero sponsor money: **no** (-$4,012 on operations alone, before any loan).
- [ ] 40 refundable founding deposits before a lease: not yet tested. Note the real threshold is visits a day, not member families: members are about 15% of visits at steady state.
- [ ] Pre-sell parties: not yet tested.

Revenue is before Maryland's 6% sales tax on food and prepared drinks; the admissions and amusement tax is modeled as a cost because the price promise is "all-in." Confirm both with the Comptroller and Wicomico County. **Not financial, tax or legal advice: an accountant should check the structure, payroll and tax before money moves.**

---

# Unit economics: Little Shore Play Cafe

Every number below comes from the input file. Nothing is looked up or guessed.

## One family visit

| line | per family visit |
| --- | ---: |
| Price | $20.82 |
| Cafe cost of goods | -$1.07 |
| Included drinks (drop-in/pack) | -$0.51 |
| Party direct costs | -$0.64 |
| Program materials | -$0.32 |
| Card processing | -$0.73 |
| Per-visit supplies (sanitizer, wipes, toy wear) | -$0.50 |
| **Contribution** (what each family visit leaves to pay the fixed costs) | **$17.05** (82%) |

## The margin that matters

Fixed costs: $13,190 a month (Rent, base (founder quote midpoint) $2,850, NNN / CAM (estimate) $700, Utilities and internet (estimate) $700, Hired staff, ~84 hrs/wk at $15 + 12% burden (ops rota, estimate) $6,110, Insurance incl. abuse/molestation (estimate) $450, Software: POS, booking, waivers (estimate) $250, Cleaning, maintenance, repairs (estimate) $400, Marketing incl. free first visits (estimate) $700, Bookkeeping and accounting (estimate) $250, Licenses and misc (estimate) $150, Membership 30-day guarantee refunds (estimate) $50, Admissions and amusement tax, ~4.5% of admissions (rate to confirm) $580).

- **Break-even: 30 family visits a day.** Below that you lose money every month.
- **Profit margin at your plan** (38 a day): **18%** of every sale, after every cost.
- Capacity: 65 a day.

## Year 1, month by month

| month | family visits a day | revenue | profit | cumulative (after $221,500 startup) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 15 | $8,120 | -$6,540 | -$228,040 |
| 2 | 19 | $10,285 | -$4,767 | -$232,808 |
| 3 | 23 | $12,450 | -$2,994 | -$235,802 |
| 4 | 26 | $14,074 | -$1,664 | -$237,466 |
| 5 | 28 | $15,157 | -$778 | -$238,244 |
| 6 | 30 | $16,240 | $109 | -$238,135 |
| 7 | 32 | $17,322 | $996 | -$237,139 |
| 8 | 33 | $17,864 | $1,439 | -$235,700 |
| 9 | 34 | $18,405 | $1,882 | -$233,818 |
| 10 | 35 | $18,946 | $2,326 | -$231,492 |
| 11 | 36 | $19,488 | $2,769 | -$228,724 |
| 12 | 37 | $20,029 | $3,212 | -$225,512 |

- **Year 1 operating profit: -$4,012** on $188,379 of revenue.
- After the $221,500 startup spend: -$225,512.
- Startup money earned back: not within year 1.
- Cash you need before it pays for itself: **$238,244**.

## What if

| scenario | margin at plan | break-even a day | year 1 profit |
| --- | ---: | ---: | ---: |
| Base plan | 18% | 30 | -$4,012 |
| Price -10% | 9% | 34 | -$22,850 |
| Volume -20% | 2% | 30 | -$34,865 |
| Unit costs +15% | 15% | 31 | -$9,128 |

## Red flags

- Year 1 loses money on operations (-$4,012).
- The startup spend is not earned back within year 1.
