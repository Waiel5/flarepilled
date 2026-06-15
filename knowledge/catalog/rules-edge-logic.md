# Rules & Edge Logic

_11 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Bulk Redirects
`cloudflare-bulk-redirects` · Edge Rules / URL forwarding · confidence: `high` · lock-in: `portable`

**Is:** Account-level lists of up to a million static one-to-one URL redirects, applied edge-side via a Ruleset Engine rule.

**Replaces:** Stop hand-managing giant nginx `map`/return-301 files, _redirects spreadsheets, or a homegrown redirect-map microservice + database for thousands of legacy/migration URLs.

**Use it via:** Dashboard: Account Home > Bulk Redirects (Lists + Rules). API: Lists API (kind=redirect items) plus Rulesets API at account level, phase http_request_redirect, action=redirect with action_parameters.from_list. Terraform: cloudflare_list (redirect items) + cloudflare_ruleset (account, http_request_redirect). No Wrangler/binding. Static only — no expressions in the target.

**Capabilities:**
- Define large numbers of URL redirects at the account level, usable across all domains in the account
- Bulk Redirect Lists: named CSV-style collections of source -> target with per-entry settings
- Bulk Redirect Rules: Ruleset-Engine rules that enable one or more lists and add optional matching conditions
- Per-redirect parameters: status code, preserve query string, include/exclude subdomains, subpath matching, preserve path suffix
- Upload/manage via dashboard or API; lists are reusable and shareable across zones in the account
- Scales to very high redirect counts (up to 1,000,000 on Enterprise) without per-URL code

**Detection signals — the lens fires on these:**
- Huge nginx `map $request_uri $redirect { ... }` include files or thousands of `return 301` lines
- A long `_redirects` file (hundreds/thousands of lines) or sprawling next.config/vercel.json redirects[]
- A 'redirect service'/URL-shortener-style app backed by a DB table of from->to plus a 301 handler
- CSV/Google-Sheet exports of legacy->new URLs consumed by a build step
- Site-migration or domain-consolidation projects with massive one-to-one URL maps

**Ideas:**
- Find large static from->to URL maps (nginx map files, _redirects, DB redirect tables) that should be a Bulk Redirect List.
- Detect a homegrown redirect-map service/microservice that Bulk Redirects could replace entirely.
- Spot a site-migration redirect spreadsheet/CSV being applied in app or build code instead of at the edge.

**Pairs with:** Single Redirects, Cloudflare Snippets, Configuration Rules

**Pricing:** URL redirects across lists (Feb 2025 limits): Free 10,000; Pro 25,000; Business 50,000; Enterprise 1,000,000. (verify — drifts; rolled out gradually through H1 2025.)

**Limits:**
- Static only — no string replacement, no regex, no dynamic/expression targets (use Single Redirects or Snippets for those)
- A single list cannot contain two redirects with the exact same source URL
- Managed at account level; you still need a Bulk Redirect Rule to activate a list
- Source URLs are matched literally (with the subdomain/subpath/path-suffix toggles) — no pattern logic

**Notes:** The right tool for volume and simplicity, the wrong tool for logic. If targets must be computed or matched by pattern, use Single Redirects (dynamic) or Snippets. Lists live at the account level, which is great for multi-zone reuse but means redirects aren't co-located with a single zone's config. CSV import format is Cloudflare-specific.

**Docs:** https://developers.cloudflare.com/rules/url-forwarding/bulk-redirects/, https://developers.cloudflare.com/rules/url-forwarding/bulk-redirects/concepts/, https://developers.cloudflare.com/changelog/post/2025-02-12-rules-upgraded-limits/

---

## Cloud Connector
`cloudflare-cloud-connector` · Edge Rules / origin routing · confidence: `high` · lock-in: `portable`

**Is:** Rule-based routing of matching website traffic directly to public cloud object storage or origins (R2, S3, GCS, Azure) with Host/SSL handled for you.

**Replaces:** Stop running a reverse-proxy/origin-router box (nginx/HAProxy or a small app) whose only job is to forward certain paths to S3/GCS/Azure buckets with the right Host header and TLS.

**Use it via:** Dashboard: Rules > Cloud Connector (rule list with provider + destination). API: Cloud Connector rules API (and underlying Origin-Rule-style origin/host behavior). Terraform/Wrangler: not documented for this beta — treat as dashboard/API only. No binding.

**Capabilities:**
- Route incoming requests matching a rule to a public cloud provider you define
- Supported destinations: Cloudflare R2, AWS S3, Google Cloud Storage, Azure (blob storage)
- Cloudflare auto-applies the needed Host header rewrite and SSL/TLS settings for the chosen endpoint
- Match traffic by path/hostname/expression so only part of a site is served from cloud storage
- Beta across all plan tiers; configured entirely in the dashboard with per-provider presets
- Effectively packages Origin-Rule-style host/SNI handling into a guided cloud-storage connector

