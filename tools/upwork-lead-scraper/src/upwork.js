/**
 * Upwork URL building + Firecrawl extraction schemas + normalization.
 */

import { scrapeJson, search as webSearch } from './firecrawl.js';

const TIER_CODES = { entry: 1, intermediate: 2, expert: 3 };

/** Build an Upwork public job-search URL from a search config entry. */
export function buildSearchUrl(searchCfg, page = 1) {
  const f = searchCfg.filters || {};
  const params = new URLSearchParams();
  params.set('q', searchCfg.q);
  params.set('sort', searchCfg.sort || 'recency');
  if (f.paymentVerified) params.set('payment_verified', '1');
  if (f.tiers?.length) {
    params.set('contractor_tier', f.tiers.map((t) => TIER_CODES[t] || t).join(','));
  }
  // t=0 hourly, t=1 fixed. Default to both.
  params.set('t', f.contractType === 'hourly' ? '0' : f.contractType === 'fixed' ? '1' : '0,1');
  if (f.fixedMin) params.set('amount', `${f.fixedMin}-`);
  if (f.hourlyMin) params.set('hourly_rate', `${f.hourlyMin}-`);
  if (f.location) params.set('location', f.location);
  if (page > 1) params.set('page', String(page));
  return `https://www.upwork.com/nx/search/jobs/?${params.toString()}`;
}

const JOB_FIELDS = {
  title: { type: 'string' },
  url: { type: 'string', description: 'Absolute URL to the job posting on upwork.com' },
  description: { type: 'string', description: 'The job description text as shown on the card or page' },
  postedRelative: { type: 'string', description: 'Relative posted time exactly as shown, e.g. "3 hours ago", "yesterday"' },
  contractType: { type: 'string', description: 'Either "hourly" or "fixed"' },
  fixedBudget: { type: 'number', description: 'Fixed-price budget in USD, null if hourly' },
  hourlyMin: { type: 'number', description: 'Low end of hourly range in USD, null if fixed price' },
  hourlyMax: { type: 'number', description: 'High end of hourly range in USD, null if fixed price' },
  experienceLevel: { type: 'string', description: 'Entry level, Intermediate, or Expert' },
  estimatedDuration: { type: 'string', description: 'Expected contract length exactly as shown, e.g. "More than 6 months", "1 to 3 months"' },
  workload: { type: 'string', description: 'Expected weekly commitment as shown, e.g. "Less than 30 hrs/week"' },
  clientHires: { type: 'number', description: 'Number of people this client has hired on Upwork before' },
  proposals: { type: 'number', description: 'Number of proposals submitted. If shown as a range like "5 to 10", use the low number' },
  paymentVerified: { type: 'boolean' },
  clientCountry: { type: 'string' },
  clientSpend: { type: 'number', description: 'Total client spend in USD, e.g. "$20K+ spent" becomes 20000' },
  clientRating: { type: 'number', description: 'Client star rating out of 5' },
  skills: { type: 'array', items: { type: 'string' } },
};

export const SEARCH_SCHEMA = {
  type: 'object',
  properties: {
    jobs: {
      type: 'array',
      items: { type: 'object', properties: JOB_FIELDS, required: ['title', 'url'] },
    },
  },
  required: ['jobs'],
};

export const JOB_SCHEMA = {
  type: 'object',
  properties: {
    ...JOB_FIELDS,
    clientHireRate: { type: 'string' },
    clientMemberSince: { type: 'string' },
    connectsRequired: { type: 'number' },
    questions: { type: 'array', items: { type: 'string' }, description: 'Screening questions the client asks applicants' },
  },
};

const SEARCH_PROMPT = `Extract every job posting card on this Upwork search results page.
For each card capture the title, the absolute job URL, the full visible description snippet,
the posted time exactly as displayed, contract type, budget or hourly range, experience level,
expected contract duration, expected weekly hours, number of proposals, whether the client's
payment method is verified, the client's country, total client spend, client rating, how many
people the client has hired before, and the listed skill tags.
Return an empty jobs array if the page shows a login wall, a captcha, or no results.`;

const JOB_PROMPT = `Extract the full details of this single Upwork job posting. Capture the COMPLETE
job description text verbatim, the budget, expected contract duration and weekly hours, the client's
full hiring history (total spend, number of hires, hire rate, member since), every screening question,
and the required connects. The full description matters most - long-term and ongoing intent is usually
buried in the last paragraph.`;

/** Pull one page of Upwork search results. */
export async function scrapeSearchPage(searchCfg, page = 1) {
  const url = buildSearchUrl(searchCfg, page);
  const res = await scrapeJson(url, { schema: SEARCH_SCHEMA, prompt: SEARCH_PROMPT });
  const jobs = Array.isArray(res.json?.jobs) ? res.json.jobs : [];
  return {
    url,
    statusCode: res.statusCode,
    blocked: isBlocked(res),
    jobs: jobs.map((j) => normalizeJob(j, searchCfg.id)),
  };
}

