# Security

_15 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## AI Crawl Control (formerly AI Audit)
`ai-crawl-control` · Security / Bot & Content Control · confidence: `high` · lock-in: `portable`

**Is:** Visibility into and control over how AI crawlers (GPTBot, ClaudeBot, etc.) access your site — see who's scraping, allow/block individual crawlers, track robots.txt compliance, and optionally charge per crawl.

**Replaces:** Hand-maintained robots.txt rules plus brittle user-agent/IP blocklists in nginx/WAF that a team curates to keep AI scrapers off their content — and the lack of any way to monetize crawler access at all.

**Use it via:** Configured in the Cloudflare dashboard (manage AI crawlers, robots.txt tracking, allow/block); analytics via the AI Crawl Control GraphQL API. Pay Per Crawl surfaces HTTP 402 + payment-intent request headers and is access-gated (apply for beta).

**Capabilities:**
- Dashboard visibility into which AI services access your content and how often
- Allow or block rules per individual crawler (granular, by bot)
- Track which crawlers actually honor your robots.txt directives, and create enforcement rules
- Pay Per Crawl (closed beta): set a zone-level price; crawlers get HTTP 200 with payment intent or an HTTP 402 Payment Required with pricing, Cloudflare acts as Merchant of Record
- Works automatically on all Cloudflare plans; integrates with Bots and WAF (which take precedence)
- GraphQL API for crawler analytics

**Detection signals — the lens fires on these:**
- robots.txt hand-curated with many AI bot User-agent blocks (GPTBot, ClaudeBot, CCBot, Google-Extended, PerplexityBot, Bytespider)
- nginx/Apache/WAF rules or middleware matching AI crawler user-agents or scraper IP ranges
- A homegrown 'block the AI scrapers' allow/deny list or Cloudflare custom rule maintained by hand
- Publisher/e-commerce/docs content owners worried about LLM training scraping or leaking pricing data
- No mechanism in place to monetize or even measure AI crawler traffic despite it being significant

**Ideas:**
- Replace a hand-maintained AI-bot robots.txt + WAF blocklist with managed per-crawler allow/block and compliance tracking
- Measure exactly which AI services scrape your content and how much, then decide allow vs. block per bot
- For a publisher, explore Pay Per Crawl to charge AI crawlers (HTTP 402) instead of just blocking them

**Pairs with:** bots / bot-management, waf, robots.txt

**Pricing:** Core visibility + allow/block works automatically on all plans. Pay Per Crawl is a closed/private beta (apply or contact account exec); payout/fee economics not specified in docs. (verify — drifts)

**Limits:**
- Pay Per Crawl is closed beta and access-gated; docs do not enumerate participating AI companies or payout terms
- WAF and Bot Management rules take precedence — a blocked crawler stays blocked regardless of Pay Per Crawl
- Blocking depends on crawler identification; well-behaved bots are easy, disguised/stealth scrapers are the hard case (lean on Bot Management here)
- Renamed from 'AI Audit' — older references/UI may still use the old name

**Notes:** Honest caveats: this is the renamed AI Audit, so memory/older docs may mislead. Monetization (Pay Per Crawl) is real but closed-beta and Cloudflare-as-Merchant-of-Record (lock-in + revenue-share implied but unverified here). It complements, not replaces, Bot Management for stealthy scrapers that spoof user-agents.

**Docs:** https://developers.cloudflare.com/ai-crawl-control/index.md, https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/what-is-pay-per-crawl/index.md, https://developers.cloudflare.com/ai-crawl-control/features/manage-ai-crawlers/index.md, https://developers.cloudflare.com/ai-crawl-control/reference/graphql-api/index.md

---

## Cloudflare API Shield
`cloudflare-api-shield` · Security / API Security · confidence: `high` · lock-in: `portable`

**Is:** A positive-security layer for APIs: discovers your endpoints, validates requests against an uploaded OpenAPI v3 schema, enforces mTLS / JWT auth, and detects BOLA, volumetric abuse, and anomalous call sequences.

**Replaces:** Hand-built API gateway security — Kong/Apigee plugins for schema validation and JWT checks, a self-managed mTLS client-cert PKI, and DIY per-endpoint rate limiting plus the request-shape validation (zod/joi/ajv) you scatter across handlers.