**Detection signals — the lens fires on these:**
- nginx/HAProxy/Apache config that proxies a path to `*.s3.amazonaws.com` / `storage.googleapis.com` / `*.blob.core.windows.net` with a Host rewrite
- An app route or small service that fetches from a bucket and streams it back (origin-router pattern)
- S3 website-endpoint or GCS bucket fronted by a custom proxy purely for custom-domain + TLS
- Env vars / config naming a public bucket as the upstream for static assets
- A CDN-origin shim whose only responsibility is bucket Host-header + SSL handling

**Ideas:**
- Find a reverse proxy that forwards paths to S3/GCS/Azure buckets with a Host rewrite — Cloud Connector replaces it.
- Detect an app/origin-router service that just streams public bucket objects back to clients.
- Spot a custom proxy fronting an S3 website endpoint for custom-domain + TLS that Cloud Connector handles natively.

**Pairs with:** Origin Rules, Transform Rules, Cache Rules, Cloudflare R2

**Pricing:** All plans (beta). Connectors: Free 10, Enterprise 300 (raised Feb 2025); mid-tiers scale between. (verify — drifts; beta status may change limits/pricing.)

**Limits:**
- Your object storage bucket must be publicly accessible for Cloud Connector to work
- Does not handle URL rewrites or caching automatically — configure Transform Rules / Cache Rules separately if needed
- Beta feature; API/Terraform coverage and provider list may be incomplete or shifting
- Limited to supported providers (R2, S3, GCS, Azure)

**Notes:** Best fit: serving static assets/files from a public bucket under your own domain without a proxy box. The public-bucket requirement is the key gotcha — for private buckets you still need signed access or a Worker. It's essentially a guided Origin Rule; if you outgrow the presets, drop to Origin Rules / Workers. Beta, so verify before depending on it.

**Docs:** https://developers.cloudflare.com/rules/cloud-connector/, https://developers.cloudflare.com/rules/cloud-connector/providers/, https://developers.cloudflare.com/changelog/post/2025-02-12-rules-upgraded-limits/

---

## Cloudflare Ruleset Engine
`ruleset-engine` · Rules / Edge Logic · confidence: `high` · lock-in: `portable`

**Is:** Cloudflare's phase-based rules runtime: a common API/language for WAF, redirects, transforms, cache, origin routing, compression, DDoS overrides, configuration rules, and other edge policies.

**Replaces:** A hand-built edge policy engine spread across nginx maps, Envoy filters, app middleware, Terraform modules, and one-off Cloudflare rule scripts.

**Use it via:** Rulesets API: create/list/update/delete rulesets and rules by account or zone and phase; Terraform: `cloudflare_ruleset`; dashboard product UIs write rulesets underneath. No Wrangler/binding because these are declarative edge policies, not Worker code.

**Capabilities:**
- Rulesets contain ordered rules, each with an expression, action, parameters, enabled flag, and optional description/ref
- Phase-based execution across HTTP request/response lifecycle: firewall, redirect, transform, cache settings, origin route, compression, configuration, and product-specific phases
- Shared Rules language fields, operators, lists, and functions across many Cloudflare products
- Account-level and zone-level rulesets depending on phase/product
- Manageable through dashboard UIs, Rulesets API, and Terraform `cloudflare_ruleset` resources

**Detection signals — the lens fires on these:**
- Large nginx/Envoy/Caddy maps for redirects, URL rewrites, header rewrites, cache-control, origin selection, or security filters
- Terraform creating many one-off Cloudflare rules without a shared ruleset model
- App middleware that only exists to make edge decisions on path, host, headers, bot score, country, ASN, or query string
- Custom rule compiler or DSL that emits WAF/redirect/cache/origin policies
- Multiple Cloudflare Rules products configured independently with no phase/order model

**Ideas:**
- Collapse origin/app rewrite middleware into phase-appropriate Transform, Redirect, Cache, or Origin Rules managed as Ruleset Engine objects.
- Replace a pile of nginx maps with Terraform `cloudflare_ruleset` resources so edge logic is versioned and ordered explicitly.
- When multiple Rules products interact, audit phase order through the Ruleset Engine docs instead of assuming dashboard order.

**Pairs with:** WAF, Transform Rules, Single Redirects, Bulk Redirects, Cache Rules, Origin Rules, Configuration Rules, Compression Rules

**Pricing:** No standalone SKU; availability, rule counts, managed rules, and quotas are inherited from the underlying Rules product and zone/account plan.

**Limits:**
- Rule quotas, supported actions, and phases are product- and plan-specific
- Rules language is powerful but Cloudflare-specific; complex business logic still belongs in Workers or the origin
- Phase order matters and can surprise teams that think in per-product dashboard pages
- Not all rule products expose every action/field at every account/zone level

