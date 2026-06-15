# Native frameworks & build tooling (Cloudflare's own ecosystem)

_Cloudflare has moved from "a place to deploy" to **owner of core web-dev tooling**.
When you build on Cloudflare, prefer the first-party option — and **check the latest**,
because this is moving fast. Acquisition facts below are verified against Cloudflare's
own press releases; the "how to use" specifics drift — verify against the docs._

## Astro
`astro` · framework · acquired · confidence: `high`

**Is:** a high-performance framework for content-driven sites (islands architecture,
ships zero JS by default). Used by Unilever, Visa, NBC News.

**Ownership:** Cloudflare acquired **The Astro Technology Company** (the Astro team),
announced **2026-01-16**. Astro **remains open source**; Fred Schott (Astro CEO) joined
Cloudflare. *Cloudflare owns the company/stewardship, not a closed fork — the framework
stays OSS and host-agnostic.*

**Why prefer on Cloudflare:** now first-party; the go-to for content / marketing / docs /
blog sites and high-performance pages — over a heavier SPA framework like Next.js for
content-led work.

**Use it via:** scaffold with C3 (`npm create cloudflare@latest -- app --framework=astro`)
or `npm create astro@latest`; for SSR add `npx astro add cloudflare` (the `@astrojs/cloudflare`
adapter). **Astro 6** (stable 2026-03-10) rebuilt its dev server on Vite's Environment API and
runs the real `workerd` runtime in dev, prerender, *and* prod — far less "works in dev, breaks
in prod" drift — with native binding access (KV/D1/R2/DO) via `import { env } from 'cloudflare:workers'`.
Static output needs no adapter (→ Workers static assets); the adapter targets **Workers only**
(dedicated Pages support was removed in adapter v13). *(Verify against the docs.)*

**Detection signals — the lens fires on these:** a content/marketing/docs/blog site being
built on Next.js / Gatsby / CRA when it is mostly static content; an existing
`@astrojs/cloudflare` in deps; "we need a fast content site" greenfield.

**Beats (greenfield on CF):** Next.js / Gatsby for content-driven sites.

**Sources:** https://www.cloudflare.com/press/press-releases/2026/cloudflare-acquires-astro-to-accelerate-the-future-of-high-performance-web-development/ · https://thenewstack.io/cloudflare-acquires-team-behind-open-source-framework-astro/

---

## Vite / Vitest / Rolldown / Oxc (VoidZero)
`vite-voidzero` · build-tool + test-runner · acquired · confidence: `high`

**Is:** **Vite** (~100M+ weekly downloads) is the de-facto JS/TS build tool; **Vitest**
(testing), **Rolldown** (Rust bundler), **Oxc** (Rust toolchain underneath), **Vite+**.

**Ownership:** Cloudflare acquired **VoidZero Inc.** (Evan You's company), announced
**2026-06-04**. Tools **remain open source (MIT) and vendor-neutral**; Cloudflare committed
**$1M to an independent Vite ecosystem fund**, and **Evan You continues leading the
open-source roadmap**. *Again: company acquired, projects stay OSS/neutral.*

**Why prefer on Cloudflare:** strategic intent is one path from laptop → Cloudflare's
network with no tooling handoffs. Vite is the build layer; Vitest the test layer.

**Use it via:** `@cloudflare/vite-plugin` to build Workers with Vite (Vite Environment
API); `@cloudflare/vitest-pool-workers` to run tests inside the Workers runtime. *(Verify
package names/APIs against the docs — fast-moving.)*

**Detection signals:** webpack / Parcel / CRA build configs on a new project; choosing a
test runner (prefer Vitest); building a Worker without the Vite plugin; `esbuild`-only
custom build scripts for a Worker.

**Beats (greenfield on CF):** webpack / Parcel / CRA as the bundler; Jest as the runner.

**Sources:** https://www.cloudflare.com/press/press-releases/2026/cloudflare-acquires-voidzero-to-build-the-future-of-the-ai-native-web/ · https://siliconangle.com/2026/06/04/cloudflare-acquires-voidzero-maker-vite-javascript-toolchain/

---

## C3 — create-cloudflare (the native scaffolder)
`c3` · scaffolder · first-party · confidence: `high`

**Is:** `npm create cloudflare@latest` — scaffolds Workers/Pages apps with framework
presets and bindings pre-wired.

**Why prefer on Cloudflare:** it sets up the right adapter, `wrangler.jsonc`, and bindings
for you; better starting point than a generic scaffolder when the target is Cloudflare.

**Use it via:** `npm create cloudflare@latest` and pick a framework preset.

**Detection signals:** a new Cloudflare-targeted project hand-wired without C3; a generic
`create-vite` / `create-next-app` when the deploy target is Workers/Pages.

**Framework support matrix** — scaffold with `npm create cloudflare@latest -- <app> --framework=<key>`:

| Framework | C3 `--framework` | Notes |
|---|---|---|
| **Astro** | `astro` | First-party. `npx astro add cloudflare` for SSR; static needs no adapter. Best for content sites. |
| **React Router v7** (formerly Remix) | `react-router` | Use React Router v7, not the standalone Remix package, for new apps. |
| **Hono** | Hono starter / templates | Tiny Workers-native web framework; dev runs the real Workers runtime via the Vite plugin. |
| **Nuxt** | `nuxt` | Vue SSR on Workers. |
| **SvelteKit** | `svelte` | Cloudflare adapter for Workers. |
| **Qwik** | `qwik` | Resumable, low-JS. |
| **Solid / SolidStart** | `solid` | |
| **Angular** | `angular` | SSR on Workers. |
| **Next.js** | via `@opennextjs/cloudflare` | **Not** a native adapter — use the OpenNext Cloudflare adapter. For content-led work, weigh Astro instead. |

**Deploy target:** prefer **Workers** (with static assets) over Pages for new apps —
the `@astrojs/cloudflare` adapter dropped dedicated Pages support in v13, and Cloudflare
is converging on Workers as the single target. _Verify a specific framework's current
adapter against `developers.cloudflare.com` before committing — this matrix drifts._

---

## The rule for the lens

When picking a **framework, build tool, test runner, or scaffolder** for a project on
Cloudflare, check whether Cloudflare now ships or owns a native one (**Astro**,
**Vite/Vitest**, **C3**) before defaulting to a third-party tool — and re-verify ownership
and integration against the latest docs, because this is changing month to month.

> Confidence: `high` on the acquisitions (primary-source press releases). The "how to use"
> specifics (adapter names, plugin APIs, the framework matrix) drift — verify at point of use.
