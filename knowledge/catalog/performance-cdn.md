# Performance & CDN

_10 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Argo Smart Routing
`cloudflare-argo-smart-routing` · Performance & CDN · confidence: `high` · lock-in: `portable`

**Is:** Routes your traffic across Cloudflare's private backbone over the least-congested path in real time, instead of letting requests take the default (often congested) public-internet route to your origin.

**Replaces:** Paying for premium transit / a private backbone or accepting default BGP routing and slow cross-continent origin fetches; a poor-man's substitute for buying your own MPLS/global accelerator.

**Use it via:** Per-zone toggle: PATCH /zones/{zone_id}/argo/smart_routing with {"value":"on"}; also surfaced under the Smart Shield bundle. Enabled in dashboard under Argo Smart Routing (Traffic).

**Capabilities:**
- Real-time detection of network congestion and rerouting over Cloudflare's backbone
- Optimizes the Cloudflare-edge-to-origin leg, biggest win for users far from the origin
- Cuts origin response latency and improves reliability on cache misses and dynamic/uncacheable traffic
- Argo for Packets extends smart routing to Spectrum/Magic Transit packet flows
- Analytics showing latency improvement vs. unoptimized routing
- Mitigated attack traffic is excluded from billed bandwidth

**Detection signals — the lens fires on these:**
- Origin in a single region (one AWS/GCP region, one data center) serving a geographically global audience
- Lots of dynamic / uncacheable traffic (APIs, authenticated dashboards, checkout) where CDN caching can't help latency
- Complaints about slow TTFB for far-away users despite a CDN being in place
- Hand-rolled multi-region origin replication done purely to cut latency (could be partially offset by smarter routing)
- Already proxying through Cloudflare but not using the backbone

**Ideas:**
- Turn on Argo for an API/dynamic-heavy zone where caching gives no latency benefit but cross-continent RTT is the bottleneck
- Use Argo analytics to quantify the latency win before committing to a costly second origin region
- Pair Argo with Tiered Cache so both cache-miss fetches and dynamic requests ride the optimized backbone

**Pairs with:** cloudflare-cache-cdn, cloudflare-smart-shield, cloudflare-load-balancing

**Pricing:** Paid add-on, usage-based per domain: USD $5.00/month base + $0.10/GB after the first GB of traffic between Cloudflare and visitors (verify - drifts). Billed bandwidth excludes mitigated attack traffic.

**Limits:**
- Usage-based bandwidth billing can surprise on high-traffic zones - Cloudflare recommends usage notifications
- Optimizes routing only; does not cache or reduce request volume by itself
- Benefit is marginal for users already close to the origin

**Notes:** Now also packaged inside the Smart Shield bundle. Because it's priced per-GB of traffic (not just cache misses), a high-volume site can see meaningful monthly cost - model it against the latency gain. It is NOT the right tool if your traffic is cache-heavy/static (the CDN already serves it) or your audience is co-located with your origin.

**Docs:** https://developers.cloudflare.com/argo-smart-routing/index.md, https://developers.cloudflare.com/argo-smart-routing/get-started/index.md

---

## Automatic Platform Optimization (APO)
`cloudflare-automatic-platform-optimization` · Performance & CDN · confidence: `high` · lock-in: `portable`

**Is:** Serves your entire WordPress site (including the HTML) from Cloudflare's edge cache via Workers, so dynamic pages get a CDN-fast TTFB without a caching plugin or a faster host.

**Replaces:** A WordPress page-cache plugin (WP Rocket / W3 Total Cache / LiteSpeed Cache) and/or paying up for managed WordPress hosting just to fix TTFB.

**Use it via:** Enabled via the official Cloudflare WordPress plugin (v3.8.2+) plus a per-zone APO toggle; requires Cloudflare Full Setup (Cloudflare nameservers). Largely plugin/dashboard-driven rather than a code SDK.

**Capabilities:**
- Caches dynamic HTML at the edge (not just static assets) and serves the whole site from cache
- Uses Cloudflare Workers to intelligently serve/refresh cached pages and auto-purge on content changes
- Caches third-party scripts to cut requests leaving the edge
- Device-type aware caching (separate mobile/desktop variants) and query-parameter handling
- Integrates with the official Cloudflare WordPress plugin for cache invalidation on edits
- Page Rules integration and subdomain/subdirectory support