**Notes:** This entry is deliberately the substrate, not a replacement for the product-specific catalog entries. Use it when the smell is 'we built a policy/rules compiler' or 'edge decisions are scattered everywhere.' For concrete migrations, pick the phase-specific product entry and verify its quota/action docs.

**Docs:** https://developers.cloudflare.com/ruleset-engine/llms.txt, https://developers.cloudflare.com/ruleset-engine/index.md, https://developers.cloudflare.com/ruleset-engine/about/phases/index.md, https://developers.cloudflare.com/ruleset-engine/rulesets-api/index.md, https://developers.cloudflare.com/ruleset-engine/rules-language/index.md

---

## Cloudflare Snippets
`cloudflare-snippets` · Edge compute (lightweight) · confidence: `high` · lock-in: `portable`

**Is:** Short pieces of JavaScript run at the edge, bound to a filter expression, for request/response logic too complex for declarative rules but too small for a Worker.

**Replaces:** Stop deploying a full Worker, a tiny Lambda@Edge/CloudFront Function, or a VCL snippet just to do a JWT check, conditional redirect, A/B split, or custom header logic at the edge.

**Use it via:** Dashboard: Rules > Snippets (code editor + Snippet Rules). API: Snippets API (PUT snippet content, snippet_rules for triggers). Terraform: cloudflare_snippet { name, main_module, files{...} } + cloudflare_snippet_rules { rules{ expression, snippet_name } }. Code model is ES-module fetch handler like Workers, but NO bindings (no KV/D1/R2/DO/secrets/env/cron) and no Wrangler dev workflow.

**Capabilities:**
- Run standard JavaScript on Cloudflare's network using Web-platform APIs (fetch, Request, Response, URL, Web Crypto)
- Same code model as Workers: ES-module `export default { async fetch(request) { ... } }` returning/forwarding a Response
- Bind each snippet to a Snippet Rule whose Rules-language expression decides when it runs (bot score, country, cookie, path, WAF attack score, etc.)
- Chain multiple snippets — each receives the request as modified by the previous one
- Common uses: JWT/token validation, conditional and dynamic redirects, header rewriting, A/B testing, request normalization
- Lower barrier than Workers — no Wrangler project required; editable in-dashboard
- Manage as code via API and Terraform (cloudflare_snippet + cloudflare_snippet_rules)

**Detection signals — the lens fires on these:**
- Lambda@Edge / CloudFront Functions or Fastly VCL snippets that only do header logic, JWT checks, or redirects
- A minimal Cloudflare Worker that uses no bindings and just rewrites/validates requests (over-provisioned)
- Edge middleware (Next.js middleware, Vercel Edge Functions) doing small auth/redirect/header tasks
- Hand-rolled JWT verification or signed-cookie checks running in a tiny proxy in front of the app
- A/B-test or feature-flag routing implemented in a small edge function

**Ideas:**
- Find Lambda@Edge/CloudFront Functions or VCL snippets doing JWT checks, header logic, or redirects that map to a Snippet.
- Detect a binding-less Worker or edge middleware that's small enough to be a Snippet instead.
- Spot edge JWT validation or A/B routing code that could be a Snippet bound to a filter expression.

**Pairs with:** Transform Rules, Single Redirects, Cloudflare Workers, Configuration Rules

**Pricing:** Paid plans only (NOT on Free). Code snippets + rules per zone: Pro 25, Business 50, Enterprise 300. Per-invocation limits: ~5 ms CPU, 2 MB memory, 32 KB max package size; subrequests Pro 2 / Business 3 / Enterprise 5. (verify — drifts.)

**Limits:**
- No bindings: no KV, D1, R2, Durable Objects, environment variables, or secrets
- No persistent state, no cron triggers, no heavy compute (no image transforms / AI inference)
- JavaScript only (Workers also do TS/Python/Rust); HTTP/HTTPS only; no observability/logs or gradual version rollouts
- Tight CPU (~5 ms), memory (2 MB), package size (32 KB) and subrequest caps; not on Free plan

**Notes:** Snippets are the on-ramp; when you need state, bindings, secrets, observability, more CPU, or versioned rollouts, graduate to Workers (the migration is natural because the code model matches). The 5 ms / 2 MB / 32 KB ceilings are real and easy to hit. Note this is the inverse of most catalog entries: here the 'managed service' replaces a *Worker* you don't need yet, as well as foreign-cloud edge functions.

**Docs:** https://developers.cloudflare.com/rules/snippets/, https://developers.cloudflare.com/rules/snippets/when-to-use/, https://developers.cloudflare.com/rules/snippets/how-it-works/, https://developers.cloudflare.com/changelog/post/2024-12-11-terraform-snippets/

---

## Compression Rules
`cloudflare-compression-rules` · Edge Rules / performance · confidence: `high` · lock-in: `portable`