/** Pull one full job detail page (used to enrich high scorers). */
export async function scrapeJobDetail(jobUrl) {
  const res = await scrapeJson(jobUrl, { schema: JOB_SCHEMA, prompt: JOB_PROMPT });
  if (!res.json) return null;
  return normalizeJob({ ...res.json, url: res.json.url || jobUrl }, null);
}

/**
 * Fallback discovery: search the open web for indexed Upwork job URLs.
 * Lower yield and staler than the on-site search, but it works when
 * Upwork's search page throws a login wall.
 */
export async function discoverViaWebSearch(query, { limit = 20 } = {}) {
  const results = await webSearch(`site:upwork.com/jobs ${query}`, { limit, tbs: 'qdr:w' });
  return results
    .filter((r) => /upwork\.com\/(jobs|freelance-jobs)/.test(r.url || ''))
    .map((r) =>
      normalizeJob(
        { title: r.title, url: r.url, description: r.description || '' },
        'web-search'
      )
    );
}

function isBlocked(res) {
  const md = (res.markdown || '').toLowerCase();
  if (res.statusCode && res.statusCode >= 400) return true;
  return (
    md.includes('verify you are human') ||
    md.includes('access denied') ||
    md.includes('cf-browser-verification') ||
    (md.includes('log in') && md.includes('sign up') && md.length < 2500)
  );
}

/** Pull the ~0... posting id out of an Upwork job URL. Stable dedupe key. */
export function jobId(url = '') {
  const m = String(url).match(/~[0-9a-z]{10,}/i);
  if (m) return m[0];
  try {
    return new URL(url, 'https://www.upwork.com').pathname;
  } catch {
    return url;
  }
}

/** Convert "3 hours ago" / "yesterday" / "2 days ago" into hours. */
export function relativeToHours(rel) {
  if (!rel) return null;
  const s = String(rel).toLowerCase().trim();
  if (s.includes('just now') || s.includes('minute')) {
    const n = parseInt(s, 10);
    return Number.isFinite(n) ? n / 60 : 0.1;
  }
  if (s.includes('yesterday')) return 24;
  const n = parseFloat(s.replace(/[^0-9.]/g, ''));
  if (!Number.isFinite(n)) return null;
  if (s.includes('hour')) return n;
  if (s.includes('day')) return n * 24;
  if (s.includes('week')) return n * 168;
  if (s.includes('month')) return n * 720;
  return null;
}

export function normalizeJob(raw = {}, sourceId = null) {
  const url = absoluteUrl(raw.url);
  const hourlyMax = num(raw.hourlyMax) ?? num(raw.hourlyMin);
  return {
    id: jobId(url),
    sourceId,
    title: str(raw.title),
    url,
    description: str(raw.description),
    postedRelative: str(raw.postedRelative),
    postedHoursAgo: relativeToHours(raw.postedRelative),
    contractType: normalizeContractType(raw),
    fixedBudget: num(raw.fixedBudget),
    hourlyMin: num(raw.hourlyMin),
    hourlyMax,
    experienceLevel: str(raw.experienceLevel),
    estimatedDuration: str(raw.estimatedDuration),
    workload: str(raw.workload),
    proposals: num(raw.proposals),
    paymentVerified: typeof raw.paymentVerified === 'boolean' ? raw.paymentVerified : null,
    clientCountry: str(raw.clientCountry),
    clientSpend: num(raw.clientSpend),
    clientRating: num(raw.clientRating),
    clientHires: num(raw.clientHires),
    clientHireRate: str(raw.clientHireRate),
    connectsRequired: num(raw.connectsRequired),
    questions: Array.isArray(raw.questions) ? raw.questions.map(str).filter(Boolean) : [],
    skills: Array.isArray(raw.skills) ? raw.skills.map(str).filter(Boolean) : [],
    firstSeenAt: new Date().toISOString(),
  };
}

function normalizeContractType(raw) {
  const t = String(raw.contractType || '').toLowerCase();
  if (t.includes('hour')) return 'hourly';
  if (t.includes('fixed')) return 'fixed';
  if (num(raw.hourlyMin) || num(raw.hourlyMax)) return 'hourly';
  if (num(raw.fixedBudget)) return 'fixed';
  return null;
}

function absoluteUrl(u) {
  if (!u) return '';
  try {
    return new URL(u, 'https://www.upwork.com').toString().split('?')[0];
  } catch {
    return String(u);
  }
}

const str = (v) => (v == null ? '' : String(v).trim());
const num = (v) => {
  if (v == null || v === '') return null;
  const n = typeof v === 'number' ? v : parseFloat(String(v).replace(/[^0-9.]/g, ''));
  return Number.isFinite(n) ? n : null;
};