**Detection signals — the lens fires on these:**
- A WordPress codebase (wp-content/, wp-config.php) - the single strongest signal
- A page-cache plugin in the plugin list (wp-rocket, w3-total-cache, litespeed-cache, wp-super-cache)
- Complaints about slow WordPress TTFB / origin PHP render time
- WooCommerce or other dynamic WP where a static-only CDN isn't enough
- Already on Cloudflare but only caching static assets, leaving HTML to hit the origin

**Ideas:**
- Retire a heavyweight page-cache plugin and let APO cache HTML at the edge instead, eliminating origin PHP renders for anonymous traffic
- Use APO to make a cheap shared-WordPress host feel like managed hosting by moving TTFB to the edge
- Enable device-type caching so mobile and desktop variants are both edge-served correctly

**Pairs with:** cloudflare-cache-cdn, cloudflare-speed-observatory

**Pricing:** Cloudflare Free plan + $5/month APO add-on, OR included free with Pro and Business plans. WordPress.com sites need a Business plan or above (to install plugins) (verify - drifts).

**Limits:**
- Requires Cloudflare Full Setup (Cloudflare-managed nameservers); partial/CNAME setup not supported
- Built and tuned for WordPress - not a general-purpose dynamic-HTML edge cache for arbitrary apps
- Logged-in / personalized WordPress traffic bypasses the cache; the win is for anonymous visitors
- Needs the official Cloudflare WP plugin for correct auto-purge on content updates

**Notes:** WordPress-specific by design - if the stack isn't WordPress, the right tool is generic Cache Rules (or Workers + Cache API), not APO. Edge-cached HTML means you must trust APO's invalidation (plugin-driven) to avoid serving stale pages after edits; bespoke/non-standard plugins can interfere. Verify plugin compatibility for sites with complex membership/cart logic.

**Docs:** https://developers.cloudflare.com/automatic-platform-optimization/index.md, https://developers.cloudflare.com/automatic-platform-optimization/about/index.md, https://developers.cloudflare.com/support/third-party-software/content-management-system-cms/wordpresscom-and-cloudflare/

---

## Cloudflare Cache / CDN
`cloudflare-cache-cdn` · Performance & CDN · confidence: `high` · lock-in: `portable`

**Is:** A global edge CDN that caches your content across Cloudflare's network so requests are served from the nearest data center instead of hitting your origin every time.

**Replaces:** A third-party CDN vendor (Fastly/Akamai/CloudFront) plus the egress bills you pay your origin host/S3 for every uncached request.

**Use it via:** Cache Rules via Rulesets API (phase http_request_cache_settings) or cloudflare_ruleset Terraform resource; purge via POST /zones/{zone_id}/purge_cache; Cache Reserve toggled per-zone in dashboard. Requires DNS records proxied (orange-cloud) through Cloudflare.

**Capabilities:**
- Default caching of common static file types with zero config
- Cache Rules: per-URL control over cache eligibility, edge TTL, browser TTL, and cache key (dashboard, API, Terraform)
- Cache Reserve: persistent R2-backed upper-tier cache (30-day default retention) that shields origin from egress
- Tiered Cache (regional + smart) to reduce origin fetches by funneling misses through upper-tier data centers
- Instant purge (by URL, tag, hostname, or everything)
- Cache Analytics: hit ratio, bandwidth saved, requests served from edge
- Respects origin Cache-Control and the independent CDN-Cache-Control header

**Detection signals — the lens fires on these:**
- CloudFront / Fastly / Akamai config in the repo (CloudFront distribution in Terraform/CDK, fastly.toml, VCL files)
- High S3/GCS egress or origin bandwidth bills; a CDN_URL or ASSET_HOST env var pointing at a cloud bucket
- Hand-rolled Cache-Control header middleware and a homegrown cache-busting/asset-fingerprinting step paired with manual invalidation calls
- nginx proxy_cache / Varnish (varnish.vcl, default.vcl) running as a self-managed caching layer
- Static assets (images, JS, CSS, fonts) served directly from app servers or an origin bucket with no edge layer

**Ideas:**
- Move static asset and bucket delivery behind Cloudflare so origin egress drops to near zero, then enable Cache Reserve to keep long-tail objects out of the origin entirely
- Replace a self-managed Varnish/nginx-cache tier with Cache Rules + Tiered Cache for the same hit-ratio without running the box
- Add cache-tag headers to API/CMS responses so you can purge-by-tag on publish instead of blasting a full cache flush

