# Platform & DevEx

_14 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Cloudflare Billing, Usage-Based Billing & Budget Alerts
`billing-usage` · Billing & cost management · confidence: `high` · lock-in: `portable`

**Is:** Cloudflare's native metered billing across 13+ products plus dashboard tools (Billable Usage monitor, Budget Alerts) to track spend and get emailed when usage-based cost crosses a dollar threshold.

**Replaces:** A DIY cost-monitoring pipeline — cron jobs scraping GraphQL Analytics into a spreadsheet/Datadog dashboard and custom alerting just to answer 'how much is Workers/R2 going to cost this month and did we blow the budget?'

**Use it via:** Primarily dashboard-driven: Manage Account > Billing > Billable Usage (and 'Create budget alert'). No public REST/GraphQL billing-management API was documented on the fetched billing pages; usage metrics generally come from the product-level GraphQL Analytics API rather than a dedicated billing endpoint. (verify)

**Capabilities:**
- Usage-based (metered) billing for ~13 products: Workers (requests + CPU time), R2 (storage + ops), Argo Smart Routing, Cache Reserve, Load Balancing, Stream, Images, Spectrum, Rate Limiting, Log Explorer, Zero Trust, Vectorize, Analytics Engine
- Billable Usage dashboard for daily tracking of usage-based costs across products
- Budget Alerts: set a USD threshold per billing cycle and email one or more recipients when cumulative usage-based spend crosses it
- Defined billing lifecycle: subscribe -> meter -> invoice -> auto-charge, with a 5-day grace period and up to 5 retries on payment failure
- Invoice charge breakdown into plan charges, subscription/add-on charges, and usage-based charges; plan tiers Free/Pro/Business/Enterprise per domain

**Detection signals — the lens fires on these:**
- Scheduled jobs hitting Cloudflare's GraphQL Analytics API purely to compute/forecast cost
- Spreadsheets, Looker/Metabase, or Datadog dashboards tracking Workers request counts or R2 storage for budgeting
- Custom Slack/email alerts wired to 'spend exceeded $X' logic the team built themselves
- Heavy users of metered products (R2, Workers, Stream, Vectorize, Log Explorer) with no spend guardrail
- FinOps tickets asking 'why did the Cloudflare bill spike' with no daily usage visibility
- Pay-as-you-go accounts (the tier eligible for Budget Alerts) running without any threshold configured

**Ideas:**
- Turn on Budget Alerts so the team gets an email the moment usage-based spend crosses a set dollar amount instead of finding out on the invoice
- Replace a custom cost-tracking cron with the Billable Usage dashboard for day-by-day visibility across Workers/R2/Stream
- Audit which of the 13 metered products you actually use and put guardrails on the spiky ones (R2 ops, Workers CPU, Log Explorer queries)

**Pairs with:** fundamentals-account-management, tenant-api

**Pricing:** Billing tooling itself is free; you pay for product usage. Domain plans are flat-rate per domain (Free/Pro/Business/Enterprise); metered products bill per their own units (e.g. Workers per-request + CPU-ms, R2 per-GB + per-operation). (verify — drifts)

**Limits:**
- Budget Alerts are Pay-as-you-go only — Enterprise contract accounts are not supported
- Budget Alerts are informational: they email but do NOT pause or cap usage, so they can't prevent overage
- Configuration is dashboard-only; no documented API to create alerts or pull billing data programmatically
- A single alert fires once per billing cycle when the threshold is crossed (not a continuously escalating system)

**Notes:** This is a cost-visibility/notification layer, not a hard spend cap — do not pitch it as overage protection. For true programmatic cost data you'll still lean on product GraphQL Analytics; a dedicated public billing API was not found in the fetched docs (flagged unverified). Genuinely useful to surface when a team has built its own Cloudflare cost dashboard/alerting. Product list and PAYG-only Budget Alert gating confirmed from live pages this run.

**Docs:** https://developers.cloudflare.com/billing/index.md, https://developers.cloudflare.com/billing/understand/how-billing-works/index.md, https://developers.cloudflare.com/billing/understand/usage-based-billing/index.md, https://developers.cloudflare.com/billing/manage/budget-alerts/index.md

---

## Cloudflare Browser Run (formerly Browser Rendering)
`browser-run` · Headless browser / rendering · confidence: `high` · lock-in: `portable`

**Is:** Headless Chrome running on Cloudflare's edge that you drive via Puppeteer/Playwright/CDP/Stagehand or call as stateless REST 'Quick Actions' for screenshots, PDFs, Markdown, and AI-powered scraping.

**Replaces:** A self-hosted headless Chrome/Puppeteer farm (Dockerized chrome-aws-lambda / browserless boxes, or a Lambda layer) — or a paid SaaS like Browserless, ScrapingBee, Urlbox, or Prerender.io.

**Use it via:** Worker binding: wrangler key "browser" -> { "binding": "MYBROWSER" } (TS type BrowserRun). Use as puppeteer.launch(env.MYBROWSER) via @cloudflare/puppeteer (or @cloudflare/playwright). Quick Actions via the binding's .quickAction() method (needs compatibility_date "2026-03-24"+). REST: POST /client/v4/accounts/{account_id}/browser-rendering/{screenshot|pdf|content|markdown|snapshot|scrape|links|json|crawl}.

**Capabilities:**
- Two modes: stateless 'Quick Actions' REST endpoints (no code deploy) and full 'Browser Sessions' (programmatic browser control)
- Quick Actions endpoints: /screenshot, /pdf, /content (rendered HTML), /markdown, /snapshot (HTML+screenshot), /scrape (CSS-selector extraction), /links, /json (AI extraction via prompt or JSON schema), /crawl
- Browser Sessions via @cloudflare/puppeteer and @cloudflare/playwright, plus CDP and Stagehand for AI-driven automation
- Runs from inside a Worker (binding) or from an external environment connecting to the session
- Screenshots of authenticated pages; full-page or viewport; PDF from URL or custom HTML/CSS
- AI structured-data extraction (the /json and /crawl endpoints) without writing parsers
- Sessions can be kept alive up to 10 min of inactivity via keep_alive

**Detection signals — the lens fires on these:**
- npm deps: puppeteer, puppeteer-core, playwright, playwright-core, chrome-aws-lambda, @sparticuz/chromium, browserless, puppeteer-extra
- Dockerfile that apt-installs chromium / google-chrome-stable or sets PUPPETEER_EXECUTABLE_PATH
- Code calling puppeteer.launch({ headless: ... }) / chromium.launch() to take screenshots or render PDFs
- PDF generation via page.pdf() or libraries like html-pdf, wkhtmltopdf, weasyprint, Gotenberg
- Scraping stacks: cheerio + axios/got fetching HTML, or a Selenium/WebDriver grid (selenium-server, webdriver, hub/node containers)
- SaaS API keys / base URLs for browserless.io, scrapingbee, scrapfly, urlbox, prerender.io, browserbase, apify
- OG-image / social-card or invoice/receipt-PDF microservices; 'render', 'screenshot', 'pdf-service', 'snapshotter' service names
- Cron jobs that poll pages and diff DOM/text (price/stock monitoring, changelog scraping)
- ENV like BROWSERLESS_TOKEN, CHROME_BIN, PUPPETEER_*, SCRAPINGBEE_API_KEY

**Ideas:**
- Replace a Lambda/Docker Puppeteer service that generates OG images or invoice PDFs with a Worker bound to MYBROWSER (or a single POST to /browser-rendering/pdf).
- Swap a cheerio+axios scraper that breaks on JS-rendered SPAs for the /content or /markdown Quick Action, or use /json to extract structured data via a JSON schema instead of hand-writing selectors.
- Feed clean page text to an LLM/RAG pipeline by hitting /markdown or /crawl instead of running a separate headless-browser crawler.

**Pairs with:** Workers (host the controlling code / binding), Workflows or Queues (orchestrate/retry long scrape & crawl jobs), R2 (store generated screenshots/PDFs without egress fees), Workers AI / AI Gateway (pair with /json and /crawl AI extraction, or post-process scraped text), Durable Objects (hold a long-lived browser session for multi-step flows)

