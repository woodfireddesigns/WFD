#!/usr/bin/env python3
"""
Finds YouTube channels with a real audience and a weak (or missing) store,
scores them, and writes them to the fin_prospects table in Supabase.

Stdlib only. No pip install, no Apify, no Firecrawl.

Setup (once):
    export YT_API_KEY=...        # console.cloud.google.com -> enable "YouTube Data API v3" -> create API key
    export SUPABASE_KEY=...      # the publishable key already in the money app

Run:
    python3 find_prospects.py                    # every niche in NICHES
    python3 find_prospects.py aquarium welding   # just those
    python3 find_prospects.py --dry              # print, write nothing

Quota: 10,000 units/day free. Searches cost 100 each, everything else costs 1.
A full run over all 21 niches is about 6,000 units, so you can run it twice a day.
"""

import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error
from datetime import date, datetime, timedelta

YT_KEY = os.environ.get("YT_API_KEY", "")
SB_URL = "https://aqeipagwuerfosxdgkie.supabase.co"
SB_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_5xuWTfWdLloVXMWVAmGwZw_ZEk68Qu5")
HOUSEHOLD = "8b825046-dbb8-4d33-8b95-351a1eb05d2c"

# Verticals where deep expertise and a devoted audience routinely sit on top of
# a store nobody has touched since 2014. Add your own; the seeds are the whole game.
NICHES = {
    # Tuned to the work WFD has actually shipped: CPG food and drink, apparel and
    # workwear, outdoor and sporting goods, tabletop and home. Narrow craft terms
    # beat category terms, because "bladesmith" finds makers and "knives" finds reviewers.

    # --- Tabletop and home. The Pitcher & Pour lane. ---
    "tabletop":    ["tablescape styling", "entertaining at home", "handmade ceramics studio"],
    "woodworking": ["woodworking shop", "furniture making", "hand tool woodworking"],
    "leather":     ["leathercraft", "handmade leather goods", "leather workshop"],
    "candles":     ["candle making business", "soy candle studio"],

    # --- Food and drink CPG. Dope Rope, Mad Matcha, Bean & Leaf. ---
    "bbq":         ["bbq smoking", "offset smoker", "competition barbecue"],
    "hotsauce":    ["hot sauce making", "fermented hot sauce", "pepper growing"],
    "coffee":      ["coffee roasting", "specialty coffee brewing"],
    "bees":        ["beekeeping", "honey harvest", "apiary"],
    "homestead":   ["homesteading", "small farm", "canning and preserving"],

    # --- Apparel and workwear. Niam, Western Welder. ---
    "welding":     ["welding projects", "tig welding", "metal fabrication shop"],
    "machining":   ["machine shop", "lathe projects", "cnc shop"],
    "knives":      ["knife making", "forging knives", "bladesmith"],

    # --- Outdoor and sporting. Daddy Caddies, Tactical Tanks, Out of Bounds. ---
    "overland":    ["overlanding build", "truck camper build", "van build"],
    "bushcraft":   ["bushcraft camping", "survival skills", "axe restoration"],
    "archery":     ["traditional archery", "bow making", "bowhunting"],
    "fishing":     ["fly tying", "rod building", "lure making"],
    "golf":        ["golf club fitting", "clubmaking", "golf course vlog"],
    "pickleball":  ["pickleball gear", "pickleball paddle review"],

    # --- Niche hobby with devoted audiences and terrible stores. Father Fish lane. ---
    "aquarium":    ["aquarium setup", "planted tank", "aquascaping"],
    "reptiles":    ["reptile keeping", "bioactive terrarium", "snake breeding"],
    "autorestore": ["car restoration", "engine rebuild", "classic truck build"],
}

# The tell: a great channel pointing at a store that was never designed.
PLATFORM_SIGNS = [
    ("shopify",      [r"cdn\.shopify\.com", r"myshopify\.com", r"Shopify\.theme"]),
    ("squarespace",  [r"squarespace", r"static1\.squarespace\.com"]),
    ("wix",          [r"wix\.com", r"wixstatic"]),
    ("bigcartel",    [r"bigcartel"]),
    ("woocommerce",  [r"woocommerce", r"wp-content/plugins/woo"]),
    ("etsy",         [r"etsy\.com"]),
    ("linktree",     [r"linktr\.ee", r"beacons\.ai", r"stan\.store"]),
    ("amazon_only",  [r"amazon\.com/shop/", r"amzn\.to"]),
]
SKIP_HOSTS = ("youtube.com", "youtu.be", "instagram.com", "facebook.com", "twitter.com",
              "x.com", "tiktok.com", "patreon.com", "discord", "paypal", "venmo")


