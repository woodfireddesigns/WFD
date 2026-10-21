// Step sync endpoint. The iPhone "Kiln Steps" shortcut writes today's total here on a schedule;
// Kiln reads it on open. Each device's data lives at a path derived from its secret sync key.
import { put, head } from '@vercel/blob';
import { createHash } from 'node:crypto';

const KEY_RE = /^[A-Za-z0-9_-]{24,64}$/;
const pathFor = k => `steps/${createHash('sha256').update(k).digest('hex')}.json`;

function localDay(tz) {
  try {
    return new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

async function load(path) {
  try {
    const h = await head(path);
    const r = await fetch(`${h.url}?v=${Date.now()}`, { cache: 'no-store' });
    if (r.ok) return await r.json();
  } catch { /* first write for this key */ }
  return { days: {}, updated: 0 };
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const q = req.query || {};
  const k = String(q.k || '');
  if (!KEY_RE.test(k)) return res.status(401).json({ error: 'Missing or invalid sync key' });
  const path = pathFor(k);
  const data = await load(path);

  // read
  if (q.n == null || q.n === '') return res.status(200).json(data);

  // write: n = step total, d = optional YYYY-MM-DD, tz = IANA zone used to pick "today"
  const n = Math.round(parseFloat(String(q.n).replace(/[^0-9.]/g, '')));
  if (!Number.isFinite(n) || n < 0 || n > 200000) return res.status(400).json({ error: 'Steps must be a number' });
  const day = /^\d{4}-\d{2}-\d{2}$/.test(String(q.d || '')) ? String(q.d) : localDay(String(q.tz || 'America/New_York'));
  data.days[day] = n;
  data.updated = Date.now();
  const keys = Object.keys(data.days).sort();
  while (keys.length > 400) delete data.days[keys.shift()];
  await put(path, JSON.stringify(data), {
    access: 'public', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json', cacheControlMaxAge: 60,
  });
  return res.status(200).send(`Kiln saved ${n.toLocaleString('en-US')} steps for ${day}`);
}
