/**
 * Socrates Screen – Cloudflare Worker: TMDB Image Proxy
 *
 * Deploy from the worker/ directory:
 *   cd worker && npx wrangler deploy
 *
 * Purpose:
 *   Indian ISPs (Jio, ACT, BSNL) block image.tmdb.org.
 *   This Worker intercepts requests with a `path` query param and
 *   fetches the image from TMDB, returning it with:
 *     - Long-lived Cache-Control headers (1 year immutable)
 *     - CORS headers so the Vue frontend can load images cross-origin
 *
 * Example request:
 *   GET https://<YOUR_WORKER>.workers.dev/?path=/abc123.jpg
 */

const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500";

// ---------------------------------------------------------------------------
// CORS helper
// ---------------------------------------------------------------------------
function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept",
    "Access-Control-Max-Age": "86400",
  };
}

// ---------------------------------------------------------------------------
// Error response helper
// ---------------------------------------------------------------------------
function jsonError(message, status, origin) {
  return new Response(JSON.stringify({ error: message, status }), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(origin) },
  });
}

// ---------------------------------------------------------------------------
// Cache helper – gracefully degrades if Cache API is unavailable
// (e.g. in wrangler dev preview, or on free workers.dev subdomains)
// ---------------------------------------------------------------------------
async function cacheGet(cacheKey) {
  try {
    if (typeof caches === "undefined") return null;
    return await caches.default.match(cacheKey);
  } catch {
    return null;
  }
}

async function cachePut(ctx, cacheKey, response) {
  try {
    if (typeof caches === "undefined") return;
    ctx.waitUntil(caches.default.put(cacheKey, response.clone()));
  } catch {
    // Cache write failed – silently ignore, image still served directly
  }
}

// ---------------------------------------------------------------------------
// Main fetch handler
// ---------------------------------------------------------------------------
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "*";

    // ── CORS preflight ───────────────────────────────────────────────────────
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    // ── Method guard ─────────────────────────────────────────────────────────
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    // ── Extract & validate `path` param ──────────────────────────────────────
    const rawPath = url.searchParams.get("path");
    if (!rawPath) {
      return jsonError("Missing required query parameter: path", 400, origin);
    }

    const safePath = rawPath.startsWith("/") ? rawPath : `/${rawPath}`;
    if (!/^\/[a-zA-Z0-9/_.\\-]+$/.test(safePath)) {
      return jsonError("Invalid path parameter", 400, origin);
    }

    const targetUrl = `${TMDB_IMAGE_BASE}${safePath}`;

    // ── Cache lookup (key = this worker's own URL to comply with zone rules) ──
    const cacheKey = new Request(request.url, { method: "GET" });
    const cached = await cacheGet(cacheKey);
    if (cached) {
      const headers = new Headers(cached.headers);
      Object.entries(corsHeaders(origin)).forEach(([k, v]) => headers.set(k, v));
      return new Response(cached.body, { status: cached.status, headers });
    }

    // ── Fetch from TMDB origin ────────────────────────────────────────────────
    let tmdbResponse;
    try {
      tmdbResponse = await fetch(targetUrl, {
        headers: {
          "User-Agent": "Mozilla/5.0 (compatible; SocratesScreen/1.0)",
          Accept: "image/webp,image/apng,image/*,*/*;q=0.8",
        },
        cf: { cacheTtl: 31536000, cacheEverything: true },
      });
    } catch (err) {
      return jsonError(`Failed to reach TMDB: ${err}`, 502, origin);
    }

    if (!tmdbResponse.ok) {
      return jsonError("TMDB returned non-OK status", tmdbResponse.status, origin);
    }

    // ── Build response with cache + CORS headers ──────────────────────────────
    const responseHeaders = new Headers(tmdbResponse.headers);
    responseHeaders.set("Cache-Control", "public, max-age=31536000, immutable");
    responseHeaders.set("Vary", "Accept");
    Object.entries(corsHeaders(origin)).forEach(([k, v]) =>
      responseHeaders.set(k, v)
    );

    const response = new Response(tmdbResponse.body, {
      status: tmdbResponse.status,
      headers: responseHeaders,
    });

    // Store in edge cache non-blocking (safe, won't crash on failure)
    await cachePut(ctx, cacheKey, response);

    return response;
  },
};
