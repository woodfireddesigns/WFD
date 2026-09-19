/**
 * Minimal Firecrawl v2 client. No SDK, no deps - just fetch + retries.
 * Docs: https://docs.firecrawl.dev/api-reference/endpoint/scrape
 */

const BASE = (process.env.FIRECRAWL_BASE_URL || 'https://api.firecrawl.dev').replace(/\/$/, '');
const PROXY = process.env.FIRECRAWL_PROXY || 'stealth';
const WAIT_FOR = Number(process.env.FIRECRAWL_WAIT_FOR || 6000);

export class FirecrawlError extends Error {
  constructor(message, { status, body } = {}) {
    super(message);
    this.name = 'FirecrawlError';
    this.status = status;
    this.body = body;
  }
}

export function hasKey() {
  return Boolean(process.env.FIRECRAWL_API_KEY);
}

export function key() {
  const k = process.env.FIRECRAWL_API_KEY;
  if (!k) {
    throw new FirecrawlError(
      'FIRECRAWL_API_KEY is not set. Copy .env.example to .env and add your key, or export it in your shell.'
    );
  }
  return k;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function request(path, body, { retries = 3, timeoutMs = 180000 } = {}) {
  const auth = `Bearer ${key()}`; // throws up front - a missing key is not worth retrying
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(`${BASE}${path}`, {
        method: 'POST',
        headers: {
          Authorization: auth,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      const text = await res.text();
      let json;
      try {
        json = text ? JSON.parse(text) : {};
      } catch {
        json = { raw: text };
      }

      if (res.ok && json.success !== false) return json;

      // 402 = out of credits, 401 = bad key. Retrying those is pointless.
      if (res.status === 401 || res.status === 402 || res.status === 403) {
        throw new FirecrawlError(
          `Firecrawl ${res.status}: ${json.error || json.details || text.slice(0, 300)}`,
          { status: res.status, body: json }
        );
      }

      lastErr = new FirecrawlError(
        `Firecrawl ${res.status}: ${json.error || json.details || text.slice(0, 300)}`,
        { status: res.status, body: json }
      );
    } catch (err) {
      if (err instanceof FirecrawlError && [401, 402, 403].includes(err.status)) throw err;
      lastErr = err;
    } finally {
      clearTimeout(timer);
    }

    if (attempt < retries) await sleep(2000 * 2 ** attempt); // 2s, 4s, 8s
  }
  throw lastErr;
}

/**
 * Scrape a URL and have Firecrawl's extractor return structured JSON against a schema.
 * Returns { json, markdown, statusCode, url }.
 */
export async function scrapeJson(url, { schema, prompt, waitFor = WAIT_FOR, proxy = PROXY, formats = [] } = {}) {
  const body = {
    url,
    formats: [{ type: 'json', prompt, schema }, ...formats],
    onlyMainContent: true,
    waitFor,
    proxy,
    blockAds: true,
    removeBase64Images: true,
    maxAge: 0, // always fetch live; job boards go stale in minutes
  };
  const res = await request('/v2/scrape', body);
  const data = res.data || {};
  return {
    json: data.json || null,
    markdown: data.markdown || '',
    statusCode: data.metadata?.statusCode,
    url: data.metadata?.sourceURL || url,
  };
}

/**
 * Firecrawl web search. Used as the fallback discovery path when Upwork's own
 * search page is blocked - Google/Bing indexes plenty of public Upwork job URLs.
 */
export async function search(query, { limit = 20, tbs } = {}) {
  const res = await request('/v2/search', {
    query,
    limit,
    sources: ['web'],
    ...(tbs ? { tbs } : {}),
  });
  return res.data?.web || [];
}
