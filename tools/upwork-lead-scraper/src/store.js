/**
 * Flat-file JSON store. Dedupes by Upwork job id so a job posted once never
 * shows up in two digests. Swap this for Supabase/Notion later if volume grows.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const DATA_DIR = path.join(ROOT, 'data');
const STORE_PATH = path.join(DATA_DIR, 'jobs.json');

export function load() {
  if (!fs.existsSync(STORE_PATH)) return { jobs: {}, lastRunAt: null };
  try {
    return JSON.parse(fs.readFileSync(STORE_PATH, 'utf8'));
  } catch {
    return { jobs: {}, lastRunAt: null };
  }
}

export function save(state) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(STORE_PATH, JSON.stringify(state, null, 2));
}

/** Returns { fresh, seen } - fresh being jobs never stored before. */
export function split(state, jobs) {
  const fresh = [];
  const seen = [];
  for (const job of jobs) {
    if (!job.id || !job.url) continue;
    (state.jobs[job.id] ? seen : fresh).push(job);
  }
  return { fresh, seen };
}

export function commit(state, jobs) {
  for (const job of jobs) {
    if (!job.id) continue;
    const prev = state.jobs[job.id];
    state.jobs[job.id] = { ...prev, ...job, firstSeenAt: prev?.firstSeenAt || job.firstSeenAt };
  }
  state.lastRunAt = new Date().toISOString();
  return state;
}

/** Drop anything older than N days so the file doesn't grow forever. */
export function prune(state, days = 45) {
  const cutoff = Date.now() - days * 864e5;
  for (const [id, job] of Object.entries(state.jobs)) {
    if (new Date(job.firstSeenAt || 0).getTime() < cutoff) delete state.jobs[id];
  }
  return state;
}