**Pairs with:** cloudflare-argo-smart-routing, cloudflare-smart-shield, cloudflare-automatic-platform-optimization, cloudflare-speed-observatory

**Pricing:** Core CDN/cache available on all plans including Free. Cache Rules limit scales by plan (10 Free to 300 Enterprise). Cache Reserve is usage-based on a paid plan: storage $0.015/GB-month, Class A ops (writes) $4.50/million, Class B ops (reads) $0.36/million (verify - drifts).

**Limits:**
- Cache Rules require proxied (orange-cloud) DNS; grey-cloud/DNS-only records are not cached
- Cache Reserve eligibility: cacheable, >=10h freshness TTL, Content-Length present, not an image-transformation variant
- Default uncacheable content (no-cache/no-store, query-string-varied dynamic responses) needs explicit Cache Rules to override
- Cache Reserve requires a paid plan

**Notes:** Going all-in means proxying DNS through Cloudflare (some lock-in to the orange-cloud model). Cache Reserve is backed by R2 so it avoids egress fees, but you now pay R2-style storage+operations - for a small/low-traffic site the ops charges can exceed the egress you saved, so it's a high-traffic / large-catalog play. Not a substitute for an application data store; it's an HTTP response cache.

**Docs:** https://developers.cloudflare.com/cache/index.md, https://developers.cloudflare.com/cache/advanced-configuration/cache-reserve/index.md, https://developers.cloudflare.com/cache/how-to/cache-rules/index.md

---

## Cloudflare China Network
`cloudflare-china-network` · Networking / Regional Delivery · confidence: `high` · lock-in: `portable`

**Is:** Runs Cloudflare's CDN, WAF, DDoS, bot management and in-China authoritative DNS from JD Cloud data centers inside mainland China for low-latency, compliant delivery to Chinese users.

**Replaces:** Standing up a separate China stack — a licensed China CDN/cloud (Alibaba Cloud, Tencent Cloud) plus a second WAF and a parallel ops pipeline — to serve users behind the Great Firewall.

**Use it via:** Not a code binding — it is an Enterprise account capability. Provisioned via a Cloudflare sales contract (China Network package + China Service Supplemental Terms); domains are then onboarded to the same zone config/API. JD Cloud vetting of content/ICP precedes activation. In-China infrastructure (IP ranges, API endpoints) is documented under china-network/reference.

**Capabilities:**
- Serves cached content and security services from data centers inside mainland China (operated by partner JD Cloud) covering most populated regions
- In-China authoritative DNS and nameservers to cut Time to First Byte for local users
- Same global Cloudflare dashboard and config experience across China and the rest of the world
- WAF, DDoS protection, and bot management available in-region
- Automatically enables IPv6 (mandatory for internet-facing services in mainland China)
- Local-language support and premium service options

**Detection signals — the lens fires on these:**
- A separate Alibaba Cloud / Tencent Cloud / Baidu Cloud CDN account or SDK kept only to serve China
- Geo-split delivery logic that routes cn / China users to a different origin or CDN hostname
- An ICP number / ICP filing already displayed in the site footer (signals China operations and eligibility)
- Duplicate WAF/CDN configs maintained in parallel for a China property
- Latency complaints or blocked assets specifically from mainland-China users

**Ideas:**
- Consolidate a separate Alibaba/Tencent China CDN onto Cloudflare China Network so one dashboard and ruleset covers global + China
- Use in-China authoritative DNS to cut TTFB for mainland users on an existing Enterprise zone
- Plan an ICP-filing + China onboarding path for a product expanding into mainland China

**Pairs with:** cloudflare-dns, cloudflare-ssl-tls

**Pricing:** Enterprise-only, sold as a separate China Network package on top of an Enterprise contract (custom/sales-quoted). Government ICP registration itself is free though providers may charge processing fees. (verify — drifts)

