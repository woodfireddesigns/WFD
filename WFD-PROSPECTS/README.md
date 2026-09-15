# WFD Prospects

Finds YouTube channels with a real audience sitting on top of a store nobody
designed, scores them, and writes them to Supabase.

The thesis: building an audience and running a commercial operation are
unrelated skills. A 100k-1M subscriber craft channel earns a few thousand a
month from AdSense while the same audience could support a real product
business. That gap is exactly the WFD stack: brand, packaging, product
photography, storefront, ads.

## Setup

1. Go to console.cloud.google.com, enable **YouTube Data API v3**, create an API key.
2. `export YT_API_KEY=your_key`

That's it. Stdlib only, no pip install.

## Run

```bash
python3 find_prospects.py --dry            # print, write nothing
python3 find_prospects.py aquarium knives  # two niches
python3 find_prospects.py                  # all 18
```

A full run costs about 5,600 of the 10,000 free daily quota units.

## Scoring

Higher score means a real audience plus a gap you can close visibly in one image.

| Signal | Points |
|---|---|
| 100k-1M subscribers | +30 |
| 50k-100k subscribers | +18 |
| Posted in last 30 days | +20 |
| Dormant over 90 days | -15 |
| No store, Linktree, or Amazon links only | +30 |
| Squarespace, Wix, Big Cartel, Etsy | +22 |
| Shopify with 8 products or fewer | +18 |
| Over 60 lifetime views per subscriber | +10 |

Anything above 70 is worth a brand board. Above 85 is worth a phone call.

## Working the list

```sql
select channel_title, subscribers, platform, store_url, score, score_notes
from fin_prospects
where status = 'new' and score >= 70
order by score desc limit 25;
```

Move one along as you work it:

```sql
select fin_prospect_set_status('<uuid>', 'board_sent', 'Sent the four-panel board');
```

Statuses: new, shortlist, board_sent, replied, call_booked, won, dead.

## Tuning it

`NICHES` at the top of the script is the whole game. Add verticals you actually
want to work in. Three or four search terms each is plenty. Narrow craft terms
beat broad category terms: "bladesmith" finds better candidates than "knives".