**Pricing:** Available on Workers Free and Paid. Free: 10 browser-minutes/day, 3 concurrent browsers. Paid: 10 browser-hours/month included then $0.09/additional hour; 10 concurrent browsers (monthly-averaged) included then $2.00/additional browser. Browser hours are shared across all methods; Quick Actions bill on browser hours only, Browser Sessions bill on both hours and concurrent browsers. (verify — drifts)

**Limits:**
- Concurrent browsers per account: 3 (Free) / 120 (Paid)
- New browser instances: 1 per 20s (Free) / 1 per second (Paid)
- Total requests: 1 per 10s (Free) / 10 per second (Paid); exceeding returns 429 Too many requests
- Browser idle timeout: 60s default; extendable up to 10 min via keep_alive; no fixed max lifetime while active
- Free crawl endpoint: 5 crawl jobs/day, max 100 pages per crawl
- .quickAction() requires compatibility_date 2026-03-24 or later

**Notes:** Headless Chrome only (Chromium engine) — no Firefox/WebKit despite the Playwright API surface; not a fit if you need cross-browser-engine testing. Cloudflare-specific bindings (@cloudflare/puppeteer/playwright) mean some lock-in vs vanilla Puppeteer, though Quick Actions are plain REST and portable. Tight Free-tier rate limits (1 req/10s, 10 min/day) make it dev/low-volume only; sustained scraping needs the Paid plan. Concurrency caps (120 on Paid) and per-second new-instance limits can bottleneck high-fan-out crawls. Product was recently renamed from 'Browser Rendering' to 'Browser Run' — older code/docs and the REST path still use 'browser-rendering'. Exact .quickAction() binding signature and full request payloads were not deeply verified this run beyond the endpoint list and config keys.

**Docs:** https://developers.cloudflare.com/browser-run/llms.txt, https://developers.cloudflare.com/browser-run/index.md, https://developers.cloudflare.com/browser-run/pricing/index.md, https://developers.cloudflare.com/browser-run/limits/index.md, https://developers.cloudflare.com/browser-run/get-started/index.md, https://developers.cloudflare.com/browser-run/examples/index.md

---

## Cloudflare Flagship
`flagship` · Feature Flags & Experimentation · confidence: `high` · lock-in: `portable`

**Is:** A managed feature-flag service that evaluates typed flags, targeting rules, and percentage rollouts locally inside Workers with no outbound HTTP call.

**Replaces:** A self-hosted LaunchDarkly/Unleash/Flagsmith deployment, or a hand-rolled flags system (config in KV/a DB + a polling client + a sticky-bucketing hash function + an admin UI). Most directly: paying for LaunchDarkly/Split/Statsig SaaS seats.

**Use it via:** Worker binding: add a `flagship` array in wrangler.jsonc — `"flagship": [{ "binding": "FLAGS", "app_id": "<APP_ID>" }]` (or `[[flagship]]` in wrangler.toml). Then `await env.FLAGS.getBooleanValue(key, default, context)` and the `getStringValue` / `getNumberValue` / `getObjectValue` variants. SDK: `@cloudflare/flagship` exposing `FlagshipServerProvider` (Workers/Node) and `FlagshipClientProvider` (browser) via the OpenFeature API. REST: `POST/GET/PATCH/DELETE https://api.cloudflare.com/client/v4/accounts/{account_id}/flagship/apps/{app_id}/flags` (Bearer token, scope: Flagship).

**Capabilities:**
- Local in-Worker flag evaluation via a native binding with zero outbound HTTP round-trip (config distributed over Workers KV + Durable Objects, propagates within seconds)
- Typed variations: boolean, string, number, and JSON object values, each flag with a designated default variation
- Targeting rules evaluated in order (first match wins) over an evaluation context (userId, country, plan, etc.), with 11 comparison operators (equality, comparison, string, array)
- Percentage rollouts with consistent hashing for sticky bucketing — same context always buckets the same way
- Per-flag enabled/disabled kill switch (disabled returns default regardless of rules)
- OpenFeature-compatible SDKs (@cloudflare/flagship) with server and client providers for Workers, Node.js, and browser — provider portability
- Audit/changelog history of flag changes
- Full REST API to create/update/delete/list apps and flags, plus flag evaluation, without the dashboard

**Detection signals — the lens fires on these:**
- npm deps: launchdarkly-node-server-sdk, @launchdarkly/node-server-sdk, launchdarkly-js-client-sdk, unleash-client, flagsmith, flagsmith-nodejs, @splitsoftware/splitio, statsig-node, @vercel/flags, @openfeature/server-sdk / @openfeature/web-sdk with a custom provider
- env vars: LAUNCHDARKLY_SDK_KEY, LD_SDK_KEY, UNLEASH_URL, UNLEASH_API_TOKEN, FLAGSMITH_ENVIRONMENT_KEY, SPLIT_API_KEY, STATSIG_SERVER_SECRET
- Hand-rolled flag patterns: a `flags` / `feature_flags` table or KV namespace read on every request; a config JSON in R2/KV polled on an interval; `if (FLAGS.newCheckout)` / `isFeatureEnabled(...)` helpers reading from process.env or a remote config fetch
- DIY sticky bucketing: murmurhash/xxhash/crc32 of a userId modulo 100 to gate a `% rollout`; cohort/allowlist arrays of user IDs checked inline
- An internal admin UI or Slack command that toggles booleans in a config store; envvar-driven `ENABLE_*` / `FEATURE_*` toggles requiring a redeploy to change
- Already on Cloudflare Workers (wrangler.jsonc / `export default { fetch }`) and gating behavior by user/country/plan — prime offload target since evaluation is local with no added latency

**Ideas:**
- Replace per-request reads of a KV/D1 'flags' table (and any redeploy-to-toggle env var flags) with a Flagship binding so flips happen from the dashboard/API in seconds with no cold redeploy
- Run a gradual rollout of a risky new code path (new checkout, new pricing engine) as a Flagship percentage rollout keyed on userId, with an instant kill switch if error rates spike
- Drop a paid LaunchDarkly/Split seat for a Workers-only app by swapping its OpenFeature provider for FlagshipServerProvider — keep the OpenFeature call sites, change only the provider

**Pairs with:** Workers, Workers KV, Durable Objects, Workers Analytics Engine (for logging which variation served / experiment exposure events), OpenFeature

**Pricing:** Not published — Flagship is in public beta (since 2026-05-26) and no pricing/billing page exists in the docs yet. Expect future metering on evaluations and/or stored config; today it is dashboard-creatable with no stated cost. (verify — drifts)

**Limits:**
- 10,000 apps per account (soft limit — raise via Cloudflare support)
- 5,000 flags per app (soft limit — raise via support)
- Condition nesting depth: 6 levels
- Flag configuration size: 25 MB per app
- Public beta — API and limits may change; max variations per flag, rule count, and rollout granularity are not documented

**Notes:** Public beta as of June 2026 — not yet GA, so treat for production-critical paths with caution and pin to the documented default-value fallback behavior. Strongest fit is Workers-native apps: evaluation is local (no outbound HTTP, no added latency), which is the headline advantage over LaunchDarkly/Split where the SDK streams/polls a vendor. It is NOT a full experimentation/A-B analytics platform — it serves variations and buckets users, but you bring your own metrics/exposure logging (e.g. Analytics Engine) to measure outcomes. For non-Cloudflare backends (pure Node.js/browser) the OpenFeature SDK works, but you lose the zero-round-trip edge benefit and take Cloudflare lock-in on flag config. Pricing is unverified — confirm before assuming free. Binding method names (getBooleanValue/getStringValue/getNumberValue/getObjectValue) are confirmed from get-started + concepts; details-variant methods and exact TypeScript types were listed in the llms.txt index but the methods/types sub-pages 404'd on .md fetch this run, so per-method signatures beyond getBooleanValue are inferred from the naming convention.

