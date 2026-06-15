# Freshness — keeping the catalog honest

Cloudflare ships fast: products get renamed (Calls → Realtime, Magic Firewall →
Network Firewall, Browser Rendering → Browser Run), launched (AI Search, R2 SQL,
Agent Memory, Dynamic Workers), and re-priced constantly. **This catalog is a dated
cache of the docs, not the source of truth.** The docs are.

- **Catalog built:** 2026-06-15
- **Snapshot of Cloudflare's index at build:** [`sources/developers.cloudflare.com-llms.txt`](sources/developers.cloudflare.com-llms.txt)

## The contract

1. The lens treats every catalog entry as a **dated hypothesis**.
2. Before asserting any specific (limit, price, binding, API shape, or even "product X
   exists"), it **verifies against the live source** — the `cloudflare-docs` MCP or the
   entry's own `llms.txt`.
3. If the live docs and the catalog disagree, **the live docs win.**

## Canonical sources — the links to double-check

| What | Link | Use |
|---|---|---|
| Master product index | https://developers.cloudflare.com/llms.txt | Diff vs the snapshot to find added/removed/renamed products |
| Per-product index | `https://developers.cloudflare.com/<product>/llms.txt` | Use when the master index or product docs expose one; otherwise reconcile against the canonical Markdown docs for that product |
| Live docs search | `cloudflare-docs` MCP (`search_cloudflare_documentation`) | Verify a specific fact on demand |
| Cloudflare's own agent prompt | https://developers.cloudflare.com/agent-setup/prompt.md | Cloudflare's self-described, re-verifiable setup source |
| Changelog | https://developers.cloudflare.com/changelog/ ( + `/changelog/llms.txt`) | What changed and when |

## Detect drift — `/flare-refresh`

1. Fetch `developers.cloudflare.com/llms.txt`.
2. Diff against [`sources/developers.cloudflare.com-llms.txt`](sources/developers.cloudflare.com-llms.txt).
3. Report products **added / removed / renamed**, each with its doc link. Classify
   documentation-only roots separately (for example `style-guide`, `learning-paths`,
   `agent-setup`, `docs-for-agents`, `migration-guides`, `support`, `use-cases`,
   `reference-architecture`): they can improve procedures and prompt behavior, but they
   are not automatically catalog entries because they do not replace hand-rolled infra.
4. For a named product, derive the docs root from its `docs:` URLs and/or the master
   index, fetch its `llms.txt` if one exists, and otherwise reconcile against the
   canonical Markdown docs plus `cloudflare-docs` search.

## Refresh the content

- **Small change:** edit `sources/catalog.json`, then `python3 sources/build_catalog.py`
  regenerates `INDEX.md` + the category files deterministically. The generator preserves
  `sources/.built` so local source edits do not falsely claim a new live-doc snapshot.
  If `sources/.built` is missing or empty, generation fails instead of inventing a date.
- **Many new/changed products:** re-run the catalog research workflow (one agent per
  product, grounded in live `llms.txt`), merge into `catalog.json`, regenerate.
- **After a true live-doc refresh:** overwrite the snapshot in `sources/`, update
  `sources/.built` to the refresh date, then run `python3 sources/build_catalog.py` so
  `INDEX.md` and generated category files inherit the real snapshot date. Update this
  file only when the refresh date or process changes.

> Provenance lives in [`sources/`](sources/): the index snapshot, the raw research JSON
> (`catalog-base.json`, `catalog-gapfill.json`), the merged/manual-additions source
> (`catalog.json`), ecosystem source data (`eco.json`), the critic's review
> (`critic.json`), and the generators (`build_catalog.py`, `build_community.py`).