def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (WFD prospect scan)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def yt(endpoint, **params):
    params["key"] = YT_KEY
    url = "https://www.googleapis.com/youtube/v3/%s?%s" % (endpoint, urllib.parse.urlencode(params))
    try:
        return json.loads(get(url))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:300]
        print("  ! YouTube API %s: %s" % (e.code, body))
        return {}


def search_channels(term, limit=50):
    """Channel ids for one search term. Costs 100 quota units."""
    r = yt("search", part="snippet", type="channel", q=term,
           maxResults=min(limit, 50), relevanceLanguage="en", regionCode="US")
    return [i["snippet"]["channelId"] for i in r.get("items", []) if i.get("snippet")]


def channel_details(ids):
    """Stats for up to 50 channels. Costs 1 quota unit."""
    if not ids:
        return []
    r = yt("channels", part="snippet,statistics,brandingSettings", id=",".join(ids[:50]), maxResults=50)
    out = []
    for c in r.get("items", []):
        st, sn = c.get("statistics", {}), c.get("snippet", {})
        out.append({
            "channel_id": c["id"],
            "channel_title": sn.get("title", ""),
            "channel_url": "https://www.youtube.com/channel/" + c["id"],
            "subscribers": int(st.get("subscriberCount", 0) or 0),
            "video_count": int(st.get("videoCount", 0) or 0),
            "view_count": int(st.get("viewCount", 0) or 0),
            "country": sn.get("country"),
            "description": sn.get("description", "") or "",
        })
    return out


def last_upload(channel_id):
    """Most recent upload date. 1 quota unit, not 100.

    Every channel's uploads playlist is its id with UC swapped for UU, so we can
    hit playlistItems directly instead of paying 100 units for a search call.
    """
    pid = "UU" + channel_id[2:]
    r = yt("playlistItems", part="snippet", playlistId=pid, maxResults=1)
    items = r.get("items", [])
    if not items:
        return None
    return items[0]["snippet"].get("publishedAt", "")[:10] or None


def find_store(description):
    """First plausible store link in the channel's about text."""
    for raw in re.findall(r"https?://[^\s\)\]\",]+", description):
        u = raw.rstrip(".,;")
        host = urllib.parse.urlparse(u).netloc.lower()
        if any(s in host for s in SKIP_HOSTS):
            continue
        return u
    return None


def inspect_store(url):
    """Platform and catalogue size. Never fails the run.

    "unreachable" is deliberately NOT the same as "unknown". A store that times out
    or sits behind a bot wall is a lead to eyeball by hand, not one to silently sink
    to the bottom of the list, which is what happened when both returned "unknown".
    """
    if not url:
        return "none", None
    html = None
    for timeout in (12, 25):                       # one slow retry before giving up
        try:
            html = get(url, timeout=timeout)
            break
        except Exception:
            continue
    if html is None:
        return "unreachable", None

    low = html.lower()
    platform = "custom"
    for name, pats in PLATFORM_SIGNS:
        if any(re.search(p, low) for p in pats):
            platform = name
            break

    # Homepages increasingly render the catalogue in JS, so counting /products/ links
    # in the HTML under-reports badly. Shopify publishes the real list, so ask it.
    if platform == "shopify":
        n = shopify_product_count(url)
        if n is not None:
            return platform, n
    products = len(set(re.findall(r"/products?/([a-z0-9\-]{3,60})", low)))
    return platform, (products or None)


def shopify_product_count(url):
    """Real catalogue size from Shopify's public products.json. None if unavailable."""
    base = "%s://%s" % (urllib.parse.urlparse(url).scheme or "https",
                        urllib.parse.urlparse(url).netloc)
    try:
        data = json.loads(get(base + "/products.json?limit=250", timeout=15))
    except Exception:
        return None
    items = data.get("products")
    return len(items) if isinstance(items, list) else None


