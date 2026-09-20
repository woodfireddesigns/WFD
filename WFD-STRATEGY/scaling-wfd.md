# Scaling Wood Fired Designs

Working document. September 2026. Written to stand alone, so nothing here assumes
prior context.

---

## What Wood Fired Designs is

Undrafted Designs, LLC, DBA Wood Fired Designs. One person, Michael Deschenes,
operating since 2014 out of Salisbury, Maryland. Sixty-plus brand systems shipped
across food and CPG, apparel, hospitality and sports. Creative credits include the
Masters Tournament, the US Open and American Needle.

The work spans brand identity, packaging with print-ready dielines, AI product
photography, Shopify and Framer builds, and paid and organic ad creative.

The stack is Figma, Framer, Shopify, Google AI Studio, Higgsfield, Nano Banana,
Kling, plus Apify and Firecrawl for prospecting and Instantly for outbound.

**The delivery advantage:** a full brand system, packaging, storefront and ad set
that an agency scopes at four months runs closer to thirty working hours here. AI
handles volume, design judgment handles selection. That speed is margin, not a
discount, and it is the entire economic basis for everything below.

---

## The actual problem, stated correctly

It is tempting to call this an income problem. It is not.

| | Monthly |
|---|---|
| Recurring bills | $7,750 |
| Groceries, gas, household | $2,090 |
| **Total burn** | **$9,840** |
| **Average household income** | **$9,857** |

Break-even. On average, to within twenty dollars.

The trouble is that "on average" does not pay a mortgage. Business revenue was
$8,993 in July and $4,158 in August. One month covers everything with room to
spare, the next month is $5,700 short, and there is no buffer to bridge the
difference. The shortfall becomes arrears, the arrears attract late fees, and the
next good month goes to paying off the last bad one instead of building reserve.

**The problem is variance, not volume.** Scaling is therefore not primarily about
earning more. It is about converting lumpy project revenue into a predictable floor,
and only then adding margin on top.

Confirmed recurring income today is about $6,529 a month. Everything above that is
project work that arrives when it arrives.

---

## The target that actually matters

Not $20,000 a month. Not yet.

**$10,000 a month in retainer revenue.**

That single number covers the entire household burn from the floor alone. Every
project fee on top of it becomes surplus: tax reserve, arrears payoff, then savings.
The variance problem disappears the day that floor exists, and it never comes back.

Three Studio-tier clients at $3,500 gets there. Three.

The $20,000 figure is the next milestone after that, reached by six clients mixed
across tiers in roughly seventy working hours a month. Worth aiming at. Not worth
planning around while the floor is still missing.

---

## Why the ceiling is $1,200 and how to break it

A "website maintenance plan" gets compared to a $99 WordPress care plan, because
that is the nearest thing a buyer can price it against. That comparison caps the
category near $1,200 a month no matter how good the work is.

This is a category problem, not a value problem. The same hours sold under a
different heading price at three times as much.

The fix is to sell an outsourced creative department: a countable stack of monthly
output that the client can price against the agency quote already sitting in their
drawer.

Three tiers, always presented together, because a single price invites yes or no
while three prices invite a choice and the choice is almost always the middle:

| Tier | Monthly | Hours | Effective rate |
|---|---|---|---|
| Foundation | $1,500 | ~5 | $300/hr |
| **Studio** | **$3,500** | **~12** | **$292/hr** |
| Partner | $6,500 | ~20 | $325/hr |

Full deliverable lists and the comparison table that justifies Studio at $3,500 are
in `WFD-PROSPECTS/retainer-packages.md`.

---

## The growth engine

### Adapting the Rule of 100

The premise of the Rule of 100 is a hundred days of a hundred daily units of
outreach, done without negotiation. Applied literally to a design business it
produces a hundred cold emails a day, which is the wrong unit entirely. Volume
outreach sells a commodity, and the whole point here is to escape a commodity
category.

The right unit is the one thing nobody else can afford to give away.

### One Brand a Day

Every working day, pick one brand with a good product and weak presentation, and
build a complete unsolicited rebuild. Four panels:

1. Repositioned packaging
2. A product shot
3. An ad frame
4. A storefront section

Send it with no ask attached. No pitch, no rate card, no call to action.

A critique triggers defensiveness. A rebuild triggers desire, and it demonstrates
the entire offer in a single image. It also proves the delivery speed without
claiming it, which is worth more than any case study.

One a day for a hundred days is a hundred brands that have seen exactly what working
with WFD looks like, and a hundred pieces of portfolio that cost nothing extra to
produce because they were made to be sent.

**Why this works here and would not work for an agency:** at thirty hours for a full
engagement, a four-panel rebuild is an afternoon. An agency would have to bill that
afternoon. WFD can spend it as marketing.

---

## Where retainer clients come from

Ranked by speed to close.

1. **The back catalogue.** Sixty-plus brands already shipped. Warmest list available,
   and none of them have ever been sent a retainer offer. This is the single most
   underworked asset in the business.
2. **Live and recent clients.** Upgrade conversations at handover.
3. **Project-to-retainer conversion.** Built into every proposal from day one.
4. **Referrals** from happy retainer clients and adjacent professional services.
5. **Cold, qualified.** Brands with a good product and mediocre packaging that are
   already spending on paid. The bad packaging is the qualifier, because it is a
   problem that can be visibly solved in one image.

---

## The cold-outreach thesis

