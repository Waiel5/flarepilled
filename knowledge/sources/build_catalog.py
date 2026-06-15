#!/usr/bin/env python3
"""Render the Flarepilled knowledge base from the research JSON.

Input : knowledge/sources/catalog.json  (merged array of entry objects)
Output: knowledge/INDEX.md  +  knowledge/catalog/<bucket>.md

The research agents each invented their own free-form `category`, so the only
real work here is bucketing them into a browseable set. Ordered keyword rules,
first match wins, specific-before-general. The catch-all is last so nothing is
dropped. # flarepilled: keyword bucketing, hand-map a slug only if it lands wrong
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # /Users/grey/CF
SRC = ROOT / "knowledge" / "sources" / "catalog.json"
INDEX = ROOT / "knowledge" / "INDEX.md"
CATDIR = ROOT / "knowledge" / "catalog"

# (bucket title, output filename, [category-substring keywords]). First match wins.
BUCKETS = [
    ("Rules & Edge Logic", "rules-edge-logic", ["rules", "edge logic", "ruleset"]),
    ("Zero Trust & SASE", "zero-trust-sase", ["zero trust", "sase", "device agent", "firewall-as-a-service", "data residency", "sovereignty"]),
    ("AI & Agents", "ai-agents", ["ai /", "ai assistant", "agent", "vector", " rag", "rag &", "inference", "llmops", "ml platform", "retrieval"]),
    ("Media", "media", ["media", "video", "image", "webrtc"]),
    ("Security", "security", ["security", "firewall", "ddos", "bot ", "bot &", "bot mitigation", "captcha", "certificate", "human verification", "api security", "client-side", "e2ee", "supply chain", "posture", "threat"]),
    ("Messaging & Email", "messaging-email", ["messaging", "email", "eventing"]),
    ("Observability & Analytics", "observability", ["observability", "analytics", "log", "rum", "alerting", "monitoring", "flow analytics", "reachability"]),
    ("Performance & CDN", "performance-cdn", ["performance", "cdn", "cache", "regional delivery", "reliability", "speed"]),
    ("Networking & DNS", "networking-dns", ["dns", "network", "registrar", "domains", "routing", "connectivity", "l4 proxy", "wan", "multi-cloud", "spectrum", "tls", "web3"]),
    ("Storage, Databases & Data", "storage-data", ["object storage", "storage", "database", "data access", "versioned storage", "streaming etl", "data & analytics", "pipeline"]),
    ("Compute & Workers", "compute-workers", ["compute", "serverless", "durable", "sandbox", "code execution", "functions-as-a-service", "stateful"]),
    ("Platform & DevEx", "platform-devex", []),  # catch-all
]

# A few entries whose free-form category fools the keyword rules, or that belong
# where Cloudflare's own taxonomy puts them. Explicit slug -> bucket title.
BUCKET_OVERRIDE = {
    "workers-kv": "Storage, Databases & Data",          # "Storage / Edge cache" -> Performance
    "r2-sql": "Storage, Databases & Data",              # "Data & Analytics" -> Observability
    "r2-data-catalog": "Storage, Databases & Data",     # "catalog" contains "log"
    "cloudflare-load-balancing": "Performance & CDN",   # Cloudflare lists under App performance
    "cloudflare-waiting-room": "Performance & CDN",
    "cloudflare-health-checks": "Performance & CDN",
    "cloudflare-google-tag-gateway": "Performance & CDN",
    "cloudflare-snippets": "Rules & Edge Logic",        # keep the Rules family whole
}

TITLE2FNAME = {t: f for (t, f, _) in BUCKETS}


def bucket_for(entry):
    slug = entry.get("slug")
    if slug in BUCKET_OVERRIDE:
        t = BUCKET_OVERRIDE[slug]
        return t, TITLE2FNAME[t]
    cat = (entry.get("category") or "").lower()
    for title, fname, keys in BUCKETS:
        if not keys:
            continue
        if any(k in cat for k in keys):
            return title, fname
    return BUCKETS[-1][0], BUCKETS[-1][1]


# Lock-in tier (heuristic, but consistent): portable < sticky < deep. The SKILL defines
# the taxonomy; this binds each product to one so /flare-scan ranks from data, not vibes.
LOCKIN_OVERRIDE = {
    "cloudflare-workers": "portable", "cloudflare-pages": "portable",
    "durable-objects": "deep", "vectorize": "deep", "ai-search": "deep",
    "workflows": "deep", "cloudflare-agents": "deep", "agent-memory": "deep",
    "cloudflare-realtime": "deep", "cloudflare-access": "deep",
}
_STICKY_CATS = ("storage", "object storage", "database", "data access", "data &",
                "streaming etl", "pipeline", "media", "video", "image", "messaging",
                "email", "vector", "ai /", "queue", "zero trust", "sase", "device agent")


def lockin_for(entry):
    if entry.get("slug") in LOCKIN_OVERRIDE:
        return LOCKIN_OVERRIDE[entry["slug"]]
    cat = (entry.get("category") or "").lower()
    if any(k in cat for k in _STICKY_CATS):
        return "sticky"   # data you'd have to migrate to leave
    return "portable"     # config-level: rules, dns, perf, most security, observability


def anchor(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def bullets(items, limit=None):
    items = items or []
    if limit:
        items = items[:limit]
    return "\n".join(f"- {x}" for x in items) if items else "_n/a_"


def short(text, n=110):
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def assert_unique_slugs(entries):
    seen = {}
    dupes = []
    for idx, entry in enumerate(entries, start=1):
        slug = entry.get("slug") or anchor(entry.get("name", "?"))
        if slug in seen:
            dupes.append((slug, seen[slug], idx))
        else:
            seen[slug] = idx
    if dupes:
        lines = [
            f"- {slug}: entries {first} and {second}"
            for slug, first, second in dupes
        ]
        raise SystemExit("Duplicate catalog slugs found; fix sources/catalog.json:\n" + "\n".join(lines))


def main():
    entries = json.loads(SRC.read_text())
    assert_unique_slugs(entries)

    # group
    groups = {}
    for e in entries:
        title, fname = bucket_for(e)
        groups.setdefault((title, fname), []).append(e)

    ordered = [(t, f) for (t, f, _) in BUCKETS if (t, f) in groups]

    CATDIR.mkdir(parents=True, exist_ok=True)
    built_path = ROOT / "knowledge" / "sources" / ".built"
    if not built_path.exists():
        raise SystemExit("Missing knowledge/sources/.built; run /flare-refresh after a true live-doc refresh.")
    built = built_path.read_text().strip()
    if not built:
        raise SystemExit("Empty knowledge/sources/.built; write the real live-doc snapshot date before generating.")
    n = len(entries)
    hi = sum(1 for e in entries if e.get("confidence") == "high")

    # ---- INDEX.md ----
    idx = [
        "# Flarepilled — Cloudflare catalog index",
        "",
        f"> **{n} products** across {len(ordered)} categories · {hi} high-confidence · "
        f"seeded {built} from `developers.cloudflare.com/llms.txt` + live per-product docs.",
        ">",
        "> **Catalog confidence:** `high` = docs/source-grounded at build time · `medium` = asserted or beta/unsettled, re-verify. "
        "Final flare confidence also requires observed repo fit, maturity, and no blocker. Re-check specifics "
        "(limits / pricing / bindings / API shape) against live docs before quoting. The deep entries live in `catalog/<category>.md`.",
        "",
    ]
    for title, fname in ordered:
        rows = sorted(groups[(title, fname)], key=lambda e: e.get("name", ""))
        idx.append(f"## {title} ({len(rows)})")
        idx.append("")
        idx.append("| Product | Replaces | Conf | |")
        idx.append("|---|---|---|---|")
        for e in rows:
            conf = e.get("confidence", "?")
            link = f"[›](catalog/{fname}.md#{anchor(e.get('name',''))})"
            idx.append(f"| **{e.get('name','?')}** | {short(e.get('replaces',''))} | `{conf}` | {link} |")
        idx.append("")
    idx += [
        "## Also in the knowledge base",
        "",
        "- [`catalog/frameworks-ecosystem.md`](catalog/frameworks-ecosystem.md) — Cloudflare's native frameworks & build tooling (Astro, Vite/VoidZero, C3 + the framework matrix).",
        "- [`community-patterns.md`](community-patterns.md) — community-sourced patterns, clever combos, and gotchas (confidence-tagged, anecdotal).",
        "- [`FRESHNESS.md`](FRESHNESS.md) — canonical sources + how to detect & fix catalog drift.",
        "",
    ]
    INDEX.write_text("\n".join(idx))

    # ---- catalog/<bucket>.md ----
    for title, fname in ordered:
        rows = sorted(groups[(title, fname)], key=lambda e: e.get("name", ""))
        out = [f"# {title}", "", f"_{len(rows)} products. Part of the Flarepilled catalog — see `../INDEX.md`._", ""]
        for e in rows:
            out += [
                f"## {e.get('name','?')}",
                f"`{e.get('slug','')}` · {e.get('category','')} · confidence: `{e.get('confidence','?')}` · lock-in: `{lockin_for(e)}`",
                "",
                f"**Is:** {e.get('oneLiner','')}",
                "",
                f"**Replaces:** {e.get('replaces','')}",
                "",
                f"**Use it via:** {e.get('apiSurface','')}",
                "",
                "**Capabilities:**",
                bullets(e.get("capabilities")),
                "",
                "**Detection signals — the lens fires on these:**",
                bullets(e.get("detectionSignals")),
                "",
                "**Ideas:**",
                bullets(e.get("ideaPrompts")),
                "",
                f"**Pairs with:** {', '.join(e.get('pairsWith') or []) or '_n/a_'}",
                "",
                f"**Pricing:** {e.get('pricing','_verify against docs_')}",
                "",
                "**Limits:**",
                bullets(e.get("limits")),
                "",
            ]
            if e.get("notes"):
                out += [f"**Notes:** {e['notes']}", ""]
            out += [f"**Docs:** {', '.join(e.get('docs') or []) or '_n/a_'}", "", "---", ""]
        (CATDIR / f"{fname}.md").write_text("\n".join(out))

    # ---- report ----
    print(f"{n} entries ({hi} high, {n-hi} other) → {len(ordered)} buckets")
    for title, fname in ordered:
        print(f"  {len(groups[(title,fname)]):2d}  {title}  (catalog/{fname}.md)")


if __name__ == "__main__":
    main()