def score(p):
    """Higher means: real audience, and a gap you can visibly close in one image."""
    s, why = 0, []
    subs = p["subscribers"]
    if 100_000 <= subs <= 1_000_000:
        s += 30; why.append("audience in the sweet spot")
    elif 50_000 <= subs < 100_000:
        s += 18; why.append("audience building")
    elif subs > 1_000_000:
        s += 8;  why.append("large, likely already represented")
    else:
        why.append("audience too small")

    if p.get("last_upload_on"):
        days = (date.today() - datetime.strptime(p["last_upload_on"], "%Y-%m-%d").date()).days
        if days <= 30:   s += 20; why.append("posting weekly")
        elif days <= 90: s += 12; why.append("still active")
        else:            s -= 15; why.append("gone quiet")

    plat, count = p.get("platform"), p.get("product_count") or 0
    if plat == "unreachable":
        s += 15; why.append("store would not load, check by hand")
    elif plat in ("none", "linktree", "amazon_only"):
        s += 30; why.append("no real store at all")
    elif plat in ("squarespace", "wix", "bigcartel", "etsy"):
        s += 22; why.append("store on a hobbyist platform")
    elif plat == "shopify" and count and count <= 8:
        s += 18; why.append("thin Shopify catalogue")
    elif plat == "shopify":
        s += 8;  why.append("established Shopify")

    if subs and p["view_count"] / max(subs, 1) > 60:
        s += 10; why.append("unusually engaged audience")

    return max(s, 0), "; ".join(why)


def upsert(rows):
    body = json.dumps(rows).encode()
    req = urllib.request.Request(
        SB_URL + "/rest/v1/fin_prospects?on_conflict=channel_id",
        data=body, method="POST",
        headers={"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
                 "Content-Type": "application/json",
                 "Prefer": "resolution=merge-duplicates,return=minimal"})
    try:
        urllib.request.urlopen(req, timeout=25).read()
        return len(rows)
    except urllib.error.HTTPError as e:
        print("  ! Supabase %s: %s" % (e.code, e.read().decode("utf-8", "ignore")[:400]))
        return 0


def run(niches, dry=False):
    if not YT_KEY:
        sys.exit("Set YT_API_KEY first. Enable YouTube Data API v3 at console.cloud.google.com and make a key.")
    seen, keep = set(), []
    for niche in niches:
        terms = NICHES.get(niche, [niche])
        print("\n=== %s ===" % niche)
        ids = []
        for t in terms:
            found = search_channels(t)
            print("  %-34s %d channels" % (t, len(found)))
            ids += [i for i in found if i not in seen]
            seen.update(found)
            time.sleep(0.3)
        for i in range(0, len(ids), 50):
            for ch in channel_details(ids[i:i + 50]):
                if ch["subscribers"] < 50_000 or ch["subscribers"] > 2_000_000:
                    continue
                ch["niche"] = niche
                ch["last_upload_on"] = last_upload(ch["channel_id"])
                ch["store_url"] = find_store(ch.pop("description"))
                ch["platform"], ch["product_count"] = inspect_store(ch["store_url"])
                ch["score"], ch["score_notes"] = score(ch)
                ch["household_id"] = HOUSEHOLD
                keep.append(ch)
                print("  %5d  %-42s %-12s %s" % (ch["score"], ch["channel_title"][:42],
                                                 ch["platform"], ch["store_url"] or "no store"))
                time.sleep(0.2)

    keep.sort(key=lambda x: -x["score"])
    print("\n%d channels kept. Top 15:" % len(keep))
    for p in keep[:15]:
        print("  %3d  %-40s %8s subs  %s" % (p["score"], p["channel_title"][:40],
                                             f'{p["subscribers"]:,}', p["score_notes"]))
    if dry:
        print("\nDry run, nothing written.")
        return
    wrote = 0
    for i in range(0, len(keep), 100):
        wrote += upsert(keep[i:i + 100])
    print("\nWrote %d rows to fin_prospects." % wrote)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    run(args or list(NICHES), dry="--dry" in sys.argv)