Building an audience and running a commercial operation are unrelated skills.

A creator with 100,000 to 1,000,000 subscribers in a craft niche has spent years
earning trust in a specific vertical, and frequently monetizes it through AdSense
and a storefront nobody has touched since 2014. The audience would support a real
product business. The presentation is the only thing in the way.

That gap is precisely the WFD stack: brand, packaging, product photography,
storefront, ads. And it is visible from the outside, which makes it qualifiable at
scale without a conversation.

A stdlib-only prospecting script lives in `WFD-PROSPECTS/find_prospects.py`. It
searches YouTube across twenty-one craft verticals, finds each channel's store,
detects the platform and catalogue size, and scores the gap.

The scoring rewards exactly the shape described above:

| Signal | Points |
|---|---|
| 100k to 1M subscribers | +30 |
| No store, Linktree, or Amazon links only | +30 |
| Squarespace, Wix, Big Cartel, Etsy | +22 |
| Posted in last 30 days | +20 |
| Shopify with 8 products or fewer | +18 |
| Over 60 lifetime views per subscriber | +10 |
| Dormant over 90 days | -15 |

Above 70 earns a four-panel board. Above 85 earns a phone call.

The niche list at the top of the script is the whole game. Narrow craft terms beat
category terms, because "bladesmith" finds makers while "knives" finds reviewers.

---

## Repositioning the portfolio

The current portfolio sells projects. Retainer buyers are asking a different
question, and the site should answer it.

**What a project buyer wants to know:** can you make something beautiful?

**What a retainer buyer wants to know:** can you keep making things, on schedule,
without me managing you?

Four changes that follow from that:

1. **Lead with systems, not artifacts.** A single logo proves taste. A brand running
   consistently across a bottle, a product page, an ad and a storefront proves the
   thing a retainer actually buys.
2. **Show volume.** Fifteen ad creatives from one month says more about monthly
   capacity than any single hero image.
3. **Show before and after.** The transformation is the product. A rebuild sitting
   next to what it replaced does the selling without copy.
4. **Name the retainer on the site.** If the offer is not visible, every retainer
   conversation has to start from scratch in the sales call.

Case study highlight reels, roughly three minutes each, are the strongest version of
all four at once. They require motion work and a local editing setup.

---

## Sequencing

Order matters more than effort here. Working the list out of order wastes the best
opportunities on the least prepared version of the offer.

**Now, this week**

- Sell the retainer at every handover currently in reach. Handover is the highest
  conversion moment in any engagement and it does not come back. Every week after,
  the relationship cools and the ask gets harder.
- Add a priced post-launch phase to every open proposal, so no project ends at
  go-live with the retainer unsold.

**Next 30 days**

- Work the back catalogue. Sixty warm brands, none of whom have been offered a
  retainer. Even a low response rate on the warmest list available beats cold.
- Get to three Studio clients, or the equivalent mix. That is the $10,000 floor.

**Next 90 days**

- Start One Brand a Day and do not negotiate with it.
- Run the prospecting script, work the shortlist above 70.
- Rebuild the portfolio around systems, volume and transformation.

**After the floor exists**

- Raise the entry tier. Nothing below $1,500.
- Build the case study reels.
- Six clients, $20,000, roughly seventy hours a month.

---

## Rules that protect the model

**Never quote one number.** Three tiers, always.

**Sell inside the project, not after it.** A proposal that ends at go-live means
selling the same client again cold in ninety days.

**Three-month minimum, then month to month.** Long enough to show results, short
enough that nobody has to think hard about signing.

**Count the deliverables out loud.** "Fifteen creatives, two campaigns, a landing
page" is checkable. "Ongoing creative support" is not, and unpriceable things get
priced low.

**Nothing below $1,500.** A $600 client expects the same responsiveness as a $3,500
one and occupies the same emotional space.

**Price projects on outcome, never hours.** A fixed-price engagement delivered in
thirty hours at $14,500 is an effective rate near $480. Quoting hours gives that
away.

---

## What could break this

Worth stating plainly, because a plan that only lists upside is a pitch, not a plan.

**Cash pressure forces bad pricing.** The month you most need a client is the month
you are most likely to discount to close one. A discounted retainer is not a bridge,
it is a permanent reset of what that client believes the work costs. This is the
single biggest risk to the whole model and it is entirely internal.

**One Brand a Day dies in week three.** Daily unpaid creative work is the first thing
to fall off when paid work spikes. The discipline is the product. A hundred days at
four a week beats twenty days at one a day and then nothing.

**Retainers become scope-creep jobs.** Countable deliverables are what prevent this.
The moment a retainer becomes "whatever they ask for," the effective rate collapses
and it stops being a business.

**Delivery capacity is one person.** Six retainers at seventy hours a month is
achievable. Twelve is not, not without either subcontractors or a productized tier
that genuinely does not scale with client count. That decision can wait, but it
cannot be skipped forever.

**Tax reserve stays at zero.** Running with no reserve is what turned a variance
problem into an arrears problem in the first place. The first surplus month funds
the reserve before it funds anything else.

---

## The one-sentence version

Wood Fired Designs is break-even on average with no buffer, so the job is not to earn
more but to convert lumpy project revenue into a $10,000 monthly retainer floor, sold
under a category that prices at three times "website maintenance," proven by giving
away the one thing thirty-hour delivery makes affordable to give away.