**Docs:** https://developers.cloudflare.com/flagship/llms.txt, https://developers.cloudflare.com/flagship/index.md, https://developers.cloudflare.com/flagship/get-started/index.md, https://developers.cloudflare.com/flagship/concepts/index.md, https://developers.cloudflare.com/flagship/reference/limits/index.md, https://developers.cloudflare.com/changelog/post/2026-05-26-public-beta/, https://developers.cloudflare.com/changelog/post/2026-06-10-api-reference/

---

## Cloudflare Fundamentals (Accounts, API Tokens, RBAC, Audit Logs, SCIM/SSO, 2FA)
`fundamentals-account-management` · Account, identity & access management · confidence: `high` · lock-in: `portable`

**Is:** The account-and-identity control plane for Cloudflare: scoped API tokens, member RBAC with roles/scopes/user-groups, audit logs, SCIM/SSO provisioning, and 2FA — the foundation every other Cloudflare API call authenticates against.

**Replaces:** Rolling your own access layer in front of Cloudflare — sharing one Global API Key, building custom role/permission tables, hand-managing who-can-touch-what, and scripting user onboarding/offboarding instead of using scoped tokens + SCIM.

**Use it via:** Base `https://api.cloudflare.com/client/v4`. Auth via `Authorization: Bearer <API_TOKEN>` (scoped tokens, preferred) or legacy `X-Auth-Email` + `X-Auth-Key` Global API Key; verify with `GET /user/tokens/verify`. Tokens, members, roles, and audit logs are managed through account/user endpoints; SCIM is configured against your IdP (Enterprise). Account-owned tokens supported for non-user automation.

**Capabilities:**
- Scoped API tokens with per-resource (account/zone) and per-action (Read vs Edit/CRUDL) permissions, IP filtering, and TTL; rollable and template-based; new tokens use a `cfut_` prefix for secret scanning
- Member management + RBAC: account/domain/resource-scoped roles, role scopes, and User Groups to apply shared policies to many members
- Audit Logs v2 capturing user and system actions, accessible via dashboard, API, or Logpush
- SCIM provisioning to auto-add/remove users and sync groups from Okta, Microsoft Entra, or Authentik (deprovision via active:false)
- SSO and social/email login; user-profile security including 2FA (security keys, TOTP, or email) and account recovery
- Account bootstrapping: create account, find Account/Zone IDs, set super administrator, abuse contact

**Detection signals — the lens fires on these:**
- CLOUDFLARE_API_KEY / X-Auth-Key + X-Auth-Email (Global API Key) in code or CI — a smell that scoped Bearer tokens should replace it
- A single shared Cloudflare credential used across many services instead of per-service scoped tokens
- Custom RBAC / permissions tables governing who can change DNS/WAF/Workers, duplicating Cloudflare roles + user groups
- Manual user onboarding/offboarding steps for Cloudflare access (no SCIM) with Okta/Entra/Authentik already in the stack
- Home-grown audit trails of infra changes that Audit Logs v2 (via Logpush) could provide natively
- Tokens with no TTL/IP restriction, or no token-rotation process
- Hardcoded account/zone IDs discovered ad hoc rather than read from the documented IDs flow

**Ideas:**
- Replace the shared Global API Key with narrowly-scoped, IP-restricted, TTL'd Bearer tokens per service and add a rotation routine
- Wire SCIM from Okta/Entra so Cloudflare access is granted/revoked automatically with the IdP instead of by hand
- Stream Audit Logs v2 via Logpush into your SIEM instead of maintaining a custom change-tracking log

**Pairs with:** terraform-provider, pulumi-provider, tenant-api, billing-usage

**Pricing:** Core account management, scoped API tokens, RBAC, and 2FA are included free with any account. Audit Logs v2 retention/Logpush and dashboard SCIM provisioning are Enterprise-gated features. (verify — drifts)

**Limits:**
- Dashboard SCIM provisioning is Enterprise-only and limited to Okta, Microsoft Entra, and Authentik (Zero Trust SCIM is a separate path)
- Removing a user from a SCIM group changes group membership but does NOT remove account membership — deactivation must come from the IdP
- Global API Key is legacy and full-access; it's a liability, not a feature to lean on
- Granular audit-log retention and some governance features depend on plan tier

**Notes:** Not a single product but the identity/access substrate under everything else — most valuable as a lens for spotting Global API Key usage, over-broad tokens, and hand-rolled RBAC/onboarding. SCIM and rich audit logging are Enterprise-gated, so recommendations should note plan requirements. Token auth format, base URL, cfut_ prefix, and SCIM IdP list (Okta/Entra/Authentik, Enterprise-only) confirmed from live pages this run.

**Docs:** https://developers.cloudflare.com/fundamentals/index.md, https://developers.cloudflare.com/fundamentals/api/get-started/create-token/index.md, https://developers.cloudflare.com/fundamentals/account/account-security/scim-setup/index.md, https://developers.cloudflare.com/fundamentals/llms.txt

---

## Cloudflare Pages
`cloudflare-pages` · Hosting / Full-stack deployment · confidence: `high` · lock-in: `portable`

**Is:** A git-connected platform that builds your frontend and instantly deploys static assets plus serverless backend code (Pages Functions) to Cloudflare's global edge.

**Replaces:** Vercel / Netlify hosting bills (plus the Jamstack stack of an S3 bucket + CloudFront + a CI build runner + a Lambda for API routes)

**Use it via:** Deploy via git push, `npx wrangler pages deploy <dir>`, or `npm create cloudflare@latest` (C3). Functions live in a `functions/` dir and export `onRequest`/`onRequestGet` handlers receiving a `context` with `context.env.<BINDING>` and `context.params`. Bindings declared in `wrangler.toml`/`wrangler.jsonc` (keys: `kv_namespaces`, `d1_databases`, `r2_buckets`, `durable_objects`, `vectorize_indexes`, `ai`, `service_bindings`, `queues.producers`, `hyperdrive`, `analytics_engine_datasets`, `vars`) or in dashboard Settings > Bindings. Local dev: `npx wrangler pages dev <output_dir>`.

**Capabilities:**
- Git integration (GitHub/GitLab): auto-build and deploy on every push to the production branch
- Preview deployments: every non-production branch and PR gets its own unlimited, live preview URL
- Pages Functions: file-based serverless routes (functions/ directory) for SSR and APIs, no dedicated server
- Direct Upload + C3 (create-cloudflare CLI) and wrangler pages deploy as alternatives to git
- Framework auto-detection and guides (React, Next.js, Astro, Hugo, SvelteKit, Remix, etc.)
- Static assets served free and unlimited from the edge CDN with automatic cache
- _headers and _redirects files for declarative header/redirect rules
- Full Cloudflare bindings available to Functions: KV, D1, R2, Durable Objects, Vectorize, Workers AI, Queues, Hyperdrive, Service bindings, Analytics Engine, secrets/vars
- Custom domains with automatic TLS (100 on Free, up to 500 Enterprise)

**Detection signals — the lens fires on these:**
- vercel.json, netlify.toml, or .netlify/ in repo root (paying a competitor for the same workflow)
- Next.js/Astro/SvelteKit/Remix/Nuxt project with a separate API hosted elsewhere (Functions could co-locate it)
- A GitHub Actions / CircleCI workflow whose only job is `npm run build` + upload static assets to S3/CloudFront
- Express/Fastify server that exists only to serve a built SPA plus a handful of /api routes
- @cloudflare/next-on-pages, @astrojs/cloudflare, or wrangler already in devDependencies (partial adoption)
- _redirects / _headers files, or a functions/ directory (already Pages-shaped)
- aws-cdk / serverless.yml standing up S3 + CloudFront + Lambda@Edge for a static-site-with-API
- create-react-app / Vite SPA deployed as a static bundle with a Procfile or Dockerfile that just runs nginx

**Ideas:**
- Move a Vercel/Netlify-hosted Next.js or Astro app to Pages to consolidate hosting under Cloudflare and drop egress/seat costs; preview URLs come free per branch.
- Collapse a separate 'API server' (Express on a VPS/Render) into Pages Functions co-located with the frontend, binding D1 for the DB and KV for sessions instead of a managed Postgres + Redis box.
- Use preview deployments as ephemeral staging environments for every PR instead of standing up and tearing down review apps manually.

