# 🟠 Flarepilled

> **Don't build what Cloudflare already runs.**

A Claude Code plugin that installs a persistent *Cloudflare-pilled architect* lens.
While you code, it quietly watches for capabilities you are **hand-rolling** (or
renting from another vendor) that Cloudflare offers as a managed edge primitive —
storage, cache, queues, cron, durable state, auth, CAPTCHA, vector search, RAG, an
LLM gateway, image/video pipelines, email — and surfaces an **honest,
confidence-rated** swap. Plus `/flare-scan` to audit a whole repo on demand.

It is the deliberate twin of **Ponytail** (the lazy-senior-dev plugin):

| | pushes you to… | by asking… |
|---|---|---|
| **Ponytail** | write less code | "does this need to exist? does stdlib do it?" |
| **Flarepilled** | operate less infra | "does Cloudflare already run this?" |

Same north star: *the cheapest system to own is the one you never had to maintain.*

## What it does

- **Always-on lens.** A `SessionStart` hook injects the lens every session. It stays
  **quiet until a real, high-confidence match**, then speaks once, briefly:

  > 🟠 **Flare:** You're hand-rolling `multer + sharp` image resizing. Cloudflare
  > **Images** replaces the whole pipeline (upload once, every variant is a URL).
  > Confidence: `high`. Catch: delivery URLs are Cloudflare-specific. Want the swap?

- **`/flare-scan`** — reads your dependency manifests, infra files, and architecture,
  matches them against the catalog, **verifies specifics against live Cloudflare
  docs**, and returns a ranked table of swaps with effort + lock-in + confidence.

- **`/flare quiet|normal|loud|off`** — set how chatty the lens is.

- **`/flare-refresh`** — re-checks the catalog against Cloudflare's live `llms.txt` and reports drift (added / removed / renamed products). See [`knowledge/FRESHNESS.md`](knowledge/FRESHNESS.md).

## Honesty model (the point)

Cloudflare is **not always the answer**, and this plugin is built to say so.

- Every suggestion names its **catch** (lock-in, egress/data-gravity, limits, cost).
- **Confidence is explicit:** `high` = verified against live docs this turn · `medium` =
  catalogued (grounded at build time, unverified) · `speculative` = an idea. An
  unverified relay never quotes a specific limit or price.
- The catalog is **dated**; Cloudflare ships fast. Before quoting any limit, price,
  binding, or API shape, the lens **re-verifies against the `cloudflare-docs` MCP**.
  The catalog is a map, not the territory.

## Structure

```
.claude-plugin/   manifest + marketplace metadata
hooks/            SessionStart hook that injects the lens (the "always-on" trick)
skills/flarepilled/SKILL.md   the lens: persona, the check, rules, smell→product map
commands/         /flare · /flare-scan · /flare-refresh
knowledge/        the brain — INDEX.md + FRESHNESS.md + per-category catalog
docs/DESIGN.md    architecture & rationale
examples/         before/after "DIY vs Cloudflare" worked cases
```

## Install

```
claude plugin marketplace add Waiel5/flarepilled
claude plugin install flarepilled@flarepilled
```

Then run `/reload-plugins` (or restart). The lens loads on the next session start.
_(Local dev: `claude plugin marketplace add /path/to/flarepilled`.)_

## Staying current

**The live Cloudflare docs are the spine; the catalog is a fast, dated cache of them.**
The lens verifies specifics against the `cloudflare-docs` MCP before asserting, and
`/flare-refresh` diffs Cloudflare's canonical `llms.txt` to surface drift. Full
procedure + canonical links: [`knowledge/FRESHNESS.md`](knowledge/FRESHNESS.md).

- **Catalog:** **112 products across 12 categories** (108 high-confidence), each
  researched against its live `llms.txt` — the full AI suite, the Zero Trust / SASE
  sub-products (Access, Gateway, CASB, DLP, Email Security, DEX), and the Rules family
  included.
- **Extend depth** by dropping a dated note in `knowledge/` and upgrading a product's
  detection signals. (A watched demo — like the Cloudflare **Images** deep-dive in
  `knowledge/videos/` — is one optional way to enrich an entry, not a dependency.)

See [`docs/DESIGN.md`](docs/DESIGN.md) for the full design.

---

*Status: v0.1 (early). Lens + commands + a 112-product knowledge base live; loudness
persists; the catalog self-flags when stale. Intentionally lazy where it can be
(`flarepilled:`). Built to grow.*
