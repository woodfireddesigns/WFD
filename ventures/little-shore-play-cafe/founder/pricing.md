# Pricing: Little Shore Play Cafe

Sources: the 100-buyer panel (`panel/answers`), the 20-buyer re-test (`panel-v2/answers`), `competitors.md`, and the CFO tool runs in `cfo.md`. Simulated price answers pick what to test. They are not proof.

## What buyers said

The four price questions were not tied to one item, so buyers split: 69 answered for the monthly membership and 31 for a single visit. Each group was run through `van_westendorp.py` separately (`pricing-curve-membership.md`, `pricing-curve-dropin.md`).

| item | PMC (too cheap below) | OPP | IPP | PME (too expensive above) | as pitched |
| --- | ---: | ---: | ---: | ---: | --- |
| Monthly membership (69 buyers) | $19.97 | $25.14 | $35.13 | **$55.11** | $59: **above the range** |
| Single drop-in (31 buyers) | $5.04 | $6.06 | $9.04 | **$14.99** | $12: inside, but... |
| Drop-in re-test, $14 with coffee (20 buyers) | $6.04 | $6.05 | $10.03 | **$15.97** | $14: inside |

**The hidden problem with the $12 drop-in.** The pitch said "$12, plus one drink per adult." Many buyers read that as a drink *included* and called $12 fair on that basis (P045, P047, P056, P087, P097). The real out-the-door cost is $12 plus a ~$4.75 drink, about **$16.75, above the panel's $15 ceiling**. Folding a house coffee into a $14 drop-in costs about $0.60 a visit and lands inside the range.

## What competitors charge

From `competitors.md` (search excerpts, re-check live pages before relying on them):

- Drop-in, 1 child, local and regional paid options: $5 (Galaxy, 1 hr) to $22.95 (Ocean's Playhouse), **median $18**. CoCo's $20, Altitude $22.94. Small-metro play cafes: $12 to $15.
- Membership: local "unlimited" passes are $15 to $20/month (CoCo's, third-party figure; Altitude). Small-metro play-cafe benchmarks $39.99 to $60, **median ~$40**.
- 2-hour party: $225 to $600, **median $475**.

## What the business needs

From the CFO tool at the recommended offer (with the ops cost corrections): each family visit brings $20.82 and leaves $17.05 after its own costs. Break-even is 30 paying family visits a day. A $1 drop-in increase (to $15, pack to $60) moves Year 1 from a $4,012 loss to a $3,408 profit and break-even to 29 a day. Price alone does not fix this business; volume does.

## The decision

### 1. The price

| item | price | why |
| --- | --- | --- |
| **First visit** | **Free** | 53 of 100 buyers named a free or cheap trial as what would flip them. Weekday capacity is empty anyway; the marginal cost is about $1.10 (coffee + supplies). |
| **Drop-in** | **$14, house coffee or tea included.** Siblings $7. Under 1 free. | Inside both panel ranges, $4 under the local median, removes the "drink minimum" friction. Paid upgrades (lattes, snacks) on top. |
| **5-visit pack** | **$55 ($11 a visit)**, valid 6 months, coffee included | 27 buyers asked for a punch card or visit pack. It is the bridge between a one-off visit and a membership. |
| **Membership** | **$45/month**, unlimited, month to month. **Founding: $39, locked 12 months, first 50 families.** +$15 per sibling. | Inside the range ($20 to $55), above the indifference point ($35), at the small-metro median. $59 was above the range and 3x local "unlimited" passes. |
| **Parties** | **Basic $295** (12 kids), **Premium $395** (20 kids + cafe platter). All-in: no auto-gratuity, no card fee. Cut Deluxe in Year 1. | Well under the $475 local median, and "all-in" answers the surprise-fee complaints found at Altitude and CoCo's. Two tiers, per the board's Product lens. |
| **Group Mornings** | **$8 a child**, weekdays, 4+ families together | 19 buyers asked for a moms-group rate. Fills slow weekday mornings, which the founders' own model says lose money. |

### 2. The ladder

Free first visit → $14 drop-in → $55 five-pack → $45 membership. Each rung pays for itself against the one below: the pack saves $15 over five drop-ins, and the membership beats the pack at the fifth visit in a month. The step-up pitch at the counter is one sentence: "If you come four or more times a month, the membership is cheaper."

### 3. The opening offer

Founding Family membership at $39, locked for 12 months, **first 50 families or opening day, whichever comes first.** Both limits are true. No "was $59" anchor: $59 was never charged and is not used anywhere.

### 4. What to test with real buyers (at the pop-ups)

| test | how | success line |
| --- | --- | --- |
| Drop-in $14 with coffee vs $12 + drink minimum | Alternate pop-up days; same signage otherwise | Paid conversion of free-visit families within 30 days |
| Founding membership $39 vs $45 | Two refundable-deposit links, split by pop-up date | 50 deposits total; compare deposit rate per 100 visitors |

### 5. The panel's price objections, verbatim (for marketing to answer)

- "$59 a month is a lot on $37k, and the library storytime I already go to is free." (P002)
- "I only really have Saturdays with my kid, so an unlimited membership would get maybe 4 uses a month, and at that rate drop-in at $12 is cheaper than $59." (P003)
- "We stick to free stuff like storytime, parks and church groups, and we'd maybe go once or twice a month. That doesn't come close to justifying $59 a month." (P026)

Panel quotes are research. Never use them as testimonials.

## Final pricing (after the Year 1 optimization, Oct 8, 2026)

This supersedes the table above. Evidence: rounds 1 to 4 and the final 100-buyer panel (`optimization.md`).

| item | price | evidence |
| --- | --- | --- |
| First visit | Free | Top flip request in every round |
| Drop-in | **Weekdays $13, weekends $15**, coffee included; siblings $7; under 1 free | Combined price ceiling across 180 answers is $14.99; weekday price lifted buyers (round 3B) and ~70% of visits are weekdays |
| 5-visit pack | **$60**, any day | $12 a visit, below the weekday price so the step up is obvious |
| Membership | $45 unlimited (+$15 sibling); $39 founding, first 50 | Unchanged; a retention product for weekly families |
| Parties | **$325** (12 kids) / **$395** (20 kids), all-in | Party panel range $151 to $400 |
| Classes | $12, teacher-led, 50% to the teacher | 11% would take one |
| Monday private rental | $200 | 2% interested: offer it, do not count on it |