**Pairs with:** D1 (SQL database binding for Functions), KV (sessions, edge config, cache), R2 (user uploads / static media, zero egress), Workers AI + Vectorize (AI features and RAG from Functions), Durable Objects (only via Workers — a reason to migrate), Hyperdrive (connect Functions to existing Postgres/MySQL)

**Pricing:** Free tier: unlimited static requests/bandwidth, 500 builds/month, 1 concurrent build, unlimited preview deployments, 100 custom domains. Pages Functions invocations are NOT free — they count against the shared Workers request quota (Free: 100,000 requests/day across Pages Functions + Workers combined, resets midnight UTC); Paid follows the Workers Standard usage model billed per request + CPU time. Build tiers: Pro 5,000/mo (5 concurrent), Business 20,000/mo (20 concurrent). (verify — drifts)

**Limits:**
- Files per deployment: 20,000 (Free) / 100,000 (Paid)
- Max single asset size: 25 MiB
- Build timeout: 20 minutes
- Soft limit of 100 projects per account
- _headers: max 100 rules; _redirects: max 2,000 static + 100 dynamic (2,100 total)
- Builds/month and concurrent builds capped by plan (500/1 Free up to 20,000/20 Business)
- Custom domains per project: 100 Free, 250 Pro, 500 Business/Enterprise
- Static assets are free and unlimited, but every Functions invocation consumes the Workers request quota

**Notes:** Honest caveats: (1) Cloudflare is steering new full-stack work toward Workers Static Assets, not Pages. The migrate-from-pages guide states Workers has a 'distinctly broader set of features' — Durable Objects, Cron Triggers, Email Workers, Queue Consumers, Logpush, Tail Workers, Source Maps, fuller Observability are Workers-only and NOT available to Pages Functions. For a greenfield app needing any of those, recommend Workers with static assets over Pages; Pages remains excellent for git-driven static/SSR sites and existing Pages projects. (2) Cost is NOT 'free static hosting' end-to-end — only static assets are free; dynamic Functions traffic bills exactly like Workers, so a function-heavy app is priced as a Workers app, not as free CDN hosting. (3) Build minutes are gated by a monthly build COUNT (not minutes) with a hard 20-min per-build timeout; very long monorepo builds can hit it. (4) Lock-in: Functions' binding model (context.env, wrangler config) is Cloudflare-specific; framework adapters (@cloudflare/next-on-pages, @astrojs/cloudflare) ease but don't eliminate portability cost. (5) Could not verify exact paid per-request/CPU rates from the Pages pricing page — it defers to the Workers Standard usage model; confirm current Workers pricing separately.

**Docs:** https://developers.cloudflare.com/pages/llms.txt, https://developers.cloudflare.com/pages/index.md, https://developers.cloudflare.com/pages/functions/bindings/index.md, https://developers.cloudflare.com/pages/functions/pricing/index.md, https://developers.cloudflare.com/pages/platform/limits/index.md, https://developers.cloudflare.com/pages/get-started/git-integration/index.md, https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/index.md

---

## Cloudflare Pulumi Provider
`pulumi-provider` · Infrastructure as Code · confidence: `high` · lock-in: `portable`