**Use it via:** REST under /zones/{zone_id}/api_gateway/* (operations, schemas, configurations, user_schemas) and the rulesets API for schema-validation actions; expression field cf.api_gateway.fallthrough_detected for catch-all WAF logic. Configurable via dashboard, API, or Terraform.

**Capabilities:**
- Schema validation against OpenAPI v3: log or block requests that violate target endpoint / path / query format / HTTP method
- API Discovery: surfaces shadow/undocumented endpoints from observed traffic
- mTLS / client certificate enforcement (incl. bring-your-own CA) — available to all customers
- JWT validation at the edge (validate claims before traffic hits origin; optional JWT Worker, Transform Rule enrichment)
- BOLA (Broken Object Level Authorization) vulnerability detection
- GraphQL malicious-query protection (depth/complexity limits)
- Volumetric Abuse Detection and Sequence Analytics / sequence mitigation (per-session API call-flow analysis)
- Session identifiers, endpoint labeling, schema learning, and a fallthrough rule for unidentified endpoints (cf.api_gateway.fallthrough_detected)

**Detection signals — the lens fires on these:**
- Per-request body validation duplicated across routes: zod, joi, ajv, yup, class-validator, pydantic / FastAPI models, express-openapi-validator
- An openapi.yaml / swagger.json in the repo that's only used for docs, not enforcement
- Hand-rolled JWT verification on every route: jsonwebtoken, jose, passport-jwt middleware
- DIY mTLS / client-cert handling or a private PKI (step-ca, openssl-generated client certs) terminated at nginx
- GraphQL servers without depth/complexity guards (graphql-depth-limit absent), or custom query-cost middleware
- Custom IDOR/object-ownership checks suggesting BOLA risk; manual per-endpoint rate limits
- API-gateway security plugins (Kong jwt/acl, Apigee policies, AWS API Gateway authorizers) you maintain

**Ideas:**
- Upload the existing openapi.yaml to Schema Validation so malformed requests are rejected at the edge, and delete the duplicated zod/ajv validation from every route handler
- Move per-route jsonwebtoken verification into edge JWT validation so unauthenticated/expired tokens never reach origin
- Run API Discovery to find shadow endpoints, then add a fallthrough rule that blocks requests to anything not in your schema

**Pairs with:** cloudflare-waf, cloudflare-bots, cloudflare-challenges

**Pricing:** Endpoint Management and Schema Validation are available on all plans with tiered limits (Free: 100 saved endpoints / 5 schemas / 200kB & 1kB body inspection; scaling up to Enterprise: 10,000 endpoints / larger schemas / 128kB body). mTLS is available to all customers. The full suite (API Discovery, BOLA, sequence analytics, volumetric abuse, JWT validation at scale) is an Enterprise paid API Shield / API Gateway add-on — upgrade to Enterprise and contact your account team. (verify - drifts)

**Limits:**
- Request-body inspection is size-capped per plan (Free 1kB -> Enterprise 128kB), so very large payloads are only partially validated
- Schema validation requires endpoints to be in Endpoint Management first (auto when uploading via dashboard; manual via API/Terraform)
- API Discovery, BOLA detection, sequence/volumetric features are Enterprise add-on, not free-tier
- Enterprise schemas cap at ~10,000 operations each

**Notes:** The standout 'stop building this' is schema validation replacing per-route request validators + the manual mTLS/JWT plumbing. Verified the all-plans schema/mTLS availability and the Enterprise gating for discovery/BOLA/sequence from the plans + schema-validation pages this run.

**Docs:** https://developers.cloudflare.com/api-shield/llms.txt, https://developers.cloudflare.com/api-shield/index.md, https://developers.cloudflare.com/api-shield/plans/index.md, https://developers.cloudflare.com/api-shield/security/schema-validation/index.md

---

## Cloudflare Bot Management / Bot Fight Mode
`cloudflare-bots` · Security / Bot Mitigation · confidence: `high` · lock-in: `portable`

**Is:** Scores every request 1-99 for bot likelihood using ML, heuristics, behavioral/anomaly analysis and JS detections, then lets you challenge or block automated traffic (scraping, credential stuffing, inventory hoarding) via rules.

**Replaces:** Rolling your own bot detection — user-agent allowlists, reCAPTCHA Enterprise / DataDome / PerimeterX (HUMAN) subscriptions, IP-reputation lookups, and homegrown fingerprinting to spot scrapers and credential-stuffers.

**Use it via:** Rules-language fields cf.bot_management.* (score, verified_bot, static_resource, js_detection.passed) consumed in WAF custom rules (rulesets API) and in Workers via request.cf.botManagement. Super Bot Fight Mode toggles via dashboard/API; Bot Management is an Enterprise add-on entitlement on the zone.

**Capabilities:**
- Per-request bot score 1-99 (scores below ~30 strongly indicate bots), exposed as cf.bot_management.score for use in WAF custom rules and Workers
- Detection engines: machine learning (auto-updated models), heuristics, anomaly detection, and JavaScript Detections (cf.bot_management.js_detection.passed)
- Verified Bots allowlist (cf.bot_management.verified_bot) and bot tags; static-resource flag (cf.bot_management.static_resource)
- Bot Fight Mode (free) and Super Bot Fight Mode (Pro/Business) for category-based challenge/block toggles
- JA3/JA4 TLS fingerprints, Detection IDs, sequence rules, and session-based analysis (Enterprise)
- Bot Analytics dashboards and detection alerts
- AI-bot controls: block AI crawlers, and AI Labyrinth (feeds misbehaving crawlers decoy content)

**Detection signals — the lens fires on these:**
- reCAPTCHA / hCaptcha keys (RECAPTCHA_SECRET_KEY, grecaptcha, @hcaptcha/react-hcaptcha) bolted onto login/signup/checkout
- Bot-vendor SDKs: datadome, @datadome/*, perimeterx, @humansecurity/*, kasada in package.json
- Hand-rolled user-agent allow/deny lists or isbot/crawler-detect usage
- Custom TLS/HTTP fingerprinting (ja3 libraries) or per-IP request-pattern heuristics for scraping
- Credential-stuffing defenses on /login: velocity counters, device fingerprinting libraries (fingerprintjs)
- Inventory/scalper protection logic on add-to-cart or ticketing endpoints
- A robots.txt + manual IP blocks as the only line against AI crawlers / scrapers

**Ideas:**
- Swap the reCAPTCHA gate on signup/login for a WAF custom rule that Managed-Challenges requests where cf.bot_management.score < 30, removing the JS dependency and friction for humans
- Protect checkout / add-to-cart from inventory-hoarding bots with a bot-score rule instead of a third-party bot-defense subscription
- Turn on Block AI Bots (or AI Labyrinth) to stop LLM scrapers that ignore robots.txt

**Pairs with:** cloudflare-waf, cloudflare-challenges, cloudflare-ddos-protection, cloudflare-api-shield

**Pricing:** Bot Fight Mode is free (a single toggle, no scores). Super Bot Fight Mode comes with Pro/Business plans. The full per-request bot score (cf.bot_management.score), JA3/JA4, detection IDs, sequence rules and Bot Analytics require the Enterprise Bot Management add-on (contact sales). (verify - drifts)

**Limits:**
- cf.bot_management.score and the rich signals are Enterprise-only; Free/Pro/Business get coarser category toggles
- Bot Fight Mode is blunt (no scoring, can challenge good automation) and is the free floor, not the real product
- Only sees traffic proxied through Cloudflare
- JS Detections require the challenge JS to run, so pure API/native clients rely on other signals

**Notes:** Confirmed via the ruleset-engine field reference that cf.bot_management.score (1-99) requires Enterprise + Bot Management. The free/paid gap is large — pitch Enterprise Bot Management only when a team already pays a bot-defense vendor or runs serious anti-scraping/anti-fraud logic; otherwise Super Bot Fight Mode is the realistic target.

**Docs:** https://developers.cloudflare.com/bots/llms.txt, https://developers.cloudflare.com/bots/index.md, https://developers.cloudflare.com/bots/get-started/bot-management/index.md, https://developers.cloudflare.com/bots/plans/index.md

---

## Cloudflare Challenges (Managed Challenge + Turnstile)
`cloudflare-challenges` · Security / Human Verification · confidence: `high` · lock-in: `portable`

**Is:** A no-puzzle human-verification platform: Managed Challenge issues adaptive browser checks via WAF rules, and Turnstile is the embeddable, free CAPTCHA-replacement widget you drop into your own forms with server-side siteverify.

**Replaces:** Google reCAPTCHA v2/v3 or hCaptcha — the visual 'select the traffic lights' puzzles, the per-call scoring you pay for, and the privacy/UX baggage that comes with them.

**Use it via:** Issue challenges by setting action 'managed_challenge' / 'js_challenge' / 'interactive' in a WAF custom rule (rulesets API). Turnstile: client renders <div class="cf-turnstile" data-sitekey=...> + script challenges.cloudflare.com/turnstile/v0/api.js, then server POSTs the token to https://challenges.cloudflare.com/turnstile/v0/siteverify. Turnstile sitekeys/secrets managed via dashboard or the Turnstile API.

**Capabilities:**
- Managed Challenge: adaptive challenge issued as a WAF custom-rule / managed-rule action; most humans pass with no interaction (no CAPTCHA puzzles)
- JavaScript Detections (lightweight non-interactive browser check) and Interactive Challenge for higher-friction cases
- Turnstile: embeddable widget (Managed / Non-interactive / Invisible modes) as a standalone reCAPTCHA/hCaptcha drop-in replacement
- Server-side token verification via the Siteverify API (critical to enforce — tokens can be reused/expired)
- Clearance cookie + Challenge Passage so a passed visitor isn't re-challenged for a configurable window
- Private Access Tokens (PATs) let supported Apple devices attest without any challenge UI
- Challenge Solve Rate (CSR) analytics; broad browser/language support

**Detection signals — the lens fires on these:**
- reCAPTCHA: grecaptcha, g-recaptcha, RECAPTCHA_SITE_KEY/SECRET_KEY, https://www.google.com/recaptcha/ script tags
- hCaptcha: @hcaptcha/react-hcaptcha, HCAPTCHA_SECRET, h-captcha class
- Any homegrown 'are you human' gate: math questions, honeypot fields, JS proof-of-work on forms
- Server code calling google.com/recaptcha/api/siteverify or hcaptcha.com/siteverify
- A login/signup/contact/comment form with no bot gate at all (candidate to add Turnstile)
- Custom challenge-cookie logic to remember 'this visitor already proved human'

**Ideas:**
- Replace the reCAPTCHA widget on signup/login/contact forms with Turnstile (same render+siteverify shape) to drop the Google dependency and lose the image puzzles
- Instead of embedding any widget, gate the abused endpoint with a WAF Managed Challenge rule so verification happens at the edge with zero app code
- Add Turnstile in Invisible mode to a comment/newsletter form to stop spam without adding user friction

**Pairs with:** cloudflare-bots, cloudflare-waf, cloudflare-ddos-protection

**Pricing:** Managed Challenge is included with WAF/Bot products on the zone (it's a rule action). Turnstile has a free tier and is widely used as a free reCAPTCHA replacement; higher-volume/Enterprise tiers exist. (verify - drifts — exact Turnstile free request volume not confirmed on the pages fetched this run.)

**Limits:**
- Managed Challenge (as a WAF action) only applies to traffic proxied through Cloudflare; Turnstile works anywhere because YOU embed and verify it
- Turnstile is worthless without server-side Siteverify enforcement — a token alone proves nothing
- Private Access Tokens depend on client OS/device support (Apple ecosystem)
- Not a substitute for bot SCORING — Challenges verify humanness at a point; Bot Management scores every request continuously

**Notes:** Turnstile is the cleanest standalone 'stop paying/embedding reCAPTCHA' hook and runs on any stack (not just Cloudflare-proxied sites). Cloudflare explicitly states it does NOT use CAPTCHA puzzles. Overview + Turnstile pages verified this run; Turnstile pricing specifics not nailed down here.

**Docs:** https://developers.cloudflare.com/cloudflare-challenges/llms.txt, https://developers.cloudflare.com/cloudflare-challenges/index.md, https://developers.cloudflare.com/cloudflare-challenges/challenge-types/turnstile/index.md

---

## Cloudflare Client-Side Security (Page Shield)
`cloudflare-client-side-security` · Security / Client-Side & Supply Chain · confidence: `high` · lock-in: `portable`

**Is:** Browser-side supply-chain monitoring that uses Content-Security-Policy report-only headers to inventory every script and outbound connection on your pages, flags malicious/changed third-party code (Magecart-style skimmers), and can enforce CSP allowlists.

**Replaces:** Hand-writing and babysitting your own Content-Security-Policy, standing up a CSP violation-report collector (report-uri.com or a self-hosted report-to endpoint), and DIY Subresource-Integrity / dependency-drift monitoring to catch compromised third-party JS.

**Use it via:** REST under /zones/{zone_id}/page_shield/* (settings, scripts, connections, cookies, policies). Works by Cloudflare auto-injecting content-security-policy-report-only headers and ingesting the browser's violation reports — no app code or SDK to install. Dashboard + API.

**Capabilities:**
- Script & connection inventory: injects a content-security-policy-report-only header on a sample of HTML, then builds the list of scripts and the third-party endpoints they call from browser violation reports
- Cookie monitoring (origin- and browser-set)
- Malicious script detection via threat feeds + ML, plus detection of unexpected changes to existing scripts (Client-Side Security Advanced)
- Page attribution (where a script first appeared) and script statuses
- Alerts: new scripts, unknown-domain resources, malicious code, code changes (delivered via the notification service)
- Content Security Rules: enforce allowlists (CSP directives) of permitted scripts/connections, with violation reporting
- PCI DSS 4.0 (6.4.3 / 11.6.1) support for payment-page script integrity and tamper detection

**Detection signals — the lens fires on these:**
- Hand-maintained Content-Security-Policy headers in nginx.conf / helmet() / middleware that drift every time a vendor script changes
- A custom CSP report-to / report-uri endpoint or a report-uri.com / Report URI subscription
- Many third-party <script src> tags (analytics, tag managers, chat widgets, payment iframes) with no integrity monitoring
- Google Tag Manager / Segment / ad pixels loading arbitrary downstream scripts you don't control
- Payment/checkout pages subject to PCI DSS that load third-party JS (Magecart skimmer risk)
- Subresource Integrity (integrity= hashes) applied manually and going stale
- An e-commerce stack (Shopify-on-custom, Magento, WooCommerce) where client-side skimming is a known threat

**Ideas:**
- Turn on Page Shield in report-only mode to get an inventory of every third-party script and outbound connection on checkout, then promote the safe set into a Content Security Rule allowlist
- Use malicious-script + code-change detection to satisfy PCI DSS 4.0 6.4.3 / 11.6.1 instead of building your own payment-page tamper monitoring
- Replace the self-hosted CSP violation-report collector with Page Shield's built-in reporting and alerts

**Pairs with:** cloudflare-waf, cloudflare-security-center

**Pricing:** Available on all plans, tiered: Free/Pro get basic script monitoring; Business/Enterprise add connection + cookie monitoring, page attribution, and alerts; Client-Side Security Advanced adds malicious-script + code-change detection and content security rules (up to ~5 rules). (verify - drifts)

**Limits:**
- Monitoring relies on CSP-report-only headers, which only fire in browsers that send reports and on a sample of HTML responses — non-browser clients are invisible
- Malicious-script classification and the enforcing Content Security Rules require the Advanced tier; lower tiers are observe-only
- Detects/reports but you still decide policy; an allowlist that's too tight can break legitimate vendor scripts
- Only covers pages served through Cloudflare

**Notes:** The docs call this 'client-side security' rather than the older 'Page Shield' branding, but it is the Page Shield product. Strongest pitch is for PCI-scoped e-commerce/checkout pages and any site drowning in third-party tags. The no-SDK, header-injection mechanism is verified from the how-it-works page this run.

**Docs:** https://developers.cloudflare.com/client-side-security/llms.txt, https://developers.cloudflare.com/client-side-security/index.md, https://developers.cloudflare.com/client-side-security/how-it-works/index.md

---

## Cloudflare DDoS Protection
`cloudflare-ddos-protection` · Security / DDoS Mitigation · confidence: `high` · lock-in: `portable`

**Is:** Always-on, autonomous DDoS mitigation across L3/4 (network) and L7 (HTTP) that fingerprints attacks out-of-path and applies surgical real-time rules at Cloudflare's edge, typically within ~3 seconds.

**Replaces:** Paying for AWS Shield Advanced / a scrubbing-center provider (Arbor, Radware) or trying to absorb volumetric floods yourself with origin autoscaling and upstream nullrouting.

**Use it via:** Configured as Ruleset Engine managed rulesets via the rulesets API (ddos_l7 and ddos_l4 phases) with override entries (sensitivity_level, action) — dashboard, API, or Terraform. Advanced TCP/DNS Protection is configured at the Magic Transit account level.

**Capabilities:**
- Autonomous edge mitigation: samples traffic out-of-path (no added latency), generates a real-time signature, distributes the fingerprint network-wide
- HTTP DDoS Attack Protection managed ruleset (L7) with rule categories + overrides (sensitivity, action)
- Network-layer DDoS Attack Protection managed ruleset (L3/4)
- Adaptive DDoS Protection: learns your traffic baseline to catch attacks that mimic legitimate patterns
- Actions: Block, Managed Challenge, Interactive Challenge, Log, or rule defaults; tunable via HTTP/network overrides
- Botnet Threat Feed; Advanced TCP Protection (stateful out-of-state SYN/ACK/RST flood engine) and Advanced DNS Protection for Magic Transit
- Programmable Flow Protection for flow-based (Magic) deployments
- Alerts and DDoS analytics

**Detection signals — the lens fires on these:**
- Origin-side rate/connection limiting meant to survive floods: fail2ban, nginx limit_conn, HAProxy stick-tables sized for attack traffic
- Autoscaling rules whose trigger is really 'absorb a traffic spike' rather than real demand
- aws-shield / AWS WAF rate-based rules, or a Cloudflare-competitor scrubbing vendor in infra config
- Manual upstream/BGP nullroute or ACL runbooks for 'when we get DDoSed'
- Bare-IP origins exposed publicly (L3/4 floods can hit them directly)
- Synflood/connection-exhaustion tuning in sysctl.conf (net.ipv4.tcp_syncookies, somaxconn) as a DDoS measure

**Ideas:**
- Proxy the zone through Cloudflare so the HTTP DDoS managed ruleset absorbs L7 floods, then tighten the override sensitivity on high-value endpoints
- For raw-IP / non-HTTP services being SYN-flooded, move them behind Magic Transit + Advanced TCP Protection instead of hand-tuning syncookies
- Replace the autoscaling-to-eat-spikes pattern with edge mitigation so origin capacity tracks real demand, not attack volume

**Pairs with:** cloudflare-waf, cloudflare-bots, cloudflare-challenges

**Pricing:** Unmetered L3/4 + L7 DDoS mitigation is included on ALL Cloudflare plans (including Free) for proxied traffic. Adaptive Protection and finer override control skew to higher plans; Advanced TCP/DNS Protection are part of the Magic Transit product (Enterprise, contact sales). (verify - drifts)

**Limits:**
- HTTP DDoS ruleset only protects proxied (orange-cloud) HTTP; non-proxied origins and raw IPs need Magic Transit/Spectrum for L3/4 coverage
- Advanced TCP Protection is Magic Transit-scoped, not a knob for a normal website zone
- Tuning is via managed-ruleset overrides (sensitivity/action), not arbitrary custom DDoS logic
- Could not pull a per-plan feature matrix for Adaptive Protection from the pages fetched this run

**Notes:** The free unmetered mitigation is the headline: most teams should never hand-build volumetric defense. The real decision is L7 (any plan, proxied) vs L3/4 at-the-IP (needs Magic Transit/Spectrum). How-it-works and Advanced TCP pages verified this run; some plan-tier specifics inferred.

**Docs:** https://developers.cloudflare.com/ddos-protection/llms.txt, https://developers.cloudflare.com/ddos-protection/about/how-ddos-protection-works/index.md, https://developers.cloudflare.com/ddos-protection/advanced-ddos-systems/overview/advanced-tcp-protection/index.md

---

## Cloudflare DMARC Management
`cloudflare-dmarc-management` · Security / Email Authentication · confidence: `medium` · lock-in: `sticky`

**Is:** A free DMARC aggregate-report processor for domains on Cloudflare DNS: it ingests RUA reports, shows every source sending mail as your domain, and tells you whether each passed SPF, DKIM, and DMARC so you can safely move to p=reject.

**Replaces:** Paying a DMARC SaaS (Dmarcian, Valimail, EasyDMARC, Postmark's DMARC Digests) or building your own RUA mailbox + XML-report parser to make sense of raw aggregate reports.

**Use it via:** Enabled from the Cloudflare dashboard for an apex domain on Cloudflare DNS; it publishes a DMARC TXT record with rua pointing at a Cloudflare-managed report address and parses inbound aggregate reports (built on Cloudflare Email Routing). Primarily a dashboard product layered on DNS records.

**Capabilities:**
- Processes DMARC aggregate (RUA) reports for your apex domain automatically once enabled
- Tracks every source sending email from your domain and shows pass/fail for SPF, DKIM, and DMARC per source
- Helps you configure the SPF, DKIM, and DMARC DNS records (managed within Cloudflare DNS)
- Statistics & details view to spot unauthorized senders / spoofing and tighten policy (p=none -> quarantine -> reject)
- Reduces the operational burden of finding legitimate senders before enforcing a strict policy

**Detection signals — the lens fires on these:**
- A _dmarc TXT record stuck at p=none (monitor-only) that never advanced to quarantine/reject
- rua=mailto: pointing at a paid DMARC vendor (dmarcian.com, valimail, easydmarc, agari) — they're paying for what Cloudflare does free
- A self-hosted RUA inbox plus a homegrown/OSS XML aggregate-report parser (parsedmarc) and a dashboard to visualize it
- Missing or messy SPF/DKIM records, or an SPF record near the 10-DNS-lookup limit
- Domain already using Cloudflare nameservers but DMARC reports handled elsewhere
- Brand-impersonation / spoofing concerns raised but no enforcing DMARC policy

**Ideas:**
- Point the domain's DMARC rua at Cloudflare DMARC Management to retire the paid DMARC SaaS subscription and still get per-source SPF/DKIM/DMARC pass-fail visibility
- Use the source breakdown to discover every legitimate sender, then graduate the policy from p=none to p=reject to stop brand-impersonation
- Replace a self-hosted parsedmarc + report mailbox pipeline with the built-in dashboard

**Pairs with:** cloudflare-security-center, cloudflare-waf

**Pricing:** Available on all plans at no additional cost. Requires the domain to be on Cloudflare DNS and a destination for reports (built on Cloudflare Email Routing, also free). (verify - drifts)

**Limits:**
- Requires your domain to use Cloudflare DNS / nameservers — not usable if DNS lives elsewhere
- Processes aggregate (RUA) reports; it surfaces sending sources and auth results, not full forensic (RUF) message-level captures
- It reports and guides — it does not send your mail or fix SPF/DKIM alignment for you
- The get-started doc page 404'd this run; setup specifics drawn from the overview page and Cloudflare email-auth docs (verify the exact rua flow)

**Notes:** Squarely a 'stop paying a DMARC vendor' play for anyone already on Cloudflare DNS. The hard requirement is Cloudflare DNS. Overview page (free, all plans, RUA processing, requires Cloudflare DNS + mailbox) verified this run; MCP search corroborated the DMARC record/rua mechanics. The dedicated get-started page returned 404 — confirm the current enablement path.

**Docs:** https://developers.cloudflare.com/dmarc-management/llms.txt, https://developers.cloudflare.com/dmarc-management/index.md

---

## Cloudflare Rate Limiting Rules
`cloudflare-rate-limiting-rules` · Security / Rate limiting · confidence: `high` · lock-in: `portable`

**Is:** Ruleset Engine-backed request throttling/block/challenge policies for websites and APIs, replacing origin Redis token buckets, nginx limit_req, app middleware, and many bespoke abuse counters.

**Replaces:** express-rate-limit, Rack::Attack, Django ratelimit, nginx `limit_req`, Redis INCR+TTL token buckets, API Gateway usage plans, or app tables that only count requests per IP/user/path.

**Use it via:** Dashboard: WAF > Rate limiting rules. API/Terraform through Rulesets API phase `http_ratelimit` / WAF rate limiting rules configuration (Cloudflare Terraform `cloudflare_ruleset`). Rule parameters include expression, action, characteristics, period, requests_per_period, and mitigation timeout.

**Capabilities:**
- Define match expressions with Cloudflare Rules language
- Choose counting characteristics such as source IP, path, query, host, headers, cookies, ASN, country, JA3/JA4, body/form fields, and JSON fields depending on plan
- Configure period, requests per period, mitigation timeout, and action
- Actions include block/challenge-style WAF actions when limits are exceeded
- Advanced Rate Limiting supports richer characteristics, complexity-based rate limiting, and account-level rate-limiting rulesets for some Enterprise customers
- Terraform and Rulesets API support zone rate limiting rules

**Detection signals — the lens fires on these:**
- npm deps: express-rate-limit, rate-limiter-flexible, bottleneck, koa-ratelimit
- Ruby Rack::Attack, Django ratelimit, Flask-Limiter, Laravel throttle middleware, Go tollbooth/limiter packages
- Redis `INCR` + `EXPIRE` / TTL counters keyed by IP/user/path
- nginx `limit_req_zone` / `limit_req`, Envoy local_rate_limit, Kong rate-limiting plugin
- Login/API abuse tables storing request_count/window_start/blocked_until
- API route middleware whose only job is per-IP or per-token throttling before origin code

**Ideas:**
- Move login/API endpoint throttling to Rate Limiting Rules before traffic hits the app, deleting Redis counters and middleware.
- Use WAF Rate Limiting for edge-abuse control; keep a Durable Object or app-side quota only when the limit depends on authenticated business state Cloudflare cannot see.
- Pair with Bot Management or Turnstile when rate limits are part of a broader abuse defense.

**Pairs with:** WAF, Ruleset Engine, Bot Management, Turnstile, Durable Objects (business-state quota fallback), Workers Rate Limiting binding

**Pricing:** Availability and rule counts vary by plan: Free includes 1 simple IP-only rule; Pro, Business, and Enterprise unlock more rules/fields. Verify the current availability table before quoting.

**Limits:**
- Rate Limiting Rules are not designed to allow an exact number of requests to reach origin; counter updates can lag by a few seconds
- Fields, counting characteristics, counting periods, mitigation timeout, custom expressions, and number of rules vary heavily by plan
- Rules are evaluated in order, and some actions stop evaluation of later rules
- Rate limiting verified bots can affect SEO

**Notes:** Do not bury this inside generic WAF advice; rate limiting is one of the highest-yield hand-rolled infra smells. Still be precise: origin/app limits remain appropriate for per-account billing quotas or state Cloudflare cannot observe at the edge.

**Docs:** https://developers.cloudflare.com/waf/llms.txt, https://developers.cloudflare.com/waf/rate-limiting-rules/index.md, https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/index.md, https://developers.cloudflare.com/waf/rate-limiting-rules/request-rate/index.md, https://developers.cloudflare.com/terraform/additional-configurations/rate-limiting-rules/

---

## Cloudflare SSL/TLS
`cloudflare-ssl-tls` · Security / Certificates · confidence: `high` · lock-in: `portable`

**Is:** Automatic free TLS certs for every proxied hostname (Universal SSL), plus an origin CA, keyless SSL, and Cloudflare-PKI client certificates for mutual TLS.

**Replaces:** Hand-rolled certbot/Let's Encrypt renewal cron on every box, a paid cert vendor (DigiCert, Sectigo), and DIY mTLS/PKI for service and IoT auth.

**Use it via:** Edge certs: /zones/{zone_id}/ssl/certificate_packs and /ssl/universal/settings. Origin CA: GET/POST/GET/DELETE /certificates (token needs Zone-SSL-and-Certificates:Edit). Client certs / mTLS: /zones/{zone_id}/client_certificates and account-level mTLS CA hostname associations. Custom certs: /zones/{zone_id}/custom_certificates. Terraform: cloudflare_certificate_pack, cloudflare_origin_ca_certificate, cloudflare_mtls_certificate.

**Capabilities:**
- Universal SSL: free, unshared, publicly-trusted DV certs auto-issued and auto-renewed once a domain is active (apex + first-level subdomains on full setup; any-depth proxied hostname on partial/CNAME setup)
- Total TLS: extends auto-issuance to proxied subdomains at any level
- Advanced Certificate Manager (ACM): custom SANs (up to 50), wildcards, multi-level subdomains, choice of CA, custom validity, custom validation
- Custom certificates: upload and serve your own edge certs (BYO cert)
- Origin CA: free long-lived certs for the Cloudflare-to-origin hop, issued via API
- Encryption (SSL) modes: Off / Flexible / Full / Full (strict) to control edge-to-origin trust; Authenticated Origin Pulls (mTLS) to prove requests came from Cloudflare
- Client certificates / mTLS: account-level Cloudflare-managed PKI (or BYOCA on Enterprise) to require client certs; verification exposed as cf.tls_client_auth.cert_verified for Access / API Shield / Workers
- Keyless SSL: keep private keys in your own infra/HSM while Cloudflare terminates TLS
- Delegated DCV and custom TLS settings (min TLS version, cipher suites)

**Detection signals — the lens fires on these:**
- certbot, acme.sh, lego, cert-manager, or greenlock in the repo; cron jobs calling certbot renew
- LETSENCRYPT_* env vars, /etc/letsencrypt mounts, or *.pem / fullchain.pem files committed or baked into Docker images
- Paid-CA artifacts: DigiCert/Sectigo order scripts, manual CSR generation steps in a runbook
- Hand-rolled mTLS: openssl ca/x509 scripts generating a client-cert PKI, custom CA bundles shipped to IoT/devices, nginx ssl_verify_client config
- Nginx/Envoy/HAProxy TLS-termination config maintained purely to renew and serve public certs
- Origin still on self-signed certs with verification disabled (candidate for Origin CA + Full strict)

**Ideas:**
- Drop the per-server certbot renewal cron and let Universal SSL (or Total TLS for deep subdomains) auto-issue and rotate edge certs
- Issue an Origin CA cert and move encryption mode to Full (strict) to close the edge-to-origin gap without buying a public cert for the origin
- Replace a DIY client-cert PKI for API/IoT auth with Cloudflare client certificates + mTLS enforcement, reading cert_verified in API Shield or a Worker

**Pairs with:** cloudflare-dns, cloudflare-spectrum, cloudflare-registrar

**Pricing:** Universal SSL + Origin CA + encryption modes free on all plans. Advanced Certificate Manager is a paid add-on (Pro/Business/Enterprise) with a per-zone/per-cert fee; Enterprise can buy up to 100 edge certs/zone. BYOCA for client certs is Enterprise-only. (verify — drifts)

**Limits:**
- Universal SSL on full setup covers only apex + first-level subdomains; deeper needs Total TLS or ACM
- Universal SSL certs are issued only after domain activation (no pre-migration cert)
- Universal SSL / ACM are DV-only (no OV/EV)
- ACM certificates are single-domain (not multi-domain) and do not apply to Pages or R2 custom domains
- Origin CA sends no expiration notifications — you must track renewals yourself
- Keyless SSL and BYOCA are higher-tier/Enterprise features

**Notes:** For proxied sites the free tier removes nearly all cert ops. Keyless SSL is the escape hatch when compliance forbids handing private keys to a CDN. mTLS client-cert verification is powerful but ties device/API auth to Cloudflare PKI; BYOCA (to keep your own root) is Enterprise-gated. The official CA(s) behind Universal SSL were not named on the pages fetched.

**Docs:** https://developers.cloudflare.com/ssl/llms.txt, https://developers.cloudflare.com/ssl/index.md, https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/index.md, https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/index.md, https://developers.cloudflare.com/ssl/client-certificates/index.md, https://developers.cloudflare.com/ssl/edge-certificates/advanced-certificate-manager/index.md

---

## Cloudflare Secrets Store
`secrets-store` · Security & Secrets Management · confidence: `high` · lock-in: `portable`

**Is:** A secure, account-level vault that stores encrypted secrets once and makes them reusable across your Cloudflare account (Workers, AI Gateway), so credentials never live in code or per-Worker config.

**Replaces:** HashiCorp Vault / AWS Secrets Manager / Doppler — or the common DIY pattern of copy-pasting the same API key into every Worker's plaintext vars or per-service `wrangler secret put`, with no central rotation or audit.

**Use it via:** Worker binding: `secrets_store_secrets` array in wrangler.jsonc/.toml with keys `binding`, `store_id`, `secret_name`; read in code via `await env.<BINDING>.get()` (async). Wrangler: `wrangler secrets-store store create <name> --remote`, plus secret create/duplicate/update/scope/delete subcommands. REST: `POST/GET/DELETE /accounts/{account_id}/secrets_store/stores`, `POST/GET/PATCH/DELETE /accounts/{account_id}/secrets_store/stores/{store_id}/secrets[/{secret_id}]`, `.../secrets/{secret_id}/duplicate`, and `GET /accounts/{account_id}/secrets_store/quota`.

**Capabilities:**
- Account-scoped secret storage encrypted across all Cloudflare data centers, reusable by multiple Workers/services instead of duplicated per-project
- Workers binding: read a secret at runtime via async `await env.<BINDING>.get()` — no plaintext in wrangler config
- Full CRUD over secrets via dashboard, REST API, and Wrangler: create, duplicate, edit/rotate value, scope, and delete
- Role-based access control (Super Administrator, Secrets Store Admin, Secrets Store Deployer) plus `Secrets Store Write` permission gating
- Audit logs for create/update/delete actions on secrets
- AI Gateway 'Bring Your Own Keys' integration — store upstream LLM provider API keys centrally

**Detection signals — the lens fires on these:**
- Same API key / credential duplicated across multiple Workers as plaintext `vars` in several wrangler.jsonc/wrangler.toml files
- Repeated `wrangler secret put SAME_NAME` run against many separate Worker projects (no central source of truth for rotation)
- Secrets committed to .dev.vars or hardcoded in Worker source / committed to the repo
- LLM provider keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.) embedded per-Worker instead of centralized — pairs with AI Gateway BYOK
- DIY secret-fetch glue: Workers calling out to AWS Secrets Manager / HashiCorp Vault / Doppler on cold start (env vars like VAULT_ADDR, VAULT_TOKEN, DOPPLER_TOKEN, AWS_SECRETS_MANAGER_*) just to feed a Worker
- No audit trail or RBAC around who can read/rotate shared credentials across the Cloudflare account

**Ideas:**
- Centralize a third-party API key (Stripe, Twilio, etc.) shared by several Workers into one Secrets Store entry bound via `secrets_store_secrets`, then rotate it in one place instead of redeploying every Worker.
- Move LLM provider keys out of individual Workers into Secrets Store and wire them through AI Gateway 'Bring Your Own Keys' for centralized, audited key management.
- Replace a Worker's runtime call to AWS Secrets Manager / Vault with a native Secrets Store binding to cut a network dependency and cold-start latency.

**Pairs with:** Cloudflare Workers (primary consumer via secrets_store_secrets binding), AI Gateway (Bring Your Own Keys for LLM provider credentials), Wrangler (provisioning and CI/CD secret management)

**Pricing:** No standalone pricing surfaced in docs; positioned as an account platform feature alongside Workers. Unit of constraint is secret count, not a metered $ figure. (verify — drifts)

**Limits:**
- 100 secrets per account (per May 2025 pay-as-you-go changelog) — verify, beta quota likely to rise
- In open beta — feature set and limits subject to change
- Unavailable on the Cloudflare China Network (operated by partner JD Cloud)
- Production secrets cannot be read from local development; use Wrangler without `--remote` for local testing
- Binding a secret to a Worker requires Super Administrator or Secrets Store Deployer role; managing secrets requires Super Administrator or Secrets Store Admin
- Secret `name` cannot contain spaces

**Notes:** Open-beta product (launched Apr 2025), so the 100-secret cap and exact wrangler subcommand flags should be re-verified before relying on them — the how-to page punts CLI flag specifics to the general Wrangler reference, and only the beta changelog gives the verbatim `store create` command. It is account-level secret storage for the Cloudflare ecosystem, NOT a general-purpose enterprise secrets manager: it does not replace Vault for non-Cloudflare workloads, has no dynamic/leased secrets, no secret versioning history beyond edit, and only Workers + AI Gateway are wired up so far. China Network exclusion matters for global deployments. For app-data encryption keys or per-user secrets it's the wrong tool — this is for shared service/account credentials.

**Docs:** https://developers.cloudflare.com/secrets-store/llms.txt, https://developers.cloudflare.com/secrets-store/index.md, https://developers.cloudflare.com/secrets-store/integrations/workers/index.md, https://developers.cloudflare.com/secrets-store/manage-secrets/how-to/index.md, https://developers.cloudflare.com/api/resources/secrets_store/index.md, https://developers.cloudflare.com/changelog/post/2025-04-09-secrets-store-beta/, https://developers.cloudflare.com/changelog/post/2025-05-19-paygo-updates/

---

## Cloudflare Security Center
`cloudflare-security-center` · Security / Posture & Threat Intelligence · confidence: `high` · lock-in: `portable`

**Is:** A unified security console that scans your Cloudflare account for misconfigurations (Security Insights), maps your internet-facing attack surface, exposes Cloudflare's threat-intelligence for IP/domain/ASN lookups, and detects brand-impersonation domains.

**Replaces:** A grab-bag of paid tools — an external attack-surface-management product (e.g. expanse-style ASM), a threat-intel enrichment subscription for IP/domain reputation, and a brand-protection / anti-phishing domain-monitoring service.

**Use it via:** REST under /accounts/{account_id}/intel/* (Investigate / Intel APIs: domain, ip, asn, whois, passive DNS), Security Center insights endpoints, and Brand Protection APIs for programmatic query management + SIEM/SOC export. Dashboard + API.

**Capabilities:**
- Security Insights: scans account settings (DNS records, SSL/TLS certs, WAF config, Access config) for misconfigurations and vulnerabilities, with on-demand and scheduled scans
- Investigate: threat-intelligence lookup for IPs, domains, hostnames, URLs, ASNs — category, hosting country, historical/passive DNS
- Infrastructure / Attack Surface Management: inventories internet-facing assets (domains, DNS records, IPs) tied to your account; manage security.txt files
- Brand Protection: domain string search with fuzzy character-distance (0-3) matching for typosquats/homoglyphs, plus AI logo-matching against uploaded brand images; monitored queries + alerts
- Security Reports: visibility into requests blocked/challenged by DDoS, WAF, and Bot Management
- Cloudforce One threat intelligence, curated indicator feeds, and open-port scanning of IP ranges
- Miscategorization reporting / categorization-change requests

**Detection signals — the lens fires on these:**
- A paid attack-surface-management or external-asset-discovery tool in the security stack (shadow-IT domain discovery)
- Threat-intel enrichment subscriptions / API keys: VirusTotal, GreyNoise, AbuseIPDB, Recorded Future calls in code or env (VT_API_KEY, ABUSEIPDB_KEY)
- A brand-protection / anti-phishing vendor (PhishLabs, ZeroFOX, BrandShield) or a homegrown newly-registered-domain + typosquat watcher
- Manual scripts that fuzz-generate lookalike domains and check WHOIS/registration
- No security.txt and no centralized view of which DNS records / certs / WAF settings are misconfigured
- Spreadsheet-tracked inventory of company domains/IPs that drifts out of date

**Ideas:**
- Run Security Insights to catch DNS/SSL/WAF/Access misconfigurations across the account instead of auditing each zone by hand
- Replace the threat-intel enrichment subscription with the Investigate / Intel APIs for IP/domain/ASN reputation and passive DNS lookups in your SOC pipeline
- Set up Brand Protection string + logo monitored queries to catch typosquatting and phishing lookalikes, retiring a separate brand-protection vendor

**Pairs with:** cloudflare-waf, cloudflare-dmarc-management, cloudflare-client-side-security

**Pricing:** Security Center is available to customers on all plans; Security Insights scan frequency scales by plan (every 7 days Free/Pro/Business, every ~3 days/daily for Enterprise) with on-demand scans on all plans. Brand Protection string monitoring + alerts is Professional+; logo-matching and advanced threat-intel / Cloudforce One / indicator feeds skew Enterprise. (verify - drifts)

**Limits:**
- Security Insights only scans assets/config inside your Cloudflare account — not infrastructure you don't run through Cloudflare
- Logo-match Brand Protection and the deeper Cloudforce One threat-intel + indicator feeds are Enterprise-tier
- Brand Protection detects lookalike/impersonation domains and alerts; takedown actions are a separate manual/Enterprise workflow
- Intel API usage is rate-limited (see intel-apis/limits)

**Notes:** Breadth over depth: it's three loosely-related capabilities (posture scanning, threat-intel lookup, brand protection) under one roof, with real value gated to Professional+/Enterprise. Overview, get-started, and brand-protection pages verified this run; the get-started page didn't enumerate every scanned config category. Strongest for teams already centralizing on Cloudflare who pay separately for ASM, threat-intel, or brand monitoring.

**Docs:** https://developers.cloudflare.com/security-center/llms.txt, https://developers.cloudflare.com/security-center/index.md, https://developers.cloudflare.com/security-center/brand-protection/index.md, https://developers.cloudflare.com/security-center/get-started/index.md

---

## Cloudflare Turnstile
`turnstile` · Bot management / CAPTCHA · confidence: `high` · lock-in: `portable`

**Is:** A CAPTCHA-free, privacy-preserving way to verify a visitor is human, using invisible JavaScript challenges instead of image puzzles, with a server-side siteverify API to confirm tokens.

**Replaces:** Google reCAPTCHA / hCaptcha (and the DIY honeypot-field + rate-limit bot-defense a team bolts onto signup, login, and contact forms)

**Use it via:** Client: <script src="https://challenges.cloudflare.com/turnstile/v0/api.js"> plus <div class="cf-turnstile" data-sitekey="..."> (implicit) or turnstile.render('#el', {sitekey, callback}) (explicit). Token arrives in callback / hidden input named cf-turnstile-response. Server: POST https://challenges.cloudflare.com/turnstile/v0/siteverify with form/JSON body {secret, response, remoteip?, idempotency_key?} -> {success, challenge_ts, hostname, error-codes[], action, cdata}. Widget CRUD via Cloudflare REST API (Account Turnstile Widgets endpoints). No Worker binding required.

**Capabilities:**
- Three widget modes: Managed (risk-adaptive, auto-picks checkbox vs non-interactive), Non-interactive (spinner, no input), and Invisible (no visible widget)
- Non-interactive challenges under the hood: proof-of-work, proof-of-space, web-API probing, browser-quirk and human-behavior detection — no image puzzles
- Server-side token validation via the siteverify API (single-use tokens, 300s lifetime, idempotency_key for safe retries)
- Works anywhere on your site without requiring Cloudflare CDN/proxy in front of it
- Pre-clearance cookies for SPAs so a single solve clears subsequent requests
- Widget sizes (normal, flexible, compact); custom action and cdata passthrough echoed back in the verify response
- WCAG 2.2 AA accessible; Enterprise adds ephemeral IDs (device fingerprint), off-label branding removal, 30-day analytics

**Detection signals — the lens fires on these:**
- npm: react-google-recaptcha, react-google-recaptcha-v3, @hcaptcha/react-hcaptcha, recaptcha (any reCAPTCHA/hCaptcha SDK)
- Script tags loading www.google.com/recaptcha/api.js or js.hcaptcha.com/1/api.js
- Env vars: RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY, RECAPTCHA_SECRET, HCAPTCHA_SECRET, NEXT_PUBLIC_RECAPTCHA_SITE_KEY
- Server calls to https://www.google.com/recaptcha/api/siteverify or hcaptcha.com/siteverify, and reading g-recaptcha-response / h-captcha-response from form bodies
- Hand-rolled bot defense on auth/forms: hidden honeypot input fields, time-to-submit heuristics, IP rate-limiters, or custom 'are you human' math/text challenges
- grep for 'g-recaptcha', 'h-captcha', 'data-sitekey', 'grecaptcha.execute' in templates/JSX

**Ideas:**
- Drop Turnstile on signup, login, password-reset, and contact/comment forms to stop credential-stuffing and spam without showing users image puzzles
- Protect a public API or coupon/checkout endpoint by requiring a Turnstile token (Invisible mode) and verifying it in a Worker or backend before processing
- Use Managed mode with pre-clearance in a React/SPA so a single human verification clears subsequent navigations instead of re-challenging every action

**Pairs with:** Cloudflare Workers (verify the token at the edge in front of your origin/API), Cloudflare WAF / Bot Management (defense in depth beyond form-level human checks), Cloudflare Pages / any framework — Turnstile is origin-agnostic and does not require the CF proxy

**Pricing:** Free plan: up to 20 widgets, 10 hostnames/widget, unlimited verification/challenge requests, 7-day analytics. Enterprise: unlimited widgets, up to 200 hostnames/widget (or any-hostname widgets), ephemeral IDs, 30-day analytics, off-label branding — contact sales. No documented per-request fee. (verify — drifts)

**Limits:**
- Token lifetime is 300 seconds (5 min) and single-use; re-validating returns error-code timeout-or-duplicate
- Token max length 2048 chars
- Free plan capped at 20 widgets and 10 hostnames per widget; higher needs require Enterprise/account team
- ephemeral_id (device fingerprint in verify metadata) is Enterprise-only
- siteverify is the only authority on validity — you MUST call it server-side; the client callback token alone is not trustworthy

**Notes:** Strong drop-in replacement for reCAPTCHA/hCaptcha and a clear upgrade over DIY honeypot+rate-limit form defense. Honest caveats: (1) it verifies humanness on specific actions/forms, NOT general API authorization or per-user authentication — do not use it as an authz layer. (2) It is a bot/abuse-friction tool, not a full bot-management/WAF product; high-value endpoints still want Bot Management. (3) Lock-in is light (swap the script + siteverify call), but the siteverify endpoint is a Cloudflare-hosted dependency in your request path. (4) Pricing/limits beyond the free tier (volume, any-per-verification charge at scale) were not fully specified in fetched docs — Enterprise is sales-gated, so verify before assuming truly unlimited at very high volume.

**Docs:** https://developers.cloudflare.com/turnstile/llms.txt, https://developers.cloudflare.com/turnstile/index.md, https://developers.cloudflare.com/turnstile/get-started/server-side-validation/index.md, https://developers.cloudflare.com/turnstile/plans/index.md, https://developers.cloudflare.com/turnstile/concepts/widget/index.md, https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/index.md

---

## Cloudflare WAF (Web Application Firewall)
`cloudflare-waf` · Security / Application Firewall · confidence: `high` · lock-in: `portable`

**Is:** An edge web application firewall that runs managed signature rulesets (Cloudflare Managed + OWASP Core), custom rule expressions, and rate limiting against inbound HTTP traffic before it reaches your origin.

**Replaces:** A self-hosted ModSecurity/Coraza + OWASP CRS stack (or an AWS WAF / Imperva / Akamai subscription) plus the nginx/Lua rate-limiting and IP-blocklist glue you'd otherwise maintain in front of your app.

**Use it via:** Ruleset Engine REST API: POST/PUT /zones/{zone_id}/rulesets with phases http_request_firewall_custom, http_request_rate_limit, http_request_firewall_managed. Detections surface as fields in custom-rule expressions (cf.waf.score, cf.waf.credential_check.*). Configurable via dashboard, API, or the cloudflare Terraform provider (cloudflare_ruleset).

**Capabilities:**
- Cloudflare Managed Ruleset: signature rules for top-10 / zero-day exploits, updated by Cloudflare's security team
- OWASP Core Ruleset: cumulative threat-scoring model with configurable threshold (paid plans)
- Free Managed Ruleset for high-impact, widely-exploited CVEs on ALL plans
- Custom rules: block/challenge/skip/log on Rules-language expressions (path, headers, geo, ASN, etc.)
- Rate limiting rules: counting by IP / IP+NAT / ASN / country / JA3-JA4 / custom expression, period + requests threshold + mitigation timeout
- Traffic detections that only SCORE (don't act): WAF attack score (1-99), leaked-credentials detection, malicious-uploads scanning, threat intelligence, AI Security for Apps
- IP Access rules, Lists, Zone Lockdown, Browser Integrity Check, exceptions/overrides on managed rules
- Deterministic execution order: IP Access -> custom rules -> rate limiting -> managed rules; first terminating action wins

**Detection signals — the lens fires on these:**
- A WAF container/sidecar in the repo: modsecurity, libmodsecurity, coraza, owasp-modsecurity-crs, naxsi in nginx.conf / Dockerfile
- Hand-rolled rate limiting: express-rate-limit, rack-attack, django-ratelimit, a Redis INCR-per-IP counter, nginx limit_req_zone
- Manual IP blocklists/allowlists in app middleware or an ipset/iptables script
- Regex-based SQLi/XSS request filters living in application middleware
- Credential-stuffing mitigation built by hand (checking submitted passwords against HaveIBeenPwned)
- aws-waf / @aws-sdk/client-wafv2, terraform aws_wafv2_* resources (paying a competitor)
- Custom 'block this user agent / country' logic scattered through route handlers

**Ideas:**
- Replace the app's express-rate-limit + Redis counter with a Cloudflare rate limiting rule keyed on IP+path so the throttle happens at the edge and never touches origin
- Move the hand-maintained SQLi/XSS request-filtering middleware behind the Cloudflare Managed Ruleset and delete the in-app regex filters
- Wire WAF leaked-credentials detection into a custom rule on the /login endpoint instead of calling a breach API per request

**Pairs with:** cloudflare-bots, cloudflare-ddos-protection, cloudflare-api-shield, cloudflare-challenges

**Pricing:** Free plan gets the Free Managed Ruleset + 1 rate-limiting rule (IP-only, 10s period) + custom rules. Cloudflare Managed Ruleset, OWASP Core Ruleset and Exposed Credentials Check unlock on Pro/Business/Enterprise; Sensitive Data Detection is Enterprise-only. Rate-limiting rule count and counting options scale by plan (Free 1 -> Enterprise 100). Billed as part of the zone plan, not per-request. (verify - drifts)

**Limits:**
- Detections only score traffic; you MUST author a custom/rate-limiting rule to actually block or challenge
- Rate-limiting counting characteristics are gated by plan (advanced keys like body fields and custom expressions are Business/Enterprise)
- Throttle (vs hard block) action on rate limiting is Enterprise-only
- OWASP Core Ruleset and full Cloudflare Managed Ruleset require paid plans

**Notes:** Only protects traffic proxied through Cloudflare (orange-cloud / Cloudflare in front of origin) - a Worker or origin reached directly bypasses it. The managed rulesets are a black box you tune via overrides/exceptions rather than edit. Verified plan-gating from the managed-rules and rate-limiting pages this run.

**Docs:** https://developers.cloudflare.com/waf/llms.txt, https://developers.cloudflare.com/waf/concepts/index.md, https://developers.cloudflare.com/waf/managed-rules/index.md, https://developers.cloudflare.com/waf/rate-limiting-rules/index.md

---

## Key Transparency
`cloudflare-key-transparency` · Security / E2EE Verification · confidence: `high` · lock-in: `portable`

**Is:** A Cloudflare-run auditor and API for append-only key-transparency logs, so anyone can verify that the public keys an E2EE messaging system hands out are consistent and not silently swapped — the auditing model behind WhatsApp-style key transparency.

**Replaces:** Building and operating your own transparency-log auditor (signed checkpoints, epoch consistency proofs, AKD verification) to back an E2EE app's 'we don't MITM your keys' claim; trusting your own key directory with no external witness.

**Use it via:** REST, no auth for reads: GET https://plexi.key-transparency.cloudflare.com/info returns {keys:[{public_key, not_before}], logs:[<log_id>]}. Plus epoch endpoints (digests/proofs) and namespace endpoints (create/manage monitored logs). Verify locally with the Plexi CLI.

**Capabilities:**
- Audits append-only Logs (Certificate-Transparency-style) used for E2EE public-key distribution
- Auditor signs epoch info: receipt time, epoch number, and epoch digest, and checks publication constraints
- Public API to fetch auditor public keys (with not_before for rotation) and the set of audited log IDs
- Epoch endpoints expose digests, audit proofs, and publication constraints; namespace endpoints manage monitored logs
- Built on AKD (auditable key directory) proofs, verifiable asynchronously
- Local verification via the Plexi tool so you don't have to trust Cloudflare's word
- Hosted under plexi.key-transparency.cloudflare.com

**Detection signals — the lens fires on these:**
- An E2EE or secure-messaging codebase with a key directory / key server and no external auditing
- Custom Merkle-tree / append-only log or signed-checkpoint code for key history
- Signal-protocol / libsignal, MLS, or 'safety number' / key-fingerprint verification flows
- Roll-your-own Certificate-Transparency-like consistency proofs
- AKD / 'auditable key directory' / 'key transparency' references
- Manual out-of-band key-fingerprint comparison as the only MITM defense

**Ideas:**
- Back an E2EE messaging app's key directory with a Cloudflare-audited transparency log so users get cryptographic (not just trust-based) assurance against key substitution.
- Run the Plexi tool in CI / a monitor to continuously verify epoch consistency of a log you depend on.
- Expose key-transparency proofs to security-conscious users as a verifiable 'no silent key swap' guarantee.

**Pairs with:** Plexi (open-source auditor/CLI), AKD libraries, messaging stacks using key transparency (e.g. WhatsApp-style)

**Pricing:** Public auditor API appears free / open for reads; no pricing stated (verify — drifts).

**Limits:**
- Niche — only relevant if you actually run an E2EE key-distribution system
- It audits/witnesses logs; it is not a turnkey 'add E2EE to my app' product — you still build the messaging + key directory
- WhatsApp is cited as an example of the approach, not necessarily this exact hosted endpoint
- Threat model assumes clients/monitors actually check proofs

**Notes:** The /info endpoint shape, the keys/logs response, what the auditor signs (receipt time + epoch number + epoch digest), AKD basis, the Plexi tool, and the append-only-log/Certificate-Transparency model are verified. The auditor-information page fetched did not itself describe the Plexi CLI's commands (that is on the monitor-the-auditor page, not fetched) — Plexi's existence is confirmed but its exact CLI usage is unverified. WhatsApp is named as an example of the technique; do not assert this specific Cloudflare service powers it. Very narrow audience.

**Docs:** https://developers.cloudflare.com/key-transparency/llms.txt, https://developers.cloudflare.com/key-transparency/index.md, https://developers.cloudflare.com/key-transparency/api/auditor-information/index.md

---

## Magic Transit
`magic-transit` · Network / DDoS Protection (L3/L4) · confidence: `high` · lock-in: `portable`

**Is:** Routes your entire network's IP traffic (whole subnets) through Cloudflare's edge over BGP + anycast GRE/IPsec tunnels, scrubbing L3/L4 DDoS close to the source and delivering clean traffic back to your infrastructure.

**Replaces:** On-prem DDoS scrubbing appliances (Arbor/NETSCOUT, Radware) plus a scrubbing-center contract (Akamai Prolexic, Imperva, Neustar/Vercara) and the GRE/cross-connect plumbing to reach them.

**Use it via:** REST under /accounts/{account_id}/magic. Tunnels: POST /accounts/{id}/magic/gre_tunnels; POST/PUT /accounts/{id}/magic/ipsec_tunnels (+ /{tunnel_id}/psk_generate); routes under /magic/routes. Prefix advertisement via Addressing API (/accounts/{id}/addressing/prefixes/{id}/bgp/...). Requires 'Magic Transit Write' (or 'Magic WAN Write') token scope. Analytics via GraphQL datasets magicTransitTunnelHealthChecksAdaptiveGroups and magicTransitTunnelTrafficAdaptiveGroups.

**Capabilities:**
- Always-on L3/L4 DDoS mitigation for entire IP ranges (not just HTTP) ingested at Cloudflare's anycast edge
- On-ramp via BGP advertisement of your /24, traffic to you over GRE or IPsec anycast tunnels (clean return path)
- Magic Transit on-demand: keep prefixes off Cloudflare normally, activate advertisement/mitigation during an attack
- Traffic steering across tunnels by priority; static routes or BGP peering (beta) to the Magic VNet routing table
- Tunnel + endpoint health checks, health alerts, Network Analytics, packet captures, traceroutes
- Anti-replay handling and MTU/MSS guidance for anycast IPsec
- Pairs with BYOIP (your IPs) or Cloudflare-leased IPs; connect over the Internet or via Network Interconnect (CNI)
- Kentik integration for network observability / attack detection

**Detection signals — the lens fires on these:**
- On-prem or colo network with public IP ranges to protect that aren't just a web app behind a CNAME (game servers, VoIP, DNS auth, APIs, mail, raw TCP/UDP)
- Existing DDoS scrubbing vendor contract: Prolexic, Imperva, Neustar/Vercara, Radware, NETSCOUT Arbor
- GRE / IPsec tunnel configs to a scrubbing provider; BGP sessions announcing /24s to upstreams
- Hardware appliances (Arbor TMS, F5, Radware DefensePro) in network diagrams
- Hardcoded server IPs that must stay reachable at L3 (can't be hidden behind a reverse proxy)
- Need to protect UDP services that an HTTP CDN/WAF can't front

**Ideas:**
- Replace a scrubbing-appliance + Prolexic-style contract by advertising your /24 through Magic Transit with always-on L3/L4 mitigation
- Set up Magic Transit on-demand so prefixes only route through Cloudflare during an active volumetric attack
- Protect non-HTTP infrastructure (DNS, game/VoIP UDP, raw TCP APIs) that can't sit behind a normal CDN/WAF

**Pairs with:** byoip, network-interconnect, network-flow, magic-wan, spectrum

**Pricing:** Enterprise-only; pricing is contract/account-team negotiated (typically committed clean-traffic bandwidth). No public self-serve tier. (verify — drifts)

**Limits:**
- Enterprise-only
- BGP on-ramp generally requires a /24 minimum prefix; smaller deployments must use Cloudflare-owned IPs
- L3/L4 (whole-subnet) product — for app-layer/HTTP-only protection the CDN+WAF or Spectrum is the right tool instead
- Operationally heavy: BGP, tunnels, MTU/MSS tuning, health checks; BGP peering on-ramp is beta
- IPv6 support is beta

**Notes:** This is the heavyweight: it moves your whole network's L3 traffic, not a single app. Don't suggest it when the workload is just a website/API that can live behind the proxy (use CDN+WAF) or when only specific TCP/UDP ports need fronting (use Spectrum). Lock-in is real at the routing layer (BGP + tunnels + possibly BYOIP). Concrete clean-traffic pricing units and exact minimum-commit were not on the fetched pages — verify with account team.

**Docs:** https://developers.cloudflare.com/magic-transit/llms.txt, https://developers.cloudflare.com/magic-transit/index.md, https://developers.cloudflare.com/magic-transit/how-to/configure-tunnels/index.md, https://developers.cloudflare.com/magic-transit/how-to/advertise-prefixes/index.md, https://developers.cloudflare.com/changelog/product/magic-transit/

---