**Is:** Control which response-compression algorithm Cloudflare applies (Brotli, gzip, zstd) by content type or file extension, via edge rules.

**Replaces:** Stop tuning nginx `gzip`/`brotli`/`gzip_types`/`brotli_types` and ngx_brotli module config, or Apache mod_deflate/mod_brotli `AddOutputFilterByType`, just to choose compression per content type.

**Use it via:** Dashboard: Rules > Compression Rules (Rules Overview). API: Rulesets API, phase http_response_compression, action=compress_response with action_parameters.algorithms[] (e.g. brotli, gzip, zstd, none, auto). Terraform: cloudflare_ruleset (http_response_compression). No Wrangler/binding.

**Capabilities:**
- Define an ordered list of compression algorithms; Cloudflare picks the first the visitor's browser supports (per Accept-Encoding)
- Match by response media type (http.response.content_type.media_type) and/or request file extension (http.request.uri.path.extension)
- Enable/disable or change compression for specific content types (e.g. compress JSON/SVG, skip already-compressed assets)
- Supports modern algorithms including Brotli, gzip, and zstd (where available)
- Full Rules-language expressions for conditional compression
- Dashboard templates plus API/Terraform management

**Detection signals — the lens fires on these:**
- nginx `gzip on; gzip_types ...;` / `brotli on; brotli_types ...;` (ngx_brotli) tuning
- Apache `AddOutputFilterByType DEFLATE ...` / mod_brotli config
- App-level compression middleware (Express `compression()`, Django GZipMiddleware) chosen per content type
- Build steps pre-compressing assets and config deciding which types to serve compressed
- CDN config explicitly enabling/disabling Brotli vs gzip per file type