**Is:** Manage Cloudflare resources as code in a real programming language (TypeScript, Python, Go, C#, Java) via the Pulumi Cloudflare provider, instead of HCL.

**Replaces:** Custom provisioning scripts (or a Terraform setup the team doesn't want) — letting you define Cloudflare infra with the same language, loops, functions, and tests as the rest of your app, with state/secrets handled by Pulumi Cloud or ESC.

**Use it via:** Per-language packages: npm `@pulumi/cloudflare`; Python `pulumi_cloudflare` (>=5.38,<6.0.0); Go `github.com/pulumi/pulumi-cloudflare/sdk/v3/go/cloudflare`; .NET `Pulumi.Cloudflare`; Java Maven `com.pulumi:cloudflare`. Auth via Pulumi config key `cloudflare:apiToken` (or `CLOUDFLARE_API_TOKEN` env var); resources like `new cloudflare.WorkersScript(...)`.

**Capabilities:**
- Provision Cloudflare resources (zones, DNS, Workers, KV, R2, rules) from TypeScript/JavaScript, Python, Go, .NET, Java, or YAML
- Use native language constructs — loops, conditionals, functions, classes, npm/pip packages — to generate infra instead of HCL
- State + secret management via Pulumi Cloud, or centralized config/secrets via Pulumi ESC (`pulumi env set $E --secret pulumiConfig.cloudflare:apiToken`)
- Deploy Workers via Pulumi (cloudflare.WorkersScript) and combine with Wrangler in the same workflow
- Pulumi AI can scaffold Cloudflare resource code from natural language

**Detection signals — the lens fires on these:**
- Pulumi.yaml / Pulumi.<stack>.yaml in the repo
- Dependency on `@pulumi/cloudflare`, `pulumi_cloudflare`, `pulumi-cloudflare`, or `Pulumi.Cloudflare`
- `import * as cloudflare from "@pulumi/cloudflare"` or `import pulumi_cloudflare` in IaC code
- pulumi config / ESC entries referencing `cloudflare:apiToken`
- A team standardized on Pulumi for AWS/GCP that still provisions Cloudflare by hand or via curl
- CLOUDFLARE_API_TOKEN consumed by a Pulumi program rather than Terraform

**Ideas:**
- Generate N DNS records / WAF rules programmatically with a loop in TypeScript instead of copy-pasting HCL blocks
- Centralize the Cloudflare API token and account ID in Pulumi ESC so Workers + infra share one secret source
- Stand up a per-PR preview stack (zone settings + Worker) using Pulumi's language-native stack references

**Pairs with:** workers-iac, r2, fundamentals-api-tokens, terraform-provider

**Pricing:** Pulumi provider/CLI is free and open-source; you pay for the Cloudflare resources provisioned. Pulumi Cloud (managed state/secrets) and ESC have their own free tier + paid plans charged by Pulumi, not Cloudflare. (verify — drifts)

**Limits:**
- The Cloudflare Pulumi provider is bridged from the Terraform provider, so it inherits v5 resource shapes and tends to track slightly behind
- Adds Pulumi (and often Pulumi Cloud/ESC) as a dependency/vendor on top of Cloudflare
- Smaller community and fewer Cloudflare-specific examples than the first-party Terraform path
- Pulumi docs pages here are thin; deep resource reference lives in Pulumi's own registry, not Cloudflare docs

**Notes:** Best fit for teams already invested in Pulumi or who strongly prefer general-purpose languages over HCL. For Cloudflare-only shops, the first-party Terraform provider is more directly supported and documented. Because it's a Terraform-bridged provider, evaluate it as 'Terraform capabilities, different SDK.' Package versions/auth confirmed from the live Hello-World tutorial this run; current major aligns with provider v5.

**Docs:** https://developers.cloudflare.com/pulumi/index.md, https://developers.cloudflare.com/pulumi/installing/index.md, https://developers.cloudflare.com/pulumi/tutorial/hello-world/index.md

---

## Cloudflare Radar
`cloudflare-radar` · Internet Intelligence / Data API · confidence: `high` · lock-in: `portable`

**Is:** A free API and dashboard exposing Cloudflare's aggregated, anonymized view of global Internet traffic, attacks, BGP, DNS, outages, and domain rankings.

**Replaces:** Paying for a threat-intel / internet-measurement data feed (e.g. Cisco Umbrella popularity list, commercial BGP/outage monitors, Alexa-style domain rankings), or scraping and maintaining your own internet-health datasets.

**Use it via:** REST: GET https://api.cloudflare.com/client/v4/radar/http/summary/device_type?dateRange=7d&format=json with header Authorization: Bearer <API_TOKEN>. Token needs Account > Radar = Read. Endpoints follow /radar/{category}/{sub}/{metric} (e.g. /radar/dns/top/locations, /radar/ranking/...). Also a Radar MCP server.

**Capabilities:**
- REST API under /client/v4/radar/{category}/{subcategory}/{metric}: HTTP traffic, DNS (top locations/domains from 1.1.1.1), NetFlows, BGP anomalies/route leaks, L3/L7 attack trends, Internet outages, URL Scanner, domain ranking datasets
- Time-series + summary endpoints with dateRange, location, format, botClass (LIKELY_HUMAN / LIKELY_AUTOMATED) filters
- Domain ranking datasets (popularity ordering derived from aggregated DNS)
- URL Scanner to inspect a page's security/performance/tech footprint
- Embeddable widgets and configurable alerts; quarterly DDoS report data
- Response envelope: {success, errors, result{ ...data, meta{ dateRange, normalization, aggInterval }}}
- Data licensed CC BY-NC 4.0

**Detection signals — the lens fires on these:**
- Cron jobs or scrapers building a 'top domains' / domain-popularity list
- Code ingesting Cisco Umbrella top-1m, Majestic, or Tranco CSVs on a schedule
- Custom BGP monitoring (RIPE RIS / RouteViews parsing) or homegrown route-leak/hijack alerting
- Internet-outage or ASN-reachability dashboards stitched from third-party status feeds
- A URL-reputation / page-scanning microservice (urlscan.io API usage)
- Manual collection of attack-trend or traffic-share stats for reports/blog posts
- Anything charting 'percent of traffic by country / device / bot' that you compute yourself

**Ideas:**
- Replace a scheduled Tranco/Umbrella CSV ingestion with live calls to Radar's domain ranking datasets.
- Wire Radar BGP-anomaly and outage endpoints into an internal NOC dashboard instead of parsing RouteViews yourself.
- Use the Radar MCP server to let an internal agent answer 'what does global traffic look like for X right now' without standing up a data pipeline.

**Pairs with:** 1.1.1.1 (DNS data source), URL Scanner, Workers (proxy/cache Radar calls), Radar MCP server

**Pricing:** Radar API is free and available on all plans; requires a Cloudflare API token scoped Account > Radar: Read (verify — drifts).

**Limits:**
- Data is aggregated/anonymized and normalized — good for trends and reporting, not per-user or per-IP forensics
- CC BY-NC 4.0: non-commercial license terms on the data — check before embedding in a paid product
- Rate limits not stated on the pages fetched; assume standard Cloudflare API limits and verify

**Notes:** API base, token scope (Account>Radar:Read), endpoint pattern, botClass filter, and the dataset catalog are verified from fetched pages. GraphQL access was NOT confirmed (overview says REST + dashboard + MCP; the index does not list a GraphQL doc) — do not claim GraphQL. The CC BY-NC 4.0 license is the main gotcha for commercial reuse. Not a replacement for your own first-party analytics — this is Cloudflare's network-wide view, not your site's.

**Docs:** https://developers.cloudflare.com/radar/llms.txt, https://developers.cloudflare.com/radar/index.md, https://developers.cloudflare.com/radar/get-started/first-request/index.md, https://developers.cloudflare.com/radar/investigate/dns/index.md

---

## Cloudflare Randomness Beacon (drand / League of Entropy)
`randomness-beacon` · Verifiable randomness / cryptography service · confidence: `medium` · lock-in: `portable`

**Is:** A public distributed randomness beacon (drand) that emits collective, publicly verifiable, unbiasable, unpredictable random values at fixed intervals using threshold BLS signatures — Cloudflare is a node in the multi-party League of Entropy.

**Replaces:** Trusting a single server's local RNG (crypto.randomBytes / /dev/urandom) for anything that must be provably fair to third parties — e.g. building your own commit-reveal scheme or paying for an audited RNG/lottery oracle.

**Use it via:** drand HTTP API — fetch beacon rounds over HTTP and verify against the chain's group/public key (round, randomness, signature, previous_signature). Cloudflare's developer docs are thin stubs that redirect to drand.love/developer for the concrete endpoint paths and client libraries (Go drand client, JS).

**Capabilities:**
- Distributed beacon: multiple independent orgs jointly produce randomness; no single party can predict or bias the output below the threshold t
- Publicly verifiable: anyone can check a value against the group public key via BLS pairing check e(H(m),S)=e(sigma,g2)
- Unbiasable + unpredictable: threshold cryptography (BLS12-381) means < t signers can't influence the result
- Chained mode (each round signs H(round || prev_sig)) or unchained mode (signs H(round)) for precomputable messages
- Members can be added/removed via resharing while keeping the same public key, so verification stays stable

**Detection signals — the lens fires on these:**
- Lotteries/raffles/airdrops/NFT trait reveals seeded by Math.random(), crypto.randomBytes, or a single backend's RNG that users are asked to 'just trust'
- Home-rolled commit-reveal randomness schemes (hash-then-reveal) to prove fairness
- On-chain VRF usage (Chainlink VRF, drand) for off-chain leader election / sharding / sortition — drand HTTP can serve the same role off-chain
- Distributed-systems leader election or random sampling that needs an external, auditable entropy source
- Anything advertising 'provably fair' to end users without a verifiable public source

**Ideas:**
- Seed a provably-fair draw (raffle, giveaway, randomized audit selection) from a beacon round so users can independently verify it wasn't rigged
- Use beacon values for unbiased leader election / committee sampling in a distributed system
- Add a verifiable randomness step to a commit-reveal flow instead of trusting a single server's RNG

**Pairs with:** Workers (fetch + verify a beacon round at request time), Time Services (sibling 'Internet infrastructure' public good), Smart-contract / VRF workflows

**Pricing:** Public good / free — drand is a free distributed public-randomness service (League of Entropy); no Cloudflare billing surfaced. (verify — drifts)

**Limits:**
- It is PUBLIC randomness — every value is published and predictable-after-the-fact; never use a past/known round as a secret key or unguessable token
- Verification correctness is on you (check signatures against the right group public key/chain hash)
- Cloudflare's own docs redirect to drand.love for operational specifics (endpoint URLs, exact round cadence, client setup) — those details were not confirmed on Cloudflare-hosted pages this run
- Round cadence (commonly cited as ~30s for the mainnet chain) was NOT verified from the fetched Cloudflare pages

**Notes:** Cloudflare runs a node in a multi-org beacon (League of Entropy); it is not a Cloudflare-proprietary product, and the canonical developer docs live at drand.love. Crypto property: values are publicly verifiable but also publicly known once published — great for fairness/auditability, wrong for secrets. Confidence is medium because the concrete HTTP endpoint and 30s cadence weren't confirmable on Cloudflare's own .md pages (they stub out to drand.love).

**Docs:** https://developers.cloudflare.com/randomness-beacon/llms.txt, https://developers.cloudflare.com/randomness-beacon/index.md, https://developers.cloudflare.com/randomness-beacon/cryptographic-background/randomness-generation/index.md

---

## Cloudflare Tenant Platform (Tenant API)
`tenant-api` · Multi-tenant provisioning / Partner platform · confidence: `high` · lock-in: `portable`

**Is:** A partner-gated provisioning API for resellers, MSPs, and SaaS platforms to programmatically create and manage many isolated customer Cloudflare accounts (and their subscriptions) under one tenant.

**Replaces:** A home-grown multi-tenant control plane — your own per-customer account abstraction, manual onboarding runbooks, and bespoke billing/entitlement glue layered on top of single-account Cloudflare API calls.

**Use it via:** REST under base `https://api.cloudflare.com/client/v4`. Core call `POST /accounts` ({name, type, unit:{id}}); manage via `PUT/DELETE /accounts/{account_id}`; then `POST /zones`, subscription, and membership endpoints. Tenant access is granted as entitlements on your partner account; standard Cloudflare auth (Bearer token / X-Auth-Email + X-Auth-Key).

**Capabilities:**
- Programmatically create customer accounts under your tenant: `POST /accounts` with name, type (standard|enterprise), and unit.id
- Update and delete managed accounts (`PUT /accounts/{id}`, `DELETE /accounts/{id}`; deletion cascades to zones/resources)
- Attach Know-Your-Customer metadata per account (business_name, business_address, business_email, business_phone, external_metadata)
- Manage zone- and account-level subscriptions for each customer (assign plans to provisioned accounts)
- Group accounts under tenant 'units' (unit.id / unit_tag) for partners administering multiple tenants
- Built into the standard Cloudflare Client v4 API library / SDKs

**Detection signals — the lens fires on these:**
- A SaaS/agency platform looping over customers and calling `POST /accounts` or storing a `cloudflare_account_id` per customer
- Your own 'tenant'/'workspace'/'organization' table that maps 1:1 to a Cloudflare account you create by hand
- Manual onboarding checklists: 'create a Cloudflare account for the client, add their domain, set their plan'
- Reseller/white-label DNS, CDN, or SSL-for-SaaS offering managing many end-customer zones
- Code juggling many separate Cloudflare API tokens, one per customer account
- external_metadata / business_* fields being tracked in your DB but not pushed to Cloudflare

**Ideas:**
- Automate client onboarding: create the customer's Cloudflare account, zone, and subscription in one provisioning flow
- Map your app's tenant/org model directly onto Cloudflare accounts with unit.id for clean per-customer isolation and billing
- Stamp KYC/business metadata onto each managed account so support and compliance can reconcile customers to Cloudflare accounts

**Pairs with:** fundamentals-account-management, billing-usage, terraform-provider

**Pricing:** No self-serve price; access requires a signed partner agreement (MSP: partners@cloudflare.com; Agency: agency@cloudflare.com) and Cloudflare-granted entitlements. Underlying customer subscriptions are billed per the partner/reseller commercial terms. (verify — drifts)

**Limits:**
- Gated to approved Channel/Alliance partners, resellers, and SaaS providers — not available to ordinary accounts
- Requires a business/contractual relationship and onboarding with Cloudflare, not just an API token
- Docs are provisioning-focused; subscription attachment is lightly specified in the API (mostly described via dashboard steps)
- This is the account-fleet control plane, not a data-plane product; it does not by itself isolate customer traffic beyond account boundaries

**Notes:** The right answer specifically when a platform is creating Cloudflare accounts on behalf of end customers at scale; overkill for a single-org product. Heavy lock-in/relationship: you're entering Cloudflare's partner program. Could not verify exact subscription-attachment request bodies or per-unit token semantics from the fetched pages — flagged as not fully specified. Confidence high on the provisioning endpoints and partner-gating, medium on subscription API details.

**Docs:** https://developers.cloudflare.com/tenant/index.md, https://developers.cloudflare.com/tenant/get-started/index.md, https://developers.cloudflare.com/tenant/how-to/manage-accounts/index.md

---

## Cloudflare Terraform Provider
`terraform-provider` · Infrastructure as Code · confidence: `high` · lock-in: `portable`

**Is:** Official Terraform provider (cloudflare/cloudflare) that manages every Cloudflare resource — DNS, WAF, Workers, R2, Access, Load Balancing — as declarative HCL in version control.

**Replaces:** Hand-rolled bash/Python scripts that POST to api.cloudflare.com/client/v4 to create DNS records, WAF rules, and Workers, plus the ad-hoc 'click-ops' dashboard changes those scripts try to reconcile.

**Use it via:** Terraform required_providers source `cloudflare/cloudflare` (registry.terraform.io); current major is v5 (v5.0.0 GA Feb 2025, stable). Provider authenticates from `CLOUDFLARE_API_TOKEN` env var (or api_token in the provider block). Remote state via `backend "s3"` pointed at `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` with R2 access_key/secret_key and skip_* flags.

**Capabilities:**
- Declarative management of DNS records, zones, page/cache/transform/origin/config rules, WAF custom + managed rulesets, rate limiting
- Manage Workers scripts, routes, KV, R2 buckets, Durable Object bindings, and other developer-platform resources as code (workers/platform/infrastructure-as-code)
- Import existing Cloudflare resources into state with `terraform import` + cf-terraforming to bootstrap config from a live account
- State stored remotely in Cloudflare R2 via the S3-compatible `backend "s3"` block (region="auto", custom endpoints)
- v5 provider is auto-generated from the Cloudflare OpenAPI schema, so new API features land in the provider quickly
- tf-migrate CLI + state upgraders (v5.19+) automate the v4->v5 resource renames (cloudflare_record -> cloudflare_dns_record, etc.) with zero-downtime `moved` blocks

**Detection signals — the lens fires on these:**
- *.tf / *.tf.json files with `provider "cloudflare"` or `cloudflare/cloudflare` in required_providers
- v4-style resource names that need migration: `cloudflare_record`, `cloudflare_access_application`, `cloudflare_zone_settings_override`
- Scripts shelling out to `curl ... api.cloudflare.com/client/v4/zones/.../dns_records` or using the cloudflare-python / cloudflare-go SDK purely to provision infra
- CLOUDFLARE_API_TOKEN / CLOUDFLARE_API_KEY in CI secrets used by deploy scripts rather than by Terraform
- Manual runbooks / README steps that say 'in the Cloudflare dashboard, add a DNS record / WAF rule'
- A separate Terraform setup (AWS/GCP) where Cloudflare is the one provider still managed by hand
- backend.tf using AWS S3 for state while the team already pays for R2 (could consolidate state into R2)

**Ideas:**
- Import the team's existing DNS zone + WAF rules into Terraform with cf-terraforming so config and reality stop drifting
- Move Terraform state off an S3 bucket into R2 using the S3-compatible backend to drop AWS state-storage + egress
- Run tf-migrate to upgrade a stuck v4 configuration to v5 before the resources diverge further

**Pairs with:** r2, workers-iac, fundamentals-api-tokens, pulumi-provider

**Pricing:** The provider is free/open-source; you pay only for the underlying Cloudflare resources it provisions. R2 state storage bills as normal R2 (storage + Class A/B operations; R2 has no egress fee). (verify — drifts)

**Limits:**
- v5 is a near-total rewrite of v4: 40+ resources renamed and attributes restructured — migrating large/module-based configs is non-trivial even with tf-migrate
- tf-migrate currently covers only the most common resources; module-heavy configs may need manual work
- Provider tracks the REST API, so newer/beta products may lag or expose rough auto-generated schemas
- Rule/ruleset resources can churn rule IDs in state (documented troubleshooting case)

**Notes:** Strongest, most mature IaC option for Cloudflare and the default recommendation for teams already on Terraform. Not the right tool for one-off imperative tasks or for app deploys (use Wrangler for Workers code/bundling; Terraform manages the surrounding infra). Lock-in is low — it is just the public API in HCL. Confirmed v5 GA and tf-migrate from live changelog this run.

**Docs:** https://developers.cloudflare.com/terraform/index.md, https://developers.cloudflare.com/terraform/installing/index.md, https://developers.cloudflare.com/terraform/advanced-topics/remote-backend/index.md, https://developers.cloudflare.com/changelog/post/2026-04-24-tf-migrate-tool-released/, https://developers.cloudflare.com/changelog/post/2025-02-03-terraform-v5-provider/

---

## Cloudflare Time Services (NTP / NTS / Roughtime)
`time-services` · Time synchronization / authenticated time · confidence: `high` · lock-in: `portable`

**Is:** A free public suite of time services on Cloudflare's anycast network: plain NTP at time.cloudflare.com, cryptographically authenticated time via NTS (TLS-backed, MITM-resistant), and the Roughtime authenticated-time protocol.

**Replaces:** Pointing servers at random pool.ntp.org hosts or a single upstream NTP server with no authentication — i.e. trusting unauthenticated time and rolling your own monitoring for clock drift / NTP spoofing.

**Use it via:** Network protocols, not an HTTP/Worker API. NTP/NTS: hostname `time.cloudflare.com` in your OS/chrony/NTPsec/ntpd-rs config. Roughtime: query `roughtime.cloudflare.com:2003` with public key `0GD7c3yP8xEc4Zl2zeuN2SlLvDVVocjsPSL8/Rl/7zg=` using the Go client `github.com/cloudflare/roughtime/cmd/getroughtime` (public key also fetchable via `dig TXT roughtime.cloudflare.com`).

**Capabilities:**
- Free anycast NTP: configure `server time.cloudflare.com iburst` (chrony/ntpd) or `NTP=time.cloudflare.com` (systemd-timesyncd); part of pool.ntp.org
- IPv4 + IPv6 anycast: 162.159.200.1, 162.159.200.123, 2606:4700:f1::1, 2606:4700:f1::123
- NTS (Network Time Security): authenticated time via a TLS key-exchange (same web PKI) then authenticated NTP packets — protects against MITM clock manipulation
- NTS clients supported: chrony, NTPsec, ntpd-rs (point them at time.cloudflare.com)
- Roughtime: Google-designed authenticated time protocol with cryptographic proof; only needs ~10s accuracy to defeat e.g. expired-cert attacks

**Detection signals — the lens fires on these:**
- ntp.conf / chrony.conf pointing at *.pool.ntp.org or a single unauthenticated NTP server
- systemd-timesyncd with default/ISP NTP and no NTS
- Security/compliance contexts (TLS cert validation, TOTP/2FA, JWT exp, log timestamps) that silently depend on unauthenticated NTP
- Custom clock-drift alerting or 'our time got skewed' incident runbooks (NTS hardens the source)
- Existing Roughtime usage pinned to the old roughtime.cloudflare.com:2002 endpoint (deprecated)

**Ideas:**
- Switch fleet NTP to time.cloudflare.com over anycast for low-latency, well-run time sync
- Harden security-sensitive hosts with NTS (chrony/NTPsec/ntpd-rs) so an on-path attacker can't shift the clock and trick cert/2FA/JWT validation
- Use Roughtime where you want cryptographically attestable 'roughly correct' time for audit logs

**Pairs with:** Any OS/server fleet, TLS / PKI (NTS reuses web PKI), Randomness Beacon (sibling public-good infra service)

**Pricing:** Free public service (NTP/NTS offered free on Cloudflare's anycast network; Roughtime free/beta). (verify — drifts)

**Limits:**
- These are public network services, not a programmable product — no Worker binding/SDK; you point existing time daemons at hostnames
- Roughtime is beta and its root public key may change; bookmark the usage page for current credentials
- Roughtime endpoint nuance: usage page lists roughtime.cloudflare.com:2003, while the OLD server roughtime.cloudflare.com:2002 was deprecated 2024-06-30 — make sure to use :2003
- NTS requires a client that supports it (chrony/NTPsec/ntpd-rs); stock timesyncd may not

**Notes:** Not a 'stop building this yourself' in the SaaS sense — it's a better, authenticated, free endpoint to point existing NTP infrastructure at. The real value flag is NTS for security-sensitive systems (unauthenticated NTP is a genuine attack surface for cert/2FA/token validation). Roughtime is the weakest leg: beta, key can rotate, and the historical :2002 server was already deprecated (2024-06-30) — recommend NTS over Roughtime for most uses. time.cloudflare.com is part of pool.ntp.org.

**Docs:** https://developers.cloudflare.com/time-services/llms.txt, https://developers.cloudflare.com/time-services/ntp/usage/index.md, https://developers.cloudflare.com/time-services/nts/index.md, https://developers.cloudflare.com/time-services/roughtime/usage/index.md, https://developers.cloudflare.com/time-services/roughtime/deprecation/index.md

---

## Cloudflare Zaraz
`zaraz` · Tag management & third-party script loading · confidence: `high` · lock-in: `portable`

**Is:** Loads third-party tools (analytics, ad pixels, chat, marketing tags) in the cloud at Cloudflare's edge instead of shipping their scripts to the browser, with a built-in consent manager.

**Replaces:** Google Tag Manager + Segment (client-side script soup) — and the per-vendor <script> tags / dataLayer plumbing a dev hand-wires for GA4, Meta Pixel, TikTok, HubSpot, etc.

**Use it via:** Configured per-zone in the Cloudflare dashboard (Zaraz section), no Worker binding required. Client: load Zaraz on the zone, then call window.zaraz.track('event', {...}), zaraz.set('k', v), zaraz.ecommerce(...) inside <body>. Server: enable HTTP Events API at a custom path (Settings > Endpoints), then POST JSON {"events":[{"client":{"__zarazTrack":"...",...},"system":{...}}]} to e.g. https://example.com/zaraz/api. Consent: zaraz.showConsentModal(), zaraz.consent API.

**Capabilities:**
- Server-side / edge execution of third-party tags so vendor JS doesn't run on the client (near-zero performance hit, fewer third-party scripts in the page)
- Native integrations for common vendors: GA4, Google Ads, Facebook/Meta Pixel, TikTok, Bing, LinkedIn Insight, Pinterest, Twitter Pixel, Amplitude, Mixpanel, Snowplow, Segment, HubSpot, Impact Radius
- Web API for client-side events: zaraz.track (events), zaraz.set (shared vars), zaraz.ecommerce, plus debug mode — a replacement for ad-hoc dataLayer.push / gtag() calls
- HTTP Events API for server-side / mobile event ingestion (transactions, sign-ups), batched via an events[] array
- Built-in Consent Management Platform: auto consent modal, purpose-based tool blocking until opt-in, first-party-cookie preference storage, zaraz.showConsentModal(), IAB TCF compliance support
- Custom integrations (Custom HTML, Custom Image, HTTP Request) and proprietary Managed Components for tools without a native integration
- Triggers/rules engine + Monitoring API for usage and event observability

**Detection signals — the lens fires on these:**
- Google Tag Manager on the page: <script src="https://www.googletagmanager.com/gtm.js">, GTM-XXXXXXX container IDs, dataLayer.push(...)
- gtag.js / GA4: gtag('config','G-...'), gtag('event',...), window.gtag, react-ga / react-ga4 npm packages
- Vendor pixel snippets inline in HTML/head: fbq('track',...) (Meta Pixel), ttq.track (TikTok), _linkedin_partner_id, snaptr, pintrk, twq
- Segment / CDP in the bundle: analytics.js, analytics.track(...), @segment/analytics-next, window.analytics, SEGMENT_WRITE_KEY env var
- A pile of third-party <script async> tags loaded directly on the client (analytics, chat widgets, marketing automation) hurting Lighthouse / Core Web Vitals
- Hand-rolled cookie/consent banners or paid CMP SDKs: @onetrust, OneTrust autoblock script, Cookiebot (cookiebot.com/uc.js), Osano, Klaro, CookieYes, react-cookie-consent
- Per-vendor server-side conversion plumbing built by hand (e.g. custom Meta Conversions API / GA4 Measurement Protocol POST calls) to dodge ad blockers
- Tracking IDs scattered across components: GA_MEASUREMENT_ID, FB_PIXEL_ID, MIXPANEL_TOKEN, NEXT_PUBLIC_GTM_ID env vars

**Ideas:**
- Move all client-side analytics/ad pixels (GA4, Meta, TikTok) off the browser into Zaraz to cut third-party JS and improve LCP/INP without losing tracking.
- Replace a separately-licensed consent banner (OneTrust/Cookiebot/Osano) with Zaraz's built-in CMP that blocks each tool until its purpose is consented, and report IAB TCF.
- Fire server-side conversion events (purchases, sign-ups) through the Zaraz HTTP Events API from the backend so they survive ad blockers, instead of trusting browser pixels.

**Pairs with:** Cloudflare Web Analytics (privacy-first first-party analytics), Workers / Pages (origin the zone fronts), Cloudflare CDN + Core Web Vitals tooling (the speed win Zaraz feeds into)

**Pricing:** Free: 1,000,000 Zaraz Events per Cloudflare account per month. Paid: $5/month per additional 1,000,000 events. A 'Zaraz Event' = a page view, a zaraz.track call, or similar interaction sent to Zaraz. All features on all plans; usage warnings at 50/80/90% and service disables past the free limit unless paid billing is enabled. (verify — drifts)

**Limits:**
- HTTP Events API is disabled by default and must be enabled at a custom path; security relies on the path being unguessable rather than a documented auth token (auth mechanism not specified in the fetched docs)
- Billing is per-event, so very high-traffic sites can rack up events fast (every page view + every track call counts)
- Best fit for sites already proxied through Cloudflare (zone-level feature); not a drop-in for apps not on Cloudflare's network
- Vendor coverage is broad but finite — anything without a native integration needs Custom HTML/Image/HTTP Request or a Managed Component

**Notes:** Honest caveats: this is a tag-management / third-party-loading layer, not an analytics product itself — it routes data to vendors you still configure. 'Server-side' here means edge-side tag execution; whether a given vendor's events fully bypass the client depends on that tool's Managed Component. Lock-in is light (it's config, not code), but it's a zone-level Cloudflare feature so it only makes sense if your traffic is already on Cloudflare. Could not verify from the fetched pages: exact zaraz.* method signatures, the precise IAB TCF version/cert, or HTTP Events API authentication details beyond 'use a unique path'. Not the right tool if the team wants a self-hosted/open CDP or needs warehouse-native event piping — Segment/RudderStack/Snowplow still own that lane.

**Docs:** https://developers.cloudflare.com/zaraz/llms.txt, https://developers.cloudflare.com/zaraz/index.md, https://developers.cloudflare.com/zaraz/pricing-info/index.md, https://developers.cloudflare.com/zaraz/http-events-api/index.md, https://developers.cloudflare.com/zaraz/consent-management/index.md, https://developers.cloudflare.com/zaraz/web-api/index.md, https://developers.cloudflare.com/zaraz/reference/supported-tools/index.md

---

## Resource Tagging
`resource-tagging` · Platform / Governance & FinOps · confidence: `high` · lock-in: `portable`

**Is:** Attach arbitrary key-value tags to Cloudflare resources (Workers, R2, KV, D1, Queues, Vectorize, zones, DNS records, tunnels, and ~35 more types) for organization, cost allocation, and policy/filter queries — without touching the resources themselves.

**Replaces:** A homegrown resource inventory/tagging convention — a spreadsheet, a naming hack like `team-prod-svc-*`, or a side database mapping resource IDs to team/env/cost-center — used because the platform had no native tags.

**Use it via:** Tagging REST API (recommended) authenticated with Account Owned Tokens (AOTs) — not user tokens; tags applied per resource type/ID. `PUT` replaces the full tag set (not a partial update). Beta dashboard also available.

**Capabilities:**
- Key-value tags across ~37 resource types: account-scoped (worker, worker_version, r2_bucket, kv_namespace, d1_database, queue, vectorize_index, durable_object_namespace, pages_project, ai_gateway, cloudflared_tunnel, image, stream_*, access_*, alerting_policy/webhook, load_balancer_*, account_ruleset, resource_share, gateway_list/rule) and zone-scoped (zone, dns_record, custom_hostname, custom_certificate, healthcheck, load_balancer, worker_route, api_gateway_operation, zone_ruleset, managed_client_certificate, access_application_policy)
- Tag-based filtering with AND/OR logic, negation, and key-only matching for cross-resource queries and policy enforcement
- Cost-allocation and access-control use cases via metadata, independent of resource config
- API-first with a beta dashboard UI

**Detection signals — the lens fires on these:**
- Naming-convention hacks encoding metadata into resource names: `team-env-purpose-*`, `prod-*` / `staging-*` prefixes on Workers/buckets/KV
- A side table / JSON / spreadsheet mapping Cloudflare resource IDs to owner / cost-center / environment
- Terraform locals or modules injecting a pseudo-`tags` map into resource names because CF lacked native tags
- FinOps scripts trying to attribute Cloudflare spend per team by parsing resource names
- Many CF resources across teams/accounts with no governance layer for ownership or cleanup

**Ideas:**
- Tag every Worker/R2/KV/D1 with team + env + cost-center to drive chargeback and ownership reporting
- Replace `prod-`/`staging-` naming hacks with real env tags and filter resources by tag in tooling
- Enforce policy/cleanup by querying untagged or mis-tagged resources across the account

**Pairs with:** workers, r2, terraform, account-owned-tokens

**Pricing:** Available on all plans; no separate charge documented. (verify — drifts)

**Limits:**
- Public beta — API is stable but rough edges remain (e.g. `PUT` replaces all tags; querying untagged resources can error instead of returning empty)
- Requires Account Owned Tokens (AOTs), not regular user API tokens
- Supported resource set is finite (~37 types) — not yet every Cloudflare resource
- It's metadata/governance, not a billing breakdown product by itself — you build cost reports on top of the tags

**Notes:** The 'stop encoding metadata in resource names' fix. Honest caveat: public beta, AOT-only auth, and PUT-replaces-all semantics mean tooling must read-modify-write carefully. Most valuable for multi-team/multi-env accounts doing FinOps or governance.

**Docs:** https://developers.cloudflare.com/resource-tagging/index.md, https://developers.cloudflare.com/resource-tagging/reference/resource-types/index.md, https://developers.cloudflare.com/resource-tagging/how-to/manage-tags/index.md

---

## Version Management
`version-management` · Platform / Config Safety · confidence: `high` · lock-in: `portable`

**Is:** Versioned, environment-gated rollout of zone configuration (notably WAF custom rules and optimization settings) so you can test changes in Development/Staging, deploy to Production, and roll back — without a live-traffic accident.

**Replaces:** A DIY 'config as code' safety net — Terraform plan/apply discipline plus a manual change-management runbook and a panicked git revert — that teams build to avoid breaking prod with a bad WAF/zone-config change.

**Use it via:** Primarily the Cloudflare dashboard today (versions, environments, deploy/rollback). REST/Terraform coverage is not surfaced in the docs index; requires Super Administrator / Administrator role and adoption of WAF managed + custom rules.

**Capabilities:**
- Three built-in environments — Development, Staging, Production — each with traffic filters that route requests by zone name, Edge Server IP, or a development cookie
- Create a version, validate it in Development, promote through Staging, then deploy to Production
- Clone an existing version to seed a new one (configs copied automatically)
- Roll back to a previously deployed version quickly
- Production traffic filter matches only your zone name and is non-editable (safety guard)

**Detection signals — the lens fires on these:**
- Terraform managing Cloudflare WAF/zone config with a heavy review/runbook process to avoid prod breakage
- A staging zone (e.g. staging.example.com as a separate Cloudflare zone) maintained solely to test config changes
- Change-management docs describing manual 'apply to staging, then prod' steps for WAF/ruleset edits
- Post-incident notes citing a bad WAF rule or zone-setting change pushed straight to production
- Scripts that snapshot/diff Cloudflare zone settings to enable a manual rollback

**Ideas:**
- Move risky WAF custom-rule changes behind Development/Staging environments before they touch production traffic
- Adopt one-click rollback for zone config instead of reconstructing prior state from Terraform state or memory
- Use the development cookie filter to QA a config change against prod-like traffic before promoting it

**Pairs with:** waf, rulesets, terraform

**Pricing:** Enterprise-only; not available on Free/Pro/Business. (verify — drifts)

**Limits:**
- Enterprise-gated
- Scope is ZONE configuration (WAF custom rules + optimization/zone settings) — NOT Workers code versioning (that's Workers Versions/Gradual Deployments) and not a substitute for Terraform across the whole account
- Traffic filters route by zone name / Edge IP / cookie — the docs do not describe percentage-based or gradual % rollout
- Requires Super Administrator / Administrator role and WAF managed+custom rules adoption

**Notes:** Easy to confuse with Workers deployment versioning — this is specifically for ZONE config safety (WAF/optimization). Recommend only for Enterprise zones. I corrected an earlier ambiguity: environments ARE first-class (Dev/Staging/Prod with editable traffic filters); what's NOT documented is percentage-based gradual rollout.

**Docs:** https://developers.cloudflare.com/version-management/index.md, https://developers.cloudflare.com/version-management/about/index.md, https://developers.cloudflare.com/version-management/reference/available-configurations/index.md

---
