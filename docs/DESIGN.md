# Flarepilled — design

> Don't build what Cloudflare already runs.

## What it is

A Claude Code **plugin** that installs a persistent *lens*: a Cloudflare-pilled
architect persona that, during ordinary code work, notices when a codebase is
**hand-rolling or renting** a capability that Cloudflare offers as a managed edge
primitive — and surfaces an honest, confidence-rated swap. Plus a `/flare-scan`
command that audits a whole repo on demand.

It is the deliberate mirror of **Ponytail** (the lazy-senior-dev plugin):
- **Ponytail** pushes *down* the complexity axis — don't write code you don't need.
- **Flarepilled** pushes *off* the operations axis — don't run infra Cloudflare runs.

Same north star: the cheapest system to own is the one you never had to maintain.

## Principles

1. **Honesty over evangelism.** Cloudflare is not always the answer. Every
   suggestion names its catch (lock-in, egress/data-gravity, limits, migration cost).
   A wrong recommendation costs trust, which is the whole asset.
2. **Confidence is a first-class field.** `high` = verified against live docs at
   point-of-use (this turn). `medium` = catalogued (grounded in docs at build time,
   not re-verified). `speculative` = an idea. The lens never launders a guess as a fact.
3. **Verify before asserting specifics.** Limits, prices, binding names, and API
   shapes drift fast. The lens confirms them against the live `cloudflare-docs` MCP
   (or a product `llms.txt`) before stating them. The catalog is a map, not the
   territory.
4. **Signal over noise.** Quiet by default; speaks on high-confidence matches only.
   Like Ponytail only simplifies when it helps.

## Architecture

```
flarepilled/                         (this repo = the plugin)
├── .claude-plugin/
│   ├── plugin.json                  manifest
│   └── marketplace.json             install/listing metadata
├── hooks/
│   ├── hooks.json                   wires SessionStart → activate
│   └── flarepilled-activate.js      prints SKILL.md to stdout = always-on lens
├── skills/flarepilled/
│   └── SKILL.md                     the lens: persona, the check, rules, smell map
├── commands/
│   ├── flare.toml                   /flare — set loudness (quiet/normal/loud/off)
│   ├── flare-scan.toml              /flare-scan — audit a codebase
│   └── flare-refresh.toml           /flare-refresh — diff the catalog vs live docs
├── knowledge/                       the catalog (the brain) — a dated cache of the docs
│   ├── INDEX.md                     master quick-ref: every product, one row
│   ├── FRESHNESS.md                 canonical sources + how to detect/fix drift
│   ├── catalog/<category>.md        per-category deep entries (from live docs)
│   ├── videos/<date>-<topic>.md     optional verified deep-dives
│   └── sources/                     provenance: llms.txt snapshot, research JSON, generator
├── examples/                        before/after "DIY vs Cloudflare" worked cases
└── docs/DESIGN.md                   this file
```

**Always-on mechanism.** For Claude Code, whatever a `SessionStart` hook writes to
stdout is injected as session context. `flarepilled-activate.js` reads `SKILL.md`
and prints it. That is the entire "persistent persona" trick — copied from Ponytail.

**v0.1 is deliberately lazy** (`flarepilled:` by design): one hook, no lite/full/ultra
state machine. Loudness persists via a one-word flag file (`~/.claude/.flarepilled-active`)
that the hook reads and `/flare` writes. Add more only if/when it earns its keep.

## The knowledge model

The lens draws on two layers — **the live docs are the spine**:

- **Catalog (the brain):** 112 products fanned out by research agents, each grounded in
  that product's live `llms.txt` at build time — 108/112 `high`, 4 `medium`. This is a
  fast, *dated cache* of the docs; specifics are re-verified against the `cloudflare-docs`
  MCP at point-of-use, and the catalog only ever decides *what to consider*.
- **Optional enrichment (`knowledge/videos/`):** a dated note from a doc page, blog, or
  watched demo — vivid but narrow, always reconciled against the docs, never ranked above
  them. Example on disk: the **Cloudflare Images** deep-dive. Not a required input.

Each catalog entry carries the fields that power the lens: `replaces` (the "stop
building this" hook), `detectionSignals` (concrete smells a scanner greps for),
`ideaPrompts` (proactive uses), `apiSurface`, `pricing`, `limits`, `pairsWith`,
`docs`, `confidence`, `notes`.

## Staying current

**The live docs are the spine; the catalog is a dated cache of them.** Keeping it honest:

1. **Verify at point-of-use** — the lens checks specifics against the `cloudflare-docs`
   MCP / a product `llms.txt` before asserting. The catalog is never quoted as current
   truth; it only decides *what to consider*.
2. **Detect drift** — `/flare-refresh` diffs Cloudflare's canonical `llms.txt` against
   the snapshot in `knowledge/sources/` and reports added / removed / renamed products.
3. **Refresh** — re-run the research (grounded in live docs at refresh time; **manual
   today, not automatic**) and regenerate via `build_catalog.py`. Optional enrichment:
   a dated note from a doc, blog, or watched demo — flavor, not the pipeline.

Canonical sources and the full procedure: `knowledge/FRESHNESS.md`.

Catalog built 2026-06-15 — 112 products across 12 categories (108 `high`, 4 `medium`),
from Cloudflare's `llms.txt` + live per-product docs (base research pass + a gap-fill
pass for the Zero Trust/SASE sub-products and the Rules family). Optional enrichment
example on disk: the Cloudflare Images deep-dive.

## Roadmap (only if wanted)

- Statusline badge reading the loudness flag (`~/.claude/.flarepilled-active`).
- A scheduled / `/loop` auto-refresh (the hook already nudges when the catalog is stale).
- Portability stubs (`AGENTS.md`, Codex/OpenCode configs) like Ponytail ships.
- Per-entry structured `migrationEffort` / `impact` fields to fully mechanize scan ranking.