**Limits:**
- Requires a Cloudflare Enterprise plan plus a separate China Network subscription and signing the China Service Supplemental Terms
- Every apex domain must have an ICP filing (Bei'an, ~1-2 months) or, for commercial sites, an ICP license (ICP Zheng, ~2-3 months); ICP number must be shown in the footer
- Content must pass JD Cloud vetting (company details, domain, ICP, content description, signed self-attestation); onboarding takes ~24-48h after approval
- Not all global Cloudflare products are available in-region (supported-products list is a separate reference page not fetched this run)
- Hard regulatory dependency — no ICP, no China Network

**Notes:** This is a compliance/regional product, not something a dev self-serves. The ICP requirement (and JD Cloud vetting) is the real gate and can take months; eligibility for a commercial ICP license is restricted (joint ventures with <50% foreign ownership, local companies). Lock-in is to an Enterprise contract. The exact list of in-China supported products was referenced but not deeply fetched.

**Docs:** https://developers.cloudflare.com/china-network/llms.txt, https://developers.cloudflare.com/china-network/index.md, https://developers.cloudflare.com/china-network/get-started/index.md, https://developers.cloudflare.com/china-network/concepts/icp/index.md

---

## Cloudflare Load Balancing
`cloudflare-load-balancing` · Reliability & Monitoring · confidence: `high` · lock-in: `portable`

**Is:** DNS/anycast-level load balancing that spreads traffic across pools of origin endpoints, health-checks them from multiple regions, and fails over or geo-steers automatically.

**Replaces:** A self-managed NGINX/HAProxy LB pair plus a hand-rolled failover script, or AWS ELB/ALB + Route 53 health-check-based failover.

**Use it via:** REST under /zones/{zone_id}/load_balancers, plus account-level /accounts/{account_id}/load_balancers/pools and /monitors; Terraform cloudflare_load_balancer, cloudflare_load_balancer_pool, cloudflare_load_balancer_monitor.

**Capabilities:**
- Distributes traffic across endpoints grouped into pools to cut strain and latency
- Active health monitoring at configurable intervals from multiple data centers (status codes, response text, timeouts)
- Automatic failover away from unhealthy pools/endpoints
- Steering policies: off/failover (active-passive, ordered) and random/weighted (active-active) at base tier; dynamic (latency-based), geo, proximity (GPS), and least-outstanding-requests/least-connections with the Traffic Steering add-on
- Session affinity (sticky sessions) and per-pool/per-endpoint weighting
- Custom rules to alter routing based on request attributes; supports Cloudflare Pages as an origin

**Detection signals — the lens fires on these:**
- A self-managed LB in config: nginx upstream {} blocks, haproxy.cfg, or an NGINX/HAProxy container
- AWS ELB/ALB/NLB or Route 53 failover/health-check records in Terraform/CDK
- A hand-rolled failover/DNS-flip script or keepalived/VRRP setup
- Multiple origin endpoints/regions that need traffic split or geo-routing
- A custom 'pick a healthy backend' layer in application code

**Ideas:**
- Replace an NGINX/HAProxy + keepalived failover pair with Cloudflare pools + monitors so health-checking and failover happen at the edge, not on a box you patch
- Use geo or proximity steering to route users to the nearest origin region instead of a custom GeoDNS setup
- Add weighted/random steering for a blue-green or canary origin rollout without touching DNS by hand

**Pairs with:** cloudflare-health-checks, cloudflare-argo-smart-routing, cloudflare-cache-cdn

**Pricing:** Paid add-on to any plan; Enterprise can preview as a non-metered service. Advanced steering policies (dynamic/geo/proximity/least-outstanding) require purchasing the Traffic Steering add-on; base tier gets off/failover + random only. Pricing shown in dashboard (verify - drifts).

**Limits:**
- Only off/failover and random steering are available without the Traffic Steering add-on (and to non-Enterprise without it)
- Operates at L7/DNS for HTTP(S) origins; not a substitute for in-cluster service mesh or L4 transport LB (use Spectrum/Magic Transit for raw TCP/UDP)
- Endpoints must be reachable from Cloudflare's network

**Notes:** Its built-in pool monitors overlap with standalone Health Checks - pick one per origin. The genuinely useful steering (latency/geo/proximity) is gated behind the paid Traffic Steering add-on, so the base offering is essentially failover + weighted round-robin. For purely internal/east-west balancing inside a cluster this is the wrong layer; it's an edge/global-traffic LB.

**Docs:** https://developers.cloudflare.com/load-balancing/index.md, https://developers.cloudflare.com/load-balancing/understand-basics/traffic-steering/index.md, https://developers.cloudflare.com/load-balancing/understand-basics/traffic-steering/steering-policies/standard-options/index.md

---

## Cloudflare Speed (Observatory)
`cloudflare-speed-observatory` · Performance & CDN · confidence: `high` · lock-in: `portable`

**Is:** A built-in performance suite that benchmarks your real pages (synthetic Lighthouse + real-user data / Core Web Vitals) and one-click-enables edge optimizations like Speed Brain, Rocket Loader, Cloudflare Fonts, and compression.

**Replaces:** A standalone web-perf monitoring/RUM vendor (SpeedCurve, Calibre, Datadog RUM) plus the front-end build plumbing for prefetching, font self-hosting, and JS deferral.

**Use it via:** Mostly dashboard toggles under Speed; individual features map to zone settings (e.g. POST/PATCH /zones/{zone_id}/settings/rocket_loader, .../speed_brain, .../fonts). Observatory tests run from the dashboard.

**Capabilities:**
- Observatory: runs synthetic (Lighthouse-style) and real-user tests, tracks Core Web Vitals (LCP/INP/CLS) and a test history dashboard
- Recommendations engine that suggests which Cloudflare settings/products would speed up the specific site
- Speed Brain: adds a Speculation-Rules header to prefetch the likely next navigation (improves LCP/TTFB on subsequent pages); on by default, all plans, Chromium 121+
- Rocket Loader (async/defer JS), Cloudflare Fonts (self-host Google Fonts at edge), content compression (Brotli/gzip)
- Protocol optimizations: HTTP/2, HTTP/3 over QUIC
- Image optimization hooks: Polish (lossy/lossless recompression, WebP/AVIF) and Image Resizing/Transformations

**Detection signals — the lens fires on these:**
- A paid RUM/perf-monitoring SDK or vendor in package.json (@datadog/browser-rum, web-vitals reporting to a third party, SpeedCurve/Calibre in CI)
- Hand-rolled <link rel=prefetch>/Speculation-Rules logic or a quicklink/instant.page dependency
- Self-hosting Google Fonts manually, or @fontsource packages plus font-loading CSS
- Webpack/Vite config doing manual script defer/async orchestration; a custom Brotli precompression step
- Lighthouse CI configured to chase Core Web Vitals scores

**Ideas:**
- Drop a third-party RUM agent and read Core Web Vitals straight from Observatory's real-user data instead
- Enable Speed Brain to get Speculation-Rules prefetching without shipping quicklink/instant.page
- Switch manually self-hosted Google Fonts over to Cloudflare Fonts to cut a request and a build step

**Pairs with:** cloudflare-cache-cdn, cloudflare-automatic-platform-optimization

**Pricing:** Speed suite available on all plans; Observatory and most content optimizations (Speed Brain, Rocket Loader, Fonts, compression, HTTP/2-3) included. Polish requires Pro+; Image Transformations are separately metered (verify - drifts).

**Limits:**
- Speed Brain needs cacheable pages, no Worker on the route, and a Chromium 121+ browser - no benefit on Safari/Firefox or Worker-rendered routes
- Observatory is positioned as beta and is a tuning/measurement aid, not a full APM/tracing tool
- Edge optimizations operate on responses Cloudflare proxies; DNS-only records are unaffected

**Notes:** Observatory's RUM is page-load / Core-Web-Vitals focused, not a replacement for backend APM (traces, error tracking). Some optimizations (Rocket Loader, aggressive prefetch) can break fragile front-ends, so they're opt-in and need testing. Polish/Transformations overlap with Cloudflare Images - check which billing surface applies before leaning on them.

**Docs:** https://developers.cloudflare.com/speed/index.md, https://developers.cloudflare.com/speed/optimization/content/speed-brain/index.md

---

## Cloudflare Waiting Room
`cloudflare-waiting-room` · Reliability & Monitoring · confidence: `high` · lock-in: `portable`

**Is:** A virtual queue at the edge that holds excess visitors on a branded waiting page during traffic spikes and admits them at a controlled rate, so your origin never gets stampeded.

**Replaces:** A hand-built queue/throttle (Redis-backed rate limiter + a custom waiting page) or a dedicated virtual-queue SaaS like Queue-it.

**Use it via:** REST under /zones/{zone_id}/waiting_rooms (create/list/update), plus rules/events sub-resources; Terraform cloudflare_waiting_room. Placed on a host/path; requires Cloudflare CDN with proxied DNS (or a load balancer) and visitor cookies.

**Capabilities:**
- Edge-enforced virtual queue that activates automatically when configured thresholds are exceeded
- Controlled admission: caps total active users and new users per minute to match origin capacity
- Session tracking with position memory and continuously updated estimated wait times
- Queueing methods: FIFO, random, passthrough, and reject; plus a queue-all option to force everyone through
- Session duration (1-30 min) so admitted/returning users skip the queue; enterprise session renewal
- JSON response mode for native/mobile apps to build a custom waiting UI; bypass rules to exempt certain traffic; fully customizable waiting page

**Detection signals — the lens fires on these:**
- A Redis/Memcached-backed rate limiter or token-bucket gate fronting a checkout/drop/registration flow
- A custom 'you are number N in line' page or a homegrown queue service
- A Queue-it / similar virtual-waiting-room vendor integration
- Flash-sale / ticket-onsale / limited-drop / exam-registration traffic patterns in the app
- Load-shedding or 503-throttling middleware written to protect a capacity-limited origin

**Ideas:**
- Replace a Redis rate-limiter + bespoke 'in line' page with a Waiting Room on the checkout/drop path, set total active users to your tested origin ceiling
- Front a ticket on-sale or product-drop URL with FIFO queueing so early arrivals get fair ordering during the spike
- Use JSON response mode to render an in-app queue screen for a mobile client instead of the default web page

**Pairs with:** cloudflare-load-balancing, cloudflare-cache-cdn

**Pricing:** Requires Business plan or above (Enterprise can preview); also available to organizations qualified under Project Fair Shot. Configured per host/path (verify - drifts).

**Limits:**
- Total active users must be > 200; new-users-per-minute is a throughput threshold, not an exact admission count
- Requires Cloudflare CDN with proxied DNS (or a load balancer) and visitor cookies enabled
- Session renewal control is Enterprise-only
- Not on Free/Pro plans (Business minimum)

**Notes:** Business-plan floor makes it a non-starter for hobby/Free projects. It protects against legitimate-traffic surges (sales, drops, registrations), not malicious floods - that's the WAF/DDoS/Rate-Limiting domain, so don't position it as a bot/attack defense. Tuning total-active-users requires knowing your real origin capacity; set it too high and the queue won't actually protect you.

**Docs:** https://developers.cloudflare.com/waiting-room/index.md, https://developers.cloudflare.com/waiting-room/reference/configuration-settings/index.md

---

## Google Tag Gateway (for Advertisers)
`cloudflare-google-tag-gateway` · Analytics / First-Party Tag Serving · confidence: `high` · lock-in: `portable`

**Is:** A free Cloudflare feature that serves Google's measurement tags (gtag.js) first-party from your own domain and forwards measurement events through your domain to Google, recovering ad signal lost to ad blockers, ITP, and third-party-cookie restrictions.

**Replaces:** Building your own server-side GTM / first-party tagging proxy (a reverse proxy + container that rehosts gtag.js and relays hits to Google), or paying for managed sGTM hosting, just to dodge ad blockers and third-party-cookie loss.

**Use it via:** No code SDK: configure in Cloudflare dashboard Tag Management (or from the GTM console). Requires Super Administrator, Administrator, or Zaraz Admin role on the account. You provide the Google tag ID and a measurement path on your zone; Cloudflare intercepts that path and proxies gtag + events to Google. Your domain must be on Cloudflare (DNS/proxy).

**Capabilities:**
- Loads the Google tag from your domain (first-party) instead of www.googletagmanager.com
- Receives measurement events on a path on your own domain, then forwards them to Google
- Improves ad signal recovery against ad blockers, ITP/Safari, and third-party cookie deprecation
- Set up via the Google Tag Manager console (fastest) or the Cloudflare dashboard
- You supply your Google tag ID and pick an unused site path for measurement requests
- Lives in the Cloudflare dashboard's Tag Management section (alongside Zaraz)
- Gateway requests do not count toward CDN, WAF, or Bot Management usage limits

**Detection signals — the lens fires on these:**
- Script tags loading https://www.googletagmanager.com/gtag/js?id=G-XXXX or ga.js / analytics.js from Google's domains
- gtag( ) / dataLayer.push usage in the frontend
- A self-built reverse proxy or Worker that rehosts gtag.js / relays GA4 Measurement Protocol hits to dodge blockers
- Server-side GTM (sGTM) container running on Cloud Run / App Engine / a VPS
- Complaints about Safari ITP, ad-blocker signal loss, or third-party cookie deprecation hurting conversion data
- Google Ads / GA4 / Floodlight tags whose hits get blocked client-side
- Domain already proxied through Cloudflare (orange-cloud) — prerequisite is already met

**Ideas:**
- Replace a hand-built gtag.js reverse proxy / sGTM box with Google Tag Gateway to serve Google tags first-party for free without running a container.
- Recover GA4 / Google Ads conversion signal lost to ad blockers and ITP by moving measurement onto a first-party path.
- For a site already on Cloudflare, flip on Tag Gateway from Tag Management instead of standing up server-side tagging infrastructure.

**Pairs with:** Zaraz (same Tag Management section), Cloudflare CDN/DNS (prerequisite), Google Analytics 4 / Google Ads / GTM

**Pricing:** Free to use; gateway requests do not count toward CDN, WAF, or Bot Management limits (verify — drifts).

**Limits:**
- Requires your domain to use Cloudflare as DNS/proxy — not usable if you are not on Cloudflare
- Scoped to Google measurement tags (GA4/Ads/GTM); not a general first-party proxy for arbitrary third-party scripts (that is closer to Zaraz)
- Does not bypass consent requirements — first-party serving is not a substitute for lawful-basis/consent
- Setup needs a Super Admin / Admin / Zaraz Admin role

**Notes:** Free pricing, the 'load tag from your domain + forward events to Google' mechanism, GTM-console vs dashboard setup, the required roles, the 'must be on Cloudflare' prerequisite, and 'requests don't count toward CDN/WAF/Bot limits' are all verified from the overview page. Only the index + overview were available in the index listing, so deeper how-it-works detail and any per-product nuances (Floodlight/Ads specifics) are inferred and worth re-checking. It sits in Tag Management next to Zaraz but is a distinct, Google-specific feature — don't conflate with Zaraz's general third-party tag loading.

**Docs:** https://developers.cloudflare.com/google-tag-gateway/llms.txt, https://developers.cloudflare.com/google-tag-gateway/index.md

---

## Health Checks (standalone)
`cloudflare-health-checks` · Reliability & Monitoring · confidence: `high` · lock-in: `portable`

**Is:** Edge-run probes that monitor whether your origin/endpoint is up - checking status codes, response body, paths and protocols from multiple Cloudflare data centers - and alert you in near real time when it goes down.

**Replaces:** A self-hosted uptime monitor (a cron + curl + PagerDuty glue, Uptime Kuma) or a paid uptime SaaS (Pingdom, UptimeRobot, StatusCake).

**Use it via:** REST: /zones/{zone_id}/healthchecks (create/list/update); Terraform cloudflare_healthcheck resource. Configured in dashboard under Health Checks. Notifications wired via Cloudflare Notifications.

**Capabilities:**
- Probes origin availability from Cloudflare's global edge at configurable intervals and from multiple regions
- Checks expected response codes, response body text, paths, timeouts, and protocol type
- Near-real-time notifications when an origin fails or recovers
- Health Checks Analytics: origin uptime, latency, failure reason, and per-event logs for debugging
- Region selection to control where probes originate
- Works for a single origin with no load balancer required

**Detection signals — the lens fires on these:**
- A homegrown uptime cron (curl/wget in a scheduled job) posting to Slack/PagerDuty on failure
- An Uptime Kuma / statping container, or a Pingdom/UptimeRobot/StatusCake account
- A single origin with no existing external availability monitoring
- Custom synthetic-check scripts hitting a /health or /healthz endpoint on a timer
- Endpoint already fronted by Cloudflare but monitored only from one external location

**Ideas:**
- Replace a cron+curl uptime script (and its alert plumbing) with a Health Check that probes from many regions and fires Cloudflare Notifications
- Use Health Checks Analytics to get multi-region latency + failure-reason history without standing up a monitoring stack
- Monitor a standalone origin that has no load balancer, then graduate to Load Balancing pools later reusing the same check concept

**Pairs with:** cloudflare-load-balancing, cloudflare-smart-shield

**Pricing:** Not on Free. Pro/Business/Enterprise include 10 / 50 / 1,000 checks respectively; Analytics on Pro and above (verify - drifts).

**Limits:**
- Standalone Health Checks are distinct from Load Balancing health monitors (different feature; monitors live on LB pools)
- Not available on the Free plan
- Check count capped per plan tier
- Monitors reachability/response, not full transaction correctness or deep APM

**Notes:** If you're already running Load Balancing, use its built-in pool monitors instead of standalone Health Checks - they overlap. Standalone Health Checks observe availability and notify; they don't take action on their own (no automatic failover - that's Load Balancing's job). Protocol support beyond HTTP/HTTPS (e.g. TCP) was not confirmed on the pages fetched this run.

**Docs:** https://developers.cloudflare.com/health-checks/index.md, https://developers.cloudflare.com/health-checks/llms.txt

---

## Smart Shield
`cloudflare-smart-shield` · Performance & CDN · confidence: `high` · lock-in: `portable`

**Is:** A bundled origin-protection layer that groups Cloudflare's request- and connection-reduction features (Smart Tiered Cache, connection reuse, Health Checks, Cache Reserve, Argo, dedicated egress IPs) under one offering to cut load between the edge and your origin.

**Replaces:** Assembling and tuning each origin-shielding piece separately (tiered cache config + a self-built health-check cron + connection-pool tuning + origin allowlisting) to protect a fragile origin.

**Use it via:** Configured as a grouping in the dashboard (Smart Shield section); underlying features keep their own per-zone settings/APIs (tiered cache, health checks, argo, cache reserve, dedicated egress IPs). Tier gates which sub-features are available.

**Capabilities:**
- Smart Tiered Cache + Regional Tiered Cache to funnel misses through upper-tier data centers and reduce origin fetches
- Connection reuse to cut the number of TCP/TLS connections opened to the origin
- Health Checks integration to monitor origin availability
- Cache Reserve integration for persistent R2-backed shielding
- Argo Smart Routing integration (optional add-on) for backbone routing
- Dedicated CDN Egress IPs (Advanced/Enterprise) so you can allowlist a stable set of Cloudflare egress IPs at your origin firewall

**Detection signals — the lens fires on these:**
- A weak/single origin (one small box, one container) behind a CDN that occasionally gets overwhelmed by miss storms
- Origin firewall rules hand-maintaining a list of Cloudflare IP ranges (could move to Dedicated Egress IPs allowlist)
- A bespoke origin health-check/cron + alerting script
- Manually configured tiered cache or origin connection tuning
- High origin connection counts / connection-exhaustion incidents

**Ideas:**
- Bundle Smart Tiered Cache + connection reuse + Health Checks to shield a single-box origin from miss storms instead of wiring each up by hand
- Adopt Dedicated CDN Egress IPs so the origin firewall allowlists a fixed IP set rather than the whole Cloudflare range
- Layer Cache Reserve into the shield so cold/long-tail objects never reach the origin

**Pairs with:** cloudflare-cache-cdn, cloudflare-argo-smart-routing, cloudflare-health-checks, cloudflare-load-balancing

**Pricing:** Tiered by plan: Smart Tiered Cache + connection reuse on all plans; Health Checks Pro and above; Regional Tiered Cache + Dedicated CDN Egress IPs on Advanced/Enterprise; Argo Smart Routing and Cache Reserve are optional usage-based add-ons (verify - drifts).

**Limits:**
- It's a packaging/umbrella over existing features rather than a single new engine - the value is curation, not a distinct capability
- Best sub-features (Regional Tiered Cache, Dedicated Egress IPs) gate behind Advanced/Enterprise
- Add-on components (Argo, Cache Reserve) carry their own usage-based costs on top

**Notes:** Newer consolidation branding - documentation explicitly folds Argo, Cache Reserve, Tiered Cache and Health Checks under it, so catalog overlap with those standalone entries is expected (cross-reference rather than double-count). Since most pieces exist independently, a team already using tiered cache + health checks may get little incremental value beyond the unified surface and the Advanced/Enterprise-only egress-IP feature.

**Docs:** https://developers.cloudflare.com/smart-shield/index.md, https://developers.cloudflare.com/smart-shield/llms.txt

---
