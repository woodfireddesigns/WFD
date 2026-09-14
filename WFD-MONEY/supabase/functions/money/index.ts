// WFD Money: serves the static app from the GitHub branch. Open access by design (no login for now).
// Assets are fetched from raw.githubusercontent.com and cached in memory per isolate for 60s.
const REPO = "woodfireddesigns/WFD";
const BRANCH = "claude/financial-tracking-advice-7y0c7e";
const DIR = "WFD-MONEY";
const TYPES: Record<string, string> = {
  "/index.html": "text/html; charset=utf-8",
  "/app.js": "text/javascript; charset=utf-8",
  "/logic.js": "text/javascript; charset=utf-8",
  "/sw.js": "text/javascript; charset=utf-8",
  "/styles.css": "text/css; charset=utf-8",
  "/manifest.webmanifest": "application/manifest+json",
  "/icons/icon-192.png": "image/png",
  "/icons/icon-512.png": "image/png",
  "/icons/apple-touch-icon.png": "image/png",
};
const TTL_MS = 60_000;
const cache = new Map<string, { body: ArrayBuffer; at: number }>();

async function load(path: string): Promise<ArrayBuffer | null> {
  const hit = cache.get(path);
  if (hit && Date.now() - hit.at < TTL_MS) return hit.body;
  const src = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${DIR}${path}`;
  const r = await fetch(src, { headers: { "User-Agent": "wfd-money-edge" } });
  if (!r.ok) return hit ? hit.body : null;
  const body = await r.arrayBuffer();
  cache.set(path, { body, at: Date.now() });
  return body;
}

Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  // path after the function name: /functions/v1/money/app.js -> /app.js
  const m = url.pathname.match(/^\/(?:functions\/v1\/)?money(\/.*)?$/);
  let rest = m ? (m[1] || "") : "";
  if (rest === "") return Response.redirect(url.origin + url.pathname + "/" + url.search, 302);
  if (rest === "/") rest = "/index.html";
  const type = TYPES[rest];
  if (!type || (req.method !== "GET" && req.method !== "HEAD")) return new Response("Not found", { status: 404 });
  const body = await load(rest);
  if (!body) return new Response("Upstream unavailable", { status: 502 });
  const isImage = type === "image/png";
  return new Response(req.method === "HEAD" ? null : body, {
    headers: {
      "Content-Type": type,
      "Cache-Control": isImage ? "public, max-age=86400" : "no-cache",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "Referrer-Policy": "strict-origin-when-cross-origin",
    },
  });
});
