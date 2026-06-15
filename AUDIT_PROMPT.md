# Flarepilled — Adversarial Audit Brief

> Hand this to a capable coding agent (Claude Code, etc.) with read/write access to
> this repository. It is authorized to launch as many parallel agents/workflows as it
> needs. The goal is to make Flarepilled **extremely powerful, precise, and honest** —
> not to be polite about it.

---

## Your mission

You are auditing **Flarepilled**, a Claude Code plugin (repo: `Waiel5/flarepilled`).
Stress-test it until it is the most powerful, accurate, and trustworthy version of
itself. Be ruthless and adversarial. **Launch as many agents/workflows as you need** —
fan out by dimension, by product area, by source. Ground every factual finding in
**primary sources** (the live Cloudflare docs: the `cloudflare-docs` MCP and
`WebFetch` on `https://developers.cloudflare.com/<product>/llms.txt`). Do not trust the
repo's own claims, your training, or even this brief — verify.

## What Flarepilled is

A persistent "Cloudflare-pilled architect" lens, modeled on the **Ponytail** plugin
(which pushes "don't write code you don't need"). Flarepilled pushes the mirror:
**"don't operate infra Cloudflare already runs."** During code work it catches
capabilities being hand-rolled — or rented from another vendor — that Cloudflare offers
as a managed primitive, and surfaces an honest, doc-verified, confidence-rated swap it
can actually wire up. Core thesis: *if Cloudflare already runs it, use Cloudflare's;
don't rebuild from scratch.*

## Read these first

| Path | What it is |
|---|---|
| `skills/flarepilled/SKILL.md` | **The always-injected lens — the heart.** Persona, decision framework, verification contract, MCP toolchain, rules, traps, smell→product map. |
| `knowledge/INDEX.md` → `knowledge/catalog/<category>.md` | The **112-product catalog** (each entry: `replaces` / `detectionSignals` / `apiSurface` / `pricing` / `limits` / `lock-in`). |
| `knowledge/catalog/frameworks-ecosystem.md` | Cloudflare's native frameworks (Astro, Vite/VoidZero, C3) + the framework matrix. |
| `knowledge/community-patterns.md` | 51 community patterns/gotchas, confidence-tagged. |
| `knowledge/FRESHNESS.md` | The freshness + verification contract and canonical sources. |
| `commands/*.toml` | `/flare` (loudness), `/flare-scan` (audit), `/flare-refresh` (drift check). |
| `hooks/flarepilled-activate.js` | SessionStart injection + loudness persistence + staleness nudge. |
| `knowledge/sources/` | Provenance JSON + the generators `build_catalog.py`, `build_community.py`. |
| `examples/` | 8 worked before/after migrations (real bindings + provisioning commands). |
| `docs/DESIGN.md` | Architecture & rationale. |

## Audit dimensions (fan out across these)

### 1. Factual accuracy — HIGHEST PRIORITY
Cloudflare renames and re-prices constantly. Verify against live docs:
- **Every catalog entry**: is `replaces` framed right? Are `apiSurface` (bindings/wrangler
  keys/SDK), `pricing`, and `limits` current and correct? Flag stale product names, wrong
  limits, wrong binding names.
- **Every row** of the SKILL's "Quick smell → Cloudflare map" — right product for the smell, named correctly, not retired?
- `frameworks-ecosystem.md`: the acquisition facts (Astro → The Astro Technology Company, Jan 16 2026; Vite/Vitest/Rolldown → VoidZero, Jun 4 2026; both stay OSS), the C3 `--framework` matrix, the `@astrojs/cloudflare` adapter + Vite plugin details.
- **The "Common traps" + community gotchas**: verify each (e.g. KV ~1 write/sec per key & ~60s consistency; DO WebSocket Hibernation billing; D1 10 GB cap + read-replica Sessions API; R2 ≠ full S3; Workers 128 MB RAM).
- The 5 MCP servers and what each does.
Report each inaccuracy with the **correct fact + the doc URL** you verified it against.

### 2. The lens prompt — power & intelligence
- Where is `SKILL.md` vague, weak, redundant, or **gameable**?
- Is the verification contract actually **enforceable** ("a nudge is `high` only if verified this turn; no numbers in an unverified relay")? Try to slip a fabricated figure past it.
- Is the suggestion budget + "when NOT to flare" discipline strong enough to stop annoyance and false positives? Construct cases where it over-fires.
- Test the four judgment tests (undifferentiated / data-gravity / lock-in tier / scale) on **hard cases** — does it make good calls or rationalize?
- Compare directly to Ponytail's `SKILL.md`. Is it as sharp? Is it more capable? What would make it decisively better?

### 3. Completeness
- What Cloudflare products/capabilities are **missing or under-covered**? Cross-check `https://developers.cloudflare.com/llms.txt`. (Known not-yet-added: Cloudflare One's Risk Score/UEBA.)
- What **detection signals** are missing that would let it catch more reinvention (npm packages, env vars, file patterns, vendor names)?

### 4. Honesty & safety — adversarial
Try to make the lens give a **bad recommendation**: oversell Cloudflare, ignore lock-in, push a beta product onto a production path, suggest migrating working non-bottleneck infra, or launder a guess as fact. Where does it crack? Where does it fail to name a real downside (egress, data gravity, lock-in tier, maturity)?

### 5. Mechanism correctness — run it, don't assume
- Run `node hooks/flarepilled-activate.js` — does it emit the lens, honor `~/.claude/.flarepilled-active` (try `off`/`loud`), and compute the staleness nudge from `knowledge/sources/.built`?
- Re-run `python3 knowledge/sources/build_catalog.py` and `build_community.py` — do they regenerate `INDEX.md` + the category files + `community-patterns.md` cleanly?
- Validate `plugin.json` / `marketplace.json` / `hooks/hooks.json` against the Claude Code plugin schemas.
- Walk the `/flare-scan` and `/flare-refresh` procedures — do they actually work end to end?

### 6. Coherence
Do all surfaces agree — product counts, command names, framing, version? Any contradiction across `README.md` / `DESIGN.md` / `SKILL.md` / `INDEX.md` / `plugin.json`?

## Deliverable

A **severity-ranked report** (high / medium / low). Each finding carries: the issue, the
**evidence** (doc URL or `file:line`), and a **concrete fix**. Then, if you have write
access, **apply the high-confidence fixes** and re-run the generators + the hook to verify
nothing broke.

Hold yourself to the plugin's own bar: mark every finding with how you verified it, and
never assert a Cloudflare fact you didn't check against live docs this run. Where you
change knowledge, edit `knowledge/sources/*.json` and regenerate — don't hand-edit
generated files.

**Make it extremely powerful. Find what's wrong.**