**Ideas:**
- Find nginx gzip_types/brotli_types or Apache mod_deflate tuning that Compression Rules can express at the edge.
- Detect app-level compression middleware configured per content type that Cloudflare could own.
- Spot per-extension compress/skip decisions (e.g. don't re-compress images) that belong in a Compression Rule.

**Pairs with:** Cache Rules, Transform Rules, Configuration Rules

**Pricing:** All plans. Rules per zone: Free 10, Pro 25, Business 50, Enterprise 300. (verify — drifts.)

**Limits:**
- No compression occurs if the browser supports none of the listed algorithms, or if origin sends cache-control: no-transform
- When multiple rules match, the last matching rule wins
- Controls algorithm selection, not custom compression levels/dictionaries
- Requires proxied (orange-cloud) DNS records

**Notes:** Narrow but handy: it governs which algorithm Cloudflare uses, replacing fiddly per-type web-server compression config. The no-transform and 'last rule wins' behaviors are the main gotchas. Cloudflare already auto-compresses sensibly, so only reach for this when you need to override defaults. Minimal lock-in.

**Docs:** https://developers.cloudflare.com/rules/compression-rules/, https://developers.cloudflare.com/rules/compression-rules/settings/, https://developers.cloudflare.com/changelog/post/2025-02-12-rules-upgraded-limits/

---

## Configuration Rules
`cloudflare-configuration-rules` · Edge Rules / per-request settings · confidence: `high` · lock-in: `portable`

**Is:** Override Cloudflare zone settings (SSL mode, cache, security level, Polish, Rocket Loader, etc.) per-request based on filter expressions.

**Replaces:** Stop building conditional edge/CDN config or per-path nginx server blocks that toggle TLS strictness, caching, or feature flags differently for /admin, /api, or specific hostnames.

**Use it via:** Dashboard: Rules > Configuration Rules. API: Rulesets API, phase http_config_settings, action=set_config with action_parameters listing the settings to override (e.g. ssl, security_level, rocket_loader, polish, email_obfuscation, bic, disable_apps). Terraform: cloudflare_ruleset (http_config_settings). No Wrangler/binding.

**Capabilities:**
- Apply a different set of Cloudflare settings only to requests matching a Rules-language expression (path, hostname, IP, country, etc.)
- Override SSL/TLS encryption mode, Browser Integrity Check, Security Level for matching traffic
- Toggle performance features: Auto Minify (legacy), Rocket Loader, Mirage, Polish, Email Obfuscation, Hotlink Protection
- Disable Apps, Disable Performance, Disable Security, Disable Zaraz, Disable Railgun (legacy) per match
- Override Automatic HTTPS Rewrites, Opportunistic Encryption, and similar zone toggles selectively
- Replaces the deprecated Page Rules settings actions with a Ruleset-Engine, expression-driven model

**Detection signals — the lens fires on these:**
- nginx per-location `ssl_verify_client`/different `proxy_cache`/security toggles by path
- App code or CDN config that sets cache-control or disables features only for certain routes
- Comments/configs like 'relax security on /webhooks' or 'stricter TLS for /admin'
- Legacy Cloudflare Page Rules using Browser Integrity Check / Security Level / Cache Level actions
- Per-hostname or per-path feature flags for Cloudflare performance/security features

**Ideas:**
- Find per-path or per-hostname toggles of TLS strictness, security level, or caching that should be Configuration Rules.
- Detect legacy Page Rules using settings actions that should migrate to Configuration Rules.
- Spot 'disable feature X only on route Y' logic that belongs in an expression-driven Configuration Rule.

**Pairs with:** Cache Rules, Transform Rules, Origin Rules, Custom Errors

**Pricing:** All plans. Rules per zone: Free 10, Pro 25, Business 50, Enterprise 300. (verify — drifts; individual settings still gated by the plan that offers that feature, e.g. Polish needs Pro+.)

**Limits:**
- Can only override settings that exist on your plan (a rule can't enable a feature your plan lacks)
- Affects Cloudflare's own settings only — not origin behavior or response bodies
- Rule-count caps per plan; evaluation/override semantics follow Ruleset-Engine order
- Requires proxied (orange-cloud) DNS records

**Notes:** The modern replacement for Page Rules' settings actions — if you see Page Rules, that's a migration signal. It tunes Cloudflare knobs per request, nothing more; it cannot run code or mutate payloads. Low lock-in (it just toggles Cloudflare features) but the expressions and setting names are Cloudflare-specific.

**Docs:** https://developers.cloudflare.com/rules/configuration-rules/, https://developers.cloudflare.com/rules/configuration-rules/settings/

---

## Custom Errors
`cloudflare-custom-errors` · Edge Rules / response shaping · confidence: `high` · lock-in: `portable`

**Is:** Serve branded, custom error pages and bodies at the edge for HTTP 4xx/5xx, security challenges, WAF blocks, and rate-limit responses.

**Replaces:** Stop maintaining custom error_page templates in nginx, ErrorDocument in Apache, or per-app 4xx/5xx HTML and a CDN error-page bucket just to brand error and block pages.

**Use it via:** Dashboard: Rules > Custom Errors / Custom Pages (zone + account). API: Custom Errors API (Custom Error Rules via Rulesets API, action serves custom response; plus Custom Pages/assets endpoints). Terraform: cloudflare_custom_pages and ruleset-based error rules. No Wrangler/binding.

**Capabilities:**
- Replace default Cloudflare error pages with your own content for status codes 400 and above
- Custom Error Rules: serve custom inline content or a fetched URL when conditions match (Ruleset-Engine driven)
- Error Pages: zone-level or account-level branded pages for challenges, WAF blocks, rate limiting, and 5xx
- Custom Error Assets: upload/reference assets that Cloudflare fetches and caches globally (source can go away afterward)
- Covers errors from origin, from Cloudflare products (including Workers), and from security challenges
- Zone-level rules override account-level config and take precedence over Error Pages; custom WAF responses win over these
- Enterprise-only Origin Error Pages for origin-generated errors

**Detection signals — the lens fires on these:**
- nginx `error_page 404 /404.html;` / `error_page 500 502 503 504 /50x.html;` blocks
- Apache `ErrorDocument 404 ...` / `ErrorDocument 500 ...`
- Per-app custom 4xx/5xx HTML templates plus middleware that renders them
- A static bucket of branded error pages fronted by the CDN
- Custom 'maintenance' or 'blocked' pages wired up for WAF/rate-limit responses

**Ideas:**
- Find nginx error_page / Apache ErrorDocument directives serving branded HTML that Custom Errors could host at the edge.
- Detect app-rendered 4xx/5xx templates or a CDN error-page bucket replaceable by Custom Error Rules.
- Spot custom WAF/rate-limit block pages that should be Cloudflare Custom Errors.

**Pairs with:** Cloudflare WAF, Rate Limiting, Configuration Rules, Managed Transforms

**Pricing:** Paid plans only (NOT Free). Custom error assets + rules per zone: Pro 25, Business 50, Enterprise 300. Origin Error Pages: Enterprise only. (verify — drifts.)

**Limits:**
- Error Pages won't render (Cloudflare default shown instead) if the request lacks an accept-encoding header — does not affect Custom Error Rules
- Error Pages exclude some status codes (e.g. 500, 501, 503, 505 for the Error Pages flavor)
- Custom WAF block responses take priority over Custom Errors content
- Origin Error Pages are Enterprise-only; not available on Free

**Notes:** Two overlapping mechanisms (legacy Custom/Error Pages vs newer Custom Error Rules) with a precedence order — read the ordering before relying on it. The accept-encoding gotcha trips people up for API clients. Branding-layer feature; low lock-in (just HTML/assets), but the rule/precedence model is Cloudflare-specific.

**Docs:** https://developers.cloudflare.com/rules/custom-errors/, https://developers.cloudflare.com/rules/custom-errors/create-rules/, https://developers.cloudflare.com/changelog/post/2025-02-12-rules-upgraded-limits/

---

## Managed Transforms
`cloudflare-managed-transforms` · Edge Rules / HTTP headers · confidence: `high` · lock-in: `portable`

**Is:** One-click toggles for common request/response header transforms (add visitor IP/geo headers, strip leaky headers, bot/leaked-credential headers) without writing a rule.

**Replaces:** Stop hand-writing nginx `proxy_set_header X-Forwarded-For/CF-Connecting-IP`, geo-IP header injection, or `more_clear_headers Server X-Powered-By` — and stop authoring custom Transform Rules for these standard cases.

**Use it via:** Dashboard: Rules > Settings / Managed Transforms (toggle list). API: Managed Transforms API (enable/disable named transforms). Terraform: supported (managed-transforms settings). No Wrangler/binding. These are toggles, not authored expressions.

**Capabilities:**
- Add visitor location (geo) headers to requests forwarded to origin (country, city, lat/long, etc.)
- Add true-client-IP / visitor IP headers; or remove visitor IP headers from origin requests
- Add bot-management request headers and leaked-credential-check headers (where entitled)
- Add common security-related response headers
- Remove the X-Powered-By response header to reduce fingerprinting
- Applied to all matching inbound requests for the zone; deployed as internal Transform Rules that do NOT count against your Transform Rules quota
- Internal rules don't clutter the Transform Rules list in the dashboard

**Detection signals — the lens fires on these:**
- nginx `proxy_set_header X-Forwarded-For $remote_addr;` / `X-Real-IP` / custom geo headers via GeoIP module
- App code reading a homemade geo header or trusting X-Forwarded-For it sets itself
- `more_clear_headers`/`header_filter_by_lua` removing Server / X-Powered-By
- Express `app.disable('x-powered-by')` or middleware stripping fingerprinting headers
- Custom Transform Rules that merely re-implement standard add-true-client-IP / add-geo behavior

**Ideas:**
- Find nginx/app code injecting visitor-IP or geo headers that Managed Transforms can add with one toggle.
- Detect header-stripping (Server/X-Powered-By) that a Managed Transform handles natively.
- Spot custom Transform Rules duplicating standard managed transforms and reclaim quota.

**Pairs with:** Transform Rules, Bot Management, Configuration Rules

**Pricing:** Available across plans (individual transforms may be gated by entitlement, e.g. Bot Management headers require the add-on). Managed Transforms do not consume the Transform Rules quota. (verify — drifts; check the reference for per-transform availability.)

**Limits:**
- Fixed catalog of pre-built transforms — not customizable per-condition (use Transform Rules for that)
- Some transforms (bot management, leaked-credential headers) require the corresponding product/add-on
- Apply zone-wide to all inbound requests, not per-path
- Internal rules are invisible in the Transform Rules list (less transparency)

**Notes:** Strictly the common-case shortcut on top of Transform Rules. If you need a header only on certain paths or with a computed value, write a Transform Rule instead. Reclaiming quota is a nice side benefit since managed transforms don't count. Trivial lock-in.

**Docs:** https://developers.cloudflare.com/rules/transform/managed-transforms/, https://developers.cloudflare.com/rules/transform/managed-transforms/reference/, https://developers.cloudflare.com/rules/transform/managed-transforms/configure/

---

## Origin Rules
`cloudflare-origin-rules` · Edge Rules / origin routing · confidence: `high` · lock-in: `portable`

**Is:** Per-request override of where and how Cloudflare connects to origin — Host header, SNI, resolved DNS hostname, and destination port.

**Replaces:** Stop juggling nginx `proxy_pass` upstreams + `proxy_set_header Host` + `proxy_ssl_name`/SNI, or maintaining a reverse-proxy box, just to route certain paths/hostnames to different backends or ports.

**Use it via:** Dashboard: Rules > Origin Rules. API: Rulesets API, phase http_request_origin, action=route, action_parameters{host_header, origin{host, port}, sni{value}}. Terraform: cloudflare_ruleset (http_request_origin). No Wrangler/binding.

**Capabilities:**
- Host Header override: rewrite the Host header sent to origin (e.g. point a path at a third-party host)
- DNS Record / Resolve Override: send the request to a different origin hostname than the one in the URL (must be a hostname on the same Cloudflare account)
- SNI override: set the TLS SNI value for the origin handshake (static value; valid hostname on the same account)
- Destination Port override: connect to origin on a specific port (1-65535) instead of the default
- All overrides are conditional via Rules-language expressions (per path, hostname, header, etc.)
- Combine with one rule to repoint a subset of traffic to an alternate backend without DNS changes

**Detection signals — the lens fires on these:**
- nginx `proxy_pass http://backend:9000;` + `proxy_set_header Host backend.internal;` + `proxy_ssl_name`/`proxy_ssl_server_name on;` blocks routing by location
- HAProxy/Envoy backends or an Nginx upstream map selecting origin by path/host
- A reverse-proxy/origin-router container whose only job is host/SNI/port rewriting toward different backends
- App or LB config that forwards specific paths to a different internal service or non-standard port
- Hardcoded Host-header rewrites for third-party origins (S3 website endpoints, SaaS backends)

**Ideas:**
- Find nginx proxy_pass/proxy_set_header Host/proxy_ssl_name blocks that route by path and could become Origin Rules.
- Detect a reverse-proxy or origin-router service that only overrides host/SNI/port toward alternate backends.
- Spot non-standard origin ports or per-path backend selection in LB config that belongs in an Origin Rule.

**Pairs with:** Transform Rules, Configuration Rules, Cloud Connector, Cloudflare Tunnel

**Pricing:** All plans. Rules per zone: Free 10, Pro 25, Business 50, Enterprise 300. Host Header, SNI, and DNS/Resolve overrides are Enterprise-only; Destination Port override is available on all plans. (verify — drifts.)

**Limits:**
- Host Header / SNI / DNS-record overrides require Enterprise; lower plans get destination-port override only
- SNI override accepts a static value only (no expression-driven SNI)
- Resolve/SNI targets must be valid hostnames on the same Cloudflare account
- Requires proxied (orange-cloud) DNS records; does not establish private connectivity (that's Tunnel/Spectrum)

**Notes:** The big caveat: the most useful overrides (Host/SNI/DNS) are Enterprise-gated, so on Pro/Business this is essentially a port-override tool. For pointing traffic at cloud object storage specifically, Cloud Connector wraps Origin-Rule-style host/SSL handling with a friendlier UI. Not a substitute for a secure tunnel to a private origin.

**Docs:** https://developers.cloudflare.com/rules/origin-rules/, https://developers.cloudflare.com/rules/origin-rules/features/

---

## Single Redirects
`cloudflare-single-redirects` · Edge Rules / URL forwarding · confidence: `high` · lock-in: `portable`

**Is:** Per-zone static or dynamic URL redirects defined as edge rules with a wildcard interface, no return-301 maps or app routes.

**Replaces:** Stop maintaining nginx `return 301`/`rewrite ... redirect` blocks, Apache Redirect/RedirectMatch, framework redirect middleware, or a Netlify-style _redirects file for one-off and pattern redirects.

**Use it via:** Dashboard: Rules > Redirect Rules (single). API: Rulesets API, phase http_request_dynamic_redirect, action=redirect, action_parameters.from_value{target_url(value or expression), status_code, preserve_query_string}. Terraform: cloudflare_ruleset (use `ref` to avoid rule recreation). Min token perm: Zone > Single Redirect > Edit (a.k.a. Dynamic URL Redirects Write). No Wrangler/binding.

**Capabilities:**
- Static redirects to a fixed target URL
- Dynamic redirects that build the target from parts of the original request (path, query, country, etc.)
- Wildcard-based pattern interface (match `https://example.com/old/*`, reuse captured segments in target) without writing regex
- Optional string-replacement and regular expressions for advanced rewriting (plan-dependent)
- Choose status code (301, 302, 307, 308) and preserve query string / path suffix
- Match using the full Rules language for conditional redirects (only redirect for certain countries, devices, paths)
- Built on the Ruleset Engine (http_request_dynamic_redirect phase) so it is versioned and API/Terraform-manageable

**Detection signals — the lens fires on these:**
- nginx `return 301 https://...`, `rewrite ^/old /new permanent`, or a `map` block driving redirects
- Apache `Redirect 301` / `RedirectMatch` in .htaccess or vhost
- A Netlify/Cloudflare Pages `_redirects` file or `next.config.js` redirects[] / `vercel.json` redirects used for a handful of rules
- Express/Koa/Django/Rails middleware doing res.redirect()/HttpResponseRedirect for marketing or legacy URLs
- A small 'redirect service' or edge function whose only job is issuing 301/302s

**Ideas:**
- Find nginx `return 301`/`map`-based redirects or _redirects/next.config redirects[] that are simple pattern matches and belong in Single Redirects.
- Detect app-level res.redirect() handlers for legacy/marketing URLs that should be edge redirects.
- Spot redirect logic conditional on country/device/path that could be a single dynamic-redirect rule.

**Pairs with:** Bulk Redirects, Transform Rules, Configuration Rules, Origin Rules

**Pricing:** All plans. Rule count shares the Rules family caps (Enterprise raised to 300 in Feb 2025; lower tiers in the 10/25/50 range). (verify — drifts; check the Single Redirects availability table.)

**Limits:**
- Best for small-to-moderate numbers of redirects defined as rules; for thousands of one-to-one mappings use Bulk Redirects instead
- Advanced regex/string-replacement features and higher rule counts depend on plan tier
- Requires proxied (orange-cloud) DNS records
- Each rule is an expression+target; very large rule sets get unwieldy vs a Bulk Redirect list

**Notes:** Single Redirects = dynamic/conditional and pattern-based; Bulk Redirects = large static one-to-one lists. Choose by shape, not just count. Dynamic targets use Rules-language expressions, which are Cloudflare-specific (mild lock-in). Not for header/path rewriting that stays on the same URL — that's Transform Rules.

**Docs:** https://developers.cloudflare.com/rules/url-forwarding/single-redirects/, https://developers.cloudflare.com/rules/url-forwarding/single-redirects/create-api/, https://developers.cloudflare.com/changelog/post/2025-02-12-rules-upgraded-limits/

---

## Transform Rules
`cloudflare-transform-rules` · Edge Rules / HTTP rewriting · confidence: `high` · lock-in: `portable`

**Is:** Edge-side rewriting of URL paths, query strings, and request/response headers via filter-expression rules, no origin code.

**Replaces:** Stop hand-rolling nginx rewrite/headers-more/sub_filter, Apache mod_rewrite, or Lambda@Edge/CloudFront-Functions header logic just to munge paths and headers in front of your app.

**Use it via:** Dashboard: Rules > Overview (Transform Rules UI with templates). API: Rulesets API, phases http_request_transform (URL rewrite), http_request_late_transform (request headers), http_response_headers_transform (response headers), action=rewrite. Terraform: cloudflare_ruleset with the matching phase. No Wrangler/binding (these are declarative rules, not code).

**Capabilities:**
- URL Rewrite Rules: rewrite the URL path and/or query string of an incoming request (static or dynamic) before it hits origin
- Request Header Transform Rules: set or remove HTTP request headers sent to origin (static value, dynamic expression, or from another header/field)
- Response Header Transform Rules: set or remove HTTP response headers returned to the visitor
- Match traffic with the Rules language / Wirefilter expressions (hostname, path, method, headers, cookies, country, bot score, etc.)
- Dynamic values built from request fields via expression functions (concat, lower, regex_replace on Business+)
- Dashboard templates for common tasks; rules evaluated in order, later rules can overwrite earlier changes
- Regex-based matching/rewriting available on Business and Enterprise plans
- Managed Transforms run before custom Transform Rules and do not count against the quota

**Detection signals — the lens fires on these:**
- nginx.conf with `rewrite ... permanent/last`, `sub_filter`, `more_set_headers`/`headers-more` module, `proxy_set_header` purely to reshape paths/headers
- Apache `RewriteRule`/`Header set`/`Header unset` in .htaccess used only for edge-style path/header rewriting
- Lambda@Edge or CloudFront Functions whose entire body mutates request.uri or sets/removes headers
- A tiny Express/Fastify middleware or reverse-proxy service that only rewrites paths or injects/strips headers
- Adding headers like X-Forwarded-* , security headers, or stripping Server/X-Powered-By in app code

**Ideas:**
- Find nginx rewrite/headers-more directives or Lambda@Edge functions that only reshape paths/headers and could move to Transform Rules.
- Spot app middleware whose sole job is injecting or stripping HTTP headers that Cloudflare could set at the edge.
- Detect URL-path rewriting (e.g. /old/* -> /new/*) hard-coded in the origin that belongs in an edge URL Rewrite Rule.

**Pairs with:** Single Redirects, Origin Rules, Configuration Rules, Managed Transforms, Cloudflare Snippets

**Pricing:** All plans. Active rules per zone: Free 10, Pro 25, Business 50, Enterprise 300. Regex matching/rewriting: Business and Enterprise only. (verify — drifts; limits were raised Feb 2025 and roll out gradually.)

**Limits:**
- Free/Pro cannot use regular expressions in matching or rewriting (Business+ only)
- URL Rewrite only changes path/query — it does not change the origin host (use Origin Rules for that) and is not a redirect (use Single Redirects)
- Rule-count caps per plan (10/25/50/300); rules run in sequence and can clobber each other
- Requires DNS records proxied (orange-cloud) through Cloudflare

**Notes:** Declarative only — for branching logic, loops, JWT verification, or anything beyond field-to-field rewriting, escalate to Snippets or Workers. Not a redirect engine (URL Rewrite is transparent to the browser). Header mutation is powerful but order-dependent; document rule order. Lock-in is low: expressions are portable concepts but the rule definitions are Cloudflare-specific.

**Docs:** https://developers.cloudflare.com/rules/transform/, https://developers.cloudflare.com/rules/transform/url-rewrite/, https://developers.cloudflare.com/rules/transform/request-header-modification/, https://developers.cloudflare.com/rules/transform/response-header-modification/

---
