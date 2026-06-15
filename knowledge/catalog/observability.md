# Observability & Analytics

_10 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Cloudflare Analytics / Custom Dashboards
`cloudflare-analytics-custom-dashboards` · Observability / Analytics · confidence: `high` · lock-in: `portable`

**Is:** Native Cloudflare traffic and security analytics, including custom dashboards and GraphQL datasets, so teams do not have to scrape Cloudflare APIs into a separate dashboard just to see edge behavior.

**Replaces:** A homegrown Cloudflare metrics dashboard, scheduled GraphQL/API scraper into Grafana/Looker/BigQuery, or one-off CSV exports for traffic/security/cache/bot analytics.

**Use it via:** Cloudflare dashboard: Analytics & Logs > Custom Dashboards. Programmatic queries through the GraphQL Analytics API. Log Explorer-backed charts require Log Explorer data. No Worker binding.

**Capabilities:**
- Custom Dashboards with widgets over many Cloudflare analytics datasets
- Prebuilt templates for common views such as traffic, performance, API, bot, DNS, Workers, Zero Trust, and security analytics
- GraphQL Analytics API exposes more than 100 datasets for programmatic queries
- Log Explorer charts can be added to dashboards for precise log-backed views where available
- Dashboard views can combine multiple Cloudflare product metrics without running a separate collector

**Detection signals — the lens fires on these:**
- Cron jobs querying Cloudflare GraphQL/REST analytics only to populate a dashboard
- Grafana/Looker/Metabase dashboards whose source tables are just Cloudflare traffic/cache/security aggregates
- Manual CSV exports from Cloudflare analytics pages
- Runbooks that tell operators to check multiple Cloudflare product dashboards and paste numbers together
- Custom API glue to chart bot, cache, WAF, DNS, Workers, or Zero Trust metrics already available in Cloudflare

**Ideas:**
- Replace a cron-scraped Grafana board of Cloudflare traffic/cache metrics with a Custom Dashboard and only keep external export for long retention or non-Cloudflare joins.
- Use a dashboard template for bot/API/security analysis before writing a bespoke analytics page.
- For product metrics that need exact logs, add Log Explorer charts rather than approximating from sampled aggregates.

**Pairs with:** Log Explorer, Logpush, R2, Workers Observability / Workers Logs, WAF, Bot Management, Cache Analytics, Zero Trust analytics

**Pricing:** Custom Dashboards are available to all Cloudflare customers; Log Explorer charts and dataset retention/precision depend on the underlying analytics/log product and plan.

**Limits:**
- Custom Dashboard count: 25 dashboards for all customers; Log Explorer custom dashboards can have a separate higher cap
- Standard analytics datasets may be sampled or aggregated; use Log Explorer/Logpush/R2 when you need raw event retention
- Not a full BI warehouse: cross-cloud joins, long retention, and arbitrary transformations still belong in your analytics stack
- GraphQL dataset availability and dimensions vary by product and plan

**Notes:** The winning move is often 'delete the small dashboard scraper,' not 'replace the whole data warehouse.' Keep external analytics when Cloudflare data must be joined with app/business events, retained for years, or transformed heavily; use Custom Dashboards for Cloudflare-native operational visibility.

**Docs:** https://developers.cloudflare.com/analytics/llms.txt, https://developers.cloudflare.com/analytics/custom-dashboards/index.md, https://developers.cloudflare.com/analytics/graphql-api/index.md, https://developers.cloudflare.com/analytics/log-explorer/charts/

---

## Cloudflare Logs (Logpush / Logpull / Instant Logs)
`logs-logpush` · Observability / Log Pipeline · confidence: `high` · lock-in: `sticky`

**Is:** Cloudflare's log delivery layer: Logpush streams per-event request/security logs in near-real-time to your storage/SIEM, Instant Logs tails them live in the dashboard/CLI, and Logpull is the legacy REST pull.

**Replaces:** A DIY log-shipping pipeline (Fluentd/Vector/Logstash + a Kafka/Kinesis hop + retry/batching code) that a team builds to get edge/CDN/WAF logs into S3 or a SIEM like Splunk/Datadog.

**Use it via:** REST: create/manage jobs at `POST /accounts/{account_id}/logpush/jobs` or `/zones/{zone_id}/logpush/jobs` (set `dataset`, `destination_conf`, `logpull_options`/output_options, `filter`); also configurable in dash and via the `cloudflare_logpush_job` Terraform resource. Instant Logs via dashboard or `wrangler tail`-style CLI.

**Capabilities:**
- Logpush: batched near-real-time delivery (no minimum batch size, can exceed once-per-minute) to 15+ destinations
- Destinations span object storage, SIEMs, and log managers — R2, S3 (+ S3-compatible), GCS, BigQuery, Azure, Splunk, Datadog, Sumo Logic, Elastic, New Relic, IBM QRadar/Cloud Logs, SentinelOne, Kinesis, generic HTTP, Cloudflare Pipelines
- Many datasets beyond HTTP: firewall_events, dns_logs, spectrum_events, nel_reports, Workers trace events, Gateway, audit logs, and more (zone- and account-scoped)
- Field selection + filters on the job so you only ship the columns/events you need
- Instant Logs for live tail; Logpull (legacy) for REST-based pull of HTTP request logs

**Detection signals — the lens fires on these:**
- Log shippers in the stack aimed at CDN/edge logs: `fluentd`, `fluent-bit`, `vector`, `logstash`, `filebeat`
- A custom worker/cron polling Cloudflare Logpull and writing to S3/GCS
- SIEM creds for ingesting web logs: SPLUNK_HEC_TOKEN, DATADOG_API_KEY, SUMO_HTTP_SOURCE, Elastic/New Relic ingest keys
- An S3/R2 bucket named like `*-cf-logs` / `cloudflare-logs-*` populated by a homegrown exporter
- Kafka/Kinesis topic carrying edge request logs en route to cold storage or a lake

**Ideas:**
- Stand up a Logpush job to R2 for cheap, egress-free long-term raw log retention instead of an S3 + Fluentd pipeline
- Ship firewall_events + http_requests to Splunk/Datadog via Logpush rather than maintaining a log-forwarder fleet
- Use Instant Logs to live-debug a misbehaving route in prod without deploying extra tooling

**Pairs with:** r2, log-explorer, splunk/datadog/sumo, cloudflare-pipelines

**Pricing:** Logpush is generally an Enterprise-plan capability (some datasets/plan exceptions exist); Cloudflare does not bill per-log for Logpush itself, but destination egress + the destination vendor's ingest cost are yours (R2 has no egress fee). No pricing page in the logs index. (verify — drifts)

**Limits:**
- Logpush delivers but does NOT store or let you search — pair with Log Explorer or your destination for query
- Zone-scoped HTTP requests are the only dataset also available via Logpull; everything else is Logpush-only
- Largely Enterprise-gated; field/dataset availability varies by product and plan
- At-least-once delivery — files can be delivered more than once per minute; dedupe downstream if needed

**Notes:** Pick Logpush when you already own a SIEM/lake and just need the firehose; pick Log Explorer when you want query without owning that stack. R2 as the destination is the egress-cost escape hatch. Enterprise gating is the main adoption blocker.

**Docs:** https://developers.cloudflare.com/logs/index.md, https://developers.cloudflare.com/logs/logpush/index.md, https://developers.cloudflare.com/logs/logpush/logpush-job/enable-destinations/index.md, https://developers.cloudflare.com/logs/logpush/logpush-job/datasets/index.md

---

## Cloudflare Notifications (Alerting)
`notifications` · Observability / Alerting · confidence: `high` · lock-in: `portable`

**Is:** Built-in alerting that watches your Cloudflare account for events — DDoS attacks, origin error spikes, cert expiry, health-check failures, usage/billing, WAF/security events — and fans them out via email, webhook, or PagerDuty.

**Replaces:** A homegrown alerting layer (cron jobs polling Cloudflare's API + a rules engine + a Slack/PagerDuty webhook poster), or paying a generic monitoring SaaS to watch CDN/security signals Cloudflare already sees.

**Use it via:** REST under `/accounts/{account_id}/alerting/v3/` — policies, destinations/webhooks, and `available_alerts`; Terraform resources `cloudflare_notification_policy` and `cloudflare_notification_policy_webhooks`. Generic webhook delivers JSON with a `cf-webhook-auth` secret header.

**Capabilities:**
- Huge catalog of event types: HTTP/L3-4 DDoS (basic + advanced), Origin/Advanced Error Rate, Traffic Anomalies, Health Check status, Universal/Advanced SSL + many cert-expiration alerts, WAF Security Events, Bot detection, Logpush job failure, Tunnel/Load Balancer pool health, Magic Transit attacks, Usage-Based Billing, and more
- Three delivery channels: Email (all plans), Webhooks (Pro+), PagerDuty (Business+)
- Webhooks integrate with Slack, Google Chat, Microsoft Teams, Discord, Feishu, ServiceNow, plus key-based Datadog/OpsGenie/Splunk and fully generic endpoints
- Webhook auth via the `cf-webhook-auth` header (shared secret you verify); documented payload schema per alert type
- Notification history for auditing what fired

**Detection signals — the lens fires on these:**
- A cron/Worker polling Cloudflare GraphQL/REST for error-rate or attack spikes and posting to Slack itself
- Hand-rolled cert-expiry checkers (openssl s_client scripts, a `check-cert-expiry` cron) for CF-managed certs
- Incoming Slack/Teams webhook URLs (`hooks.slack.com/services/...`, Teams connector URLs) wired into a custom notifier
- PagerDuty Events API integration keys used by a bespoke 'is Cloudflare angry?' watcher
- Health-check / uptime scripts duplicating Cloudflare Load Balancing or Health Checks alerting

**Ideas:**
- Wire Origin Error Rate + HTTP DDoS alerts straight to PagerDuty/Slack instead of a custom polling watcher
- Get proactive SSL/cert-expiration alerts for every CF-managed cert rather than a cron that runs openssl
- Alert on Usage-Based Billing thresholds to catch cost surprises before the invoice

**Pairs with:** pagerduty, slack/teams (webhooks), health-checks, waf

**Pricing:** Included; channel availability is plan-gated — Email on all plans, Webhooks on Pro+, PagerDuty on Business+. (verify — drifts)

**Limits:**
- Only fires on proxied domains — Cloudflare must see the traffic to evaluate a trigger
- Alerts on Cloudflare-observable events only; it won't watch your origin app's internal metrics
- Webhook/PagerDuty channels gated behind Pro/Business tiers respectively
- Specific alert types are themselves plan- or product-gated (e.g. Advanced DDoS/SSL alerts)

**Notes:** The clean win is deleting a 'poll CF + post to Slack' cron. It is NOT a general APM/alerting replacement (Datadog/Grafana alerting) for your own services — scope is Cloudflare-observable events. Note webhooks (Pro+) and PagerDuty (Business+) gating before recommending on Free zones.

**Docs:** https://developers.cloudflare.com/notifications/index.md, https://developers.cloudflare.com/notifications/notification-available/index.md, https://developers.cloudflare.com/notifications/get-started/configure-webhooks/index.md, https://developers.cloudflare.com/notifications/get-started/configure-pagerduty/index.md

---

## Cloudflare Web Analytics
`web-analytics` · Observability / Web RUM · confidence: `high` · lock-in: `portable`

**Is:** Privacy-first, cookieless Real User Monitoring you add to any website with a single JS beacon — page views, referrers, dimensions, and Core Web Vitals, no personal data collected.

**Replaces:** Google Analytics (GA4) for basic traffic/RUM, or a paid privacy-analytics SaaS like Plausible / Fathom / Simple Analytics — plus the cookie-consent banner they force you to maintain.

**Use it via:** Client JS beacon `<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token":"<TOKEN>"}'></script>` placed before </body> (token copied from dashboard 'Manage site'); auto-injected for proxied zones; SPA mode supported. Reporting is viewed in dashboard.

**Capabilities:**
- Cookieless, no-personal-data RUM — collects metrics via the browser Performance API
- Works on ANY site via a JS snippet — no DNS change and no need to proxy through Cloudflare
- Core Web Vitals (LCP/INP/CLS) plus page-load-time, high-level metrics, referrers, and configurable dimensions
- Filters and Rules to scope tracking to specific sites/paths
- Available on all Cloudflare plans

**Detection signals — the lens fires on these:**
- GA in the codebase: `gtag('config', ...)`, `react-ga`, `react-ga4`, `googletagmanager.com/gtag/js`, GA_MEASUREMENT_ID / G-XXXX
- Paid privacy-analytics SDKs: `plausible-tracker`, Plausible/Fathom/Simple Analytics script tags or NEXT_PUBLIC_PLAUSIBLE_DOMAIN
- A cookie-consent banner library (`cookie-consent`, `react-cookie-consent`, OneTrust) present mainly because analytics sets cookies
- web-vitals npm package wired to a homegrown `/collect` endpoint to hand-roll Core Web Vitals capture
- Self-hosted Matomo/Umami/PostHog instance used only for pageview + CWV reporting

**Ideas:**
- Swap GA4 for Cloudflare Web Analytics to drop the cookie banner and the personal-data liability on a marketing site
- Add the beacon to a non-Cloudflare-proxied site to get Core Web Vitals RUM in minutes
- Replace a self-hosted Umami/Matomo box used only for pageviews + CWV with the zero-ops beacon

**Pairs with:** speed observatory (rum-beacon), pages, web analytics notifications

**Pricing:** Free; available on all plans. No per-pageview charge documented. (verify — drifts)

**Limits:**
- Sampling applies on high-traffic sites; not session/user-level product analytics (no funnels, cohorts, or per-user paths like PostHog/Amplitude)
- Metrics come from the Performance API beacon — ad-blockers can suppress the beacon, undercounting traffic
- No documented data-export/reporting API in the index — reporting is dashboard-centric

**Notes:** Great as a GA/Plausible replacement for traffic + Web Vitals where privacy and 'no cookie banner' matter. NOT a substitute for event/product analytics (PostHog, Amplitude, Mixpanel). I confirmed the cookieless Performance-API beacon mechanism and 'any site / no proxy' support from the about + get-started pages; the literal data-cf-beacon snippet shown here is the standard form — the get-started page directs you to copy the exact token-bearing snippet from the dashboard.

**Docs:** https://developers.cloudflare.com/web-analytics/index.md, https://developers.cloudflare.com/web-analytics/about/index.md, https://developers.cloudflare.com/web-analytics/get-started/index.md, https://developers.cloudflare.com/web-analytics/data-metrics/core-web-vitals/index.md

---

## GraphQL Analytics API
`graphql-analytics-api` · Observability / Platform Analytics · confidence: `high` · lock-in: `portable`

**Is:** A single GraphQL endpoint to pull pre-aggregated analytics about traffic flowing through Cloudflare (HTTP requests, Firewall/WAF, Load Balancing, and most other CF products) by zone or account.

**Replaces:** Hand-rolled scrapers/cron jobs that hit a dozen per-product Cloudflare REST endpoints and stitch the results, or paying for a third-party CDN-analytics dashboard, just to chart Cloudflare-side traffic and security metrics.

**Use it via:** Single endpoint `POST https://api.cloudflare.com/client/v4/graphql` with an API token (Bearer) or API key headers; body is a GraphQL query selecting `viewer.zones`/`viewer.accounts` dataset nodes with filter/limit/orderBy.

**Capabilities:**
- One GraphQL endpoint covers many datasets: HTTP requests, Firewall/WAF events, Load Balancing, DNS, Workers, and more
- Server-side aggregation, grouping, time-bucketing, and filtering — you ask for exactly the rollup you want
- Zone-scoped and account-scoped nodes; the same API powers Cloudflare's own dashboard charts
- Schema is introspectable; good fit for feeding internal dashboards or Grafana

**Detection signals — the lens fires on these:**
- Cron jobs / scripts calling many `api.cloudflare.com/client/v4/zones/{id}/analytics/...` REST endpoints and merging them
- Code paginating per-product Cloudflare stats to build an internal traffic or WAF dashboard
- A homegrown 'CDN report' service pulling cache hit ratio, bandwidth, or threat counts on a schedule
- Grafana/Looker dashboards wired to bespoke CF REST pulls rather than the GraphQL dataset
- CLOUDFLARE_API_TOKEN used by reporting/analytics jobs (vs. config-management jobs)

**Ideas:**
- Replace a multi-endpoint CF stats scraper with one GraphQL query that returns exactly the time-bucketed rollup you chart
- Feed an internal Grafana dashboard with zone HTTP + WAF event counts from the single GraphQL node
- Pull per-zone cache hit ratio and bandwidth for a customer-facing usage report

**Pairs with:** logs (logpush), analytics-engine, grafana

**Pricing:** Included with Cloudflare plans; data granularity/retention scales with plan tier (Free/Pro/Biz/Ent). No separate per-query charge documented. (verify — drifts)

**Limits:**
- Query complexity, time range, and retention are capped per plan (see GraphQL API limits page)
- Explicitly NOT a billing source of truth — datasets include traffic (e.g. DDoS) that CF excludes from billable metrics
- Reports Cloudflare-edge data only — it knows nothing about your origin/app internals (that's Analytics Engine's job)

**Notes:** Best for Cloudflare-side traffic/security analytics you'd otherwise scrape. Not for app-level custom events (Analytics Engine) and not for per-request forensic detail (Log Explorer / Logpush). Numbers can differ from billing dashboards by design.

**Docs:** https://developers.cloudflare.com/analytics/graphql-api/index.md, https://developers.cloudflare.com/analytics/index.md

---

## Log Explorer
`log-explorer` · Observability / Log Storage & Search · confidence: `high` · lock-in: `sticky`

**Is:** Cloudflare-native log storage + SQL search and forensics, so you can investigate HTTP/security logs directly in the dashboard or API without forwarding anything to a third-party SIEM.

**Replaces:** A Splunk / Datadog Logs / Elastic (ELK) / self-hosted OpenSearch cluster — and the Logpush-to-SIEM plumbing feeding it — that a team runs purely to retain and query Cloudflare logs.

**Use it via:** REST API under the Log Explorer endpoints (dataset management + SQL query submission, see `/log-explorer/api/`); SQL query interface documented in `/log-explorer/sql-queries/`; also driven from the Cloudflare dashboard.

**Capabilities:**
- Stores Cloudflare logs inside Cloudflare with full platform context (no forwarding/egress to a SIEM)
- SQL-based log search + saved/example queries for forensics and incident investigation
- Dashboard and API access; manage which datasets are retained
- Long retention for contract customers — up to two years of stored logs
- Billing is on volume ingested/stored, not on how often you search or scan

**Detection signals — the lens fires on these:**
- A SIEM/log-store running mostly to hold CF logs: `@elastic/elasticsearch`, OpenSearch, Splunk, Datadog Logs, Loki
- Logpush jobs whose only purpose is to feed a search index you also pay to operate
- Ops paying for log-retention storage + ingest in a third-party tool for compliance/forensics on edge traffic
- Grep-the-bucket workflows: engineers downloading R2/S3 log files and scanning them ad hoc
- Incident runbooks that say 'pull the WAF logs from Splunk' for a CF-fronted property

**Ideas:**
- Drop a redundant ELK/Splunk tier and keep CF logs queryable in Log Explorer for SOC investigations
- Run SQL forensics over firewall/HTTP logs during an incident straight from the dashboard
- Hold 2 years of security logs for compliance without standing up cold-storage + a query engine

**Pairs with:** logs (logpush), waf, r2, graphql-analytics-api

**Pricing:** Paid add-on for any Application Services or Zero Trust purchase; no free tier/trial. Billed on volume of logs ingested AND stored (GB), independent of query frequency. Extended retention for contract customers cited at $0.10 per GB per month. (verify — drifts)

**Limits:**
- No free version or trial; requires an underlying Application Services or Zero Trust subscription
- You pay for ingest + storage volume — high-traffic zones can get expensive vs. sampled analytics
- Scoped to Cloudflare log datasets; not a general-purpose log lake for arbitrary app logs

**Notes:** The 'stop running a SIEM just for CF logs' play. If you already have a mature Splunk/Datadog estate that ingests app logs too, Log Explorer complements rather than replaces it. Storage-volume billing (not query billing) is the key economics flip vs. scan-priced tools.

**Docs:** https://developers.cloudflare.com/log-explorer/index.md, https://developers.cloudflare.com/log-explorer/pricing/index.md, https://developers.cloudflare.com/log-explorer/api/index.md, https://developers.cloudflare.com/log-explorer/sql-queries/index.md

---

## Network Error Logging (NEL)
`network-error-logging` · Observability / Last-Mile Reachability · confidence: `high` · lock-in: `portable`

**Is:** Uses the browser's W3C Network Error Logging standard — Cloudflare injects the Report-To/NEL headers — so visitors' browsers report connection failures (DNS/TCP/TLS/HTTP) back to Cloudflare, giving you last-mile reachability data your server logs can never see.

**Replaces:** Building your own client-side connectivity beacon (a fetch-with-retry-and-report-to-an-endpoint script) plus the ingest/aggregation backend, or paying a synthetic/RUM vendor (Catchpoint, ThousandEyes, Datadog RUM) just to see last-mile failures.

**Use it via:** No code to write — Cloudflare automatically returns the Report-To and NEL response headers for zones, and browsers do the reporting. Consume via dashboard (Analytics & Logs > Edge Reachability) or push to your SIEM/storage with Logpush (NEL reports dataset). Opt-out via dashboard toggle or a permanent opt-out through support.

**Capabilities:**
- Surfaces failures that happen BEFORE the request reaches Cloudflare/your origin (the 'last mile') — invisible to normal access logs
- Browser sends JSON reports per the W3C NEL spec when DNS/TCP/TLS/HTTP errors occur
- Reports include error type, elapsed time, HTTP method, protocol, and geo/network context
- Categorized error types: tcp.timed_out / tcp.failed / tcp.aborted, h2.protocol_error / h3.protocol_error, tls.cert.authority_invalid / tls.cert.name_invalid / TLS version & cipher mismatch
- Aggregates by Origin ASN, Origin IP, country/metro, and the probable intended Cloudflare data center
- Viewable in the dashboard (Analytics & Logs > Edge Reachability) and exportable via Logpush
- Privacy-preserving: no PII stored; any IP data lives only in volatile memory for the request duration

**Detection signals — the lens fires on these:**
- A Cloudflare zone (proxied/orange-cloud) where the team complains about 'users can't connect but our logs look clean' — exactly the gap NEL fills
- Home-grown client-side connectivity/heartbeat beacons posting to /collect or an analytics endpoint to detect outages
- Manually setting Report-To / NEL / Reporting-Endpoints headers in app or edge config
- Paying for synthetic monitoring or RUM (Catchpoint, ThousandEyes, Datadog RUM, SpeedCurve) primarily to catch reachability/last-mile issues
- Support tickets about regional ISP outages, TLS cert errors, or QUIC/HTTP3 reachability that can't be reproduced server-side
- Existing Logpush jobs — adding the NEL dataset is near-free

**Ideas:**
- Turn on NEL and watch Edge Reachability to spot regional ISP/last-mile outages and TLS cert errors your origin logs never record
- Logpush the NEL dataset into your SIEM/BigQuery to alert on tcp.timed_out or tls.cert.* spikes by ASN/country
- Use NEL error types + probable-data-center fields to triage whether a reported outage is a specific ISP, a Cloudflare PoP, or your TLS config

**Pairs with:** logpush, cdn, waf

**Pricing:** Built into Cloudflare zones; the docs imply broad availability with no plan restriction called out, surfaced free in the dashboard. Logpush export availability follows your plan's Logpush entitlement. (verify — drifts)

**Limits:**
- Depends entirely on browser support for the W3C NEL spec (Chromium-based browsers; not all browsers report)
- Only covers traffic to proxied Cloudflare zones — not arbitrary endpoints
- Reports are sampled/best-effort and asynchronous; not a real-time per-user alarm
- By design stores no PII / per-user data, so you can't pivot to an individual affected user
- Plan-level access to NEL data and to Logpush export was not explicitly confirmed on the fetched pages

**Notes:** This is essentially free passive last-mile telemetry you may already be entitled to and not using — high-value to flag whenever a proxied zone exists. It complements (does not replace) RUM/synthetic monitoring: NEL only sees connection-level failures, not page performance or in-app errors. Whether it's on by default vs. needs enabling, and exact plan gating for the data/Logpush, were not nailed down in the fetched pages — verify in the dashboard. Browser-coverage caveat means absence of reports != absence of problems.

**Docs:** https://developers.cloudflare.com/network-error-logging/llms.txt, https://developers.cloudflare.com/network-error-logging/index.md, https://developers.cloudflare.com/network-error-logging/how-to/index.md, https://developers.cloudflare.com/network-error-logging/reference/index.md

---

## Network Flow (formerly Magic Network Monitoring)
`network-flow` · Network / Observability & Flow Analytics · confidence: `high` · lock-in: `portable`

**Is:** Ships your routers' NetFlow/sFlow/IPFIX samples (or cloud VPC flow logs) to Cloudflare, which turns them into traffic analytics and threshold/anomaly alerts — and can detect volumetric DDoS and auto-trigger Magic Transit mitigation.

**Replaces:** A self-hosted flow-collector stack (nfdump/nfsen, pmacct, ntopng, Akvorado, Elastiflow, or a Grafana+InfluxDB pipeline) running on a box you babysit — or a paid NPM/flow SaaS (Kentik, ThousandEyes, SolarWinds NTA).

**Use it via:** REST under /accounts/{account_id}/mnm (legacy 'Magic Network Monitoring' path): config (default sampling, router IPs) and rules CRUD (/mnm/rules, with rule advertisement update for Magic Transit). AWS VPC flow logs are API-only: token at /accounts/{account_id}/mnm/vpc-flows/token. Routers export to a Cloudflare-network IP shown in the dashboard after you register the router's public IP + sampling rate. Analytics via GraphQL.

**Capabilities:**
- Ingests NetFlow v5, NetFlow v9, IPFIX, and sFlow exported from your routers
- Cloud flow logs (beta): AWS VPC flow logs via Firehose for cloud environments
- Traffic analytics dashboards for visibility, troubleshooting, capacity planning
- Rules engine: static-threshold and dynamic-threshold (anomaly) rules with notifications when volume thresholds are crossed
- sFlow DDoS attack rule type for volumetric attack detection on your public IPs
- Magic Transit integration: detected attacks can auto-advertise prefixes / activate Magic Transit on-demand mitigation
- GraphQL Analytics API to pull flow data programmatically
- Free tier suitable for home networks, labs, and small businesses

**Detection signals — the lens fires on these:**
- Routers/switches configured to export flow data: 'ip flow-export', 'flow-monitor', sFlow agents, 'sampler', netflow/ipfix collector configs
- Self-hosted flow tooling: nfdump, nfsen, pmacct, ntopng, Akvorado, Elastiflow, fastnetmon
- A Grafana/InfluxDB/Elasticsearch pipeline whose only job is NetFlow/sFlow visualization
- Paying for Kentik, ThousandEyes, Deepfield, SolarWinds NTA, or Auvik for flow analytics
- AWS VPC Flow Logs piped to S3/Firehose for traffic analysis
- Magic Transit customer wanting automated 'detect attack -> turn on mitigation' instead of manual on-demand activation
- Home-lab / SMB asking 'what's eating my bandwidth' without a flow collector

**Ideas:**
- Point your edge routers' NetFlow/sFlow export at Network Flow instead of running an nfsen/ntopng box, and get hosted analytics + alerts free for up to 10 routers
- Wire Network Flow's sFlow DDoS-attack rules to auto-activate Magic Transit on-demand so volumetric attacks trigger mitigation without a human
- Use dynamic-threshold rules to alert on traffic anomalies (exfil spikes, scanning, link saturation) per-router

**Pairs with:** magic-transit, byoip, network-interconnect

**Pricing:** Free version available to everyone (all enterprise features, with volume/config caps). Free limits: 10 registered routers, 25 rules, 250 network flows/sec per account. Paid/enterprise raises those caps and unlocks higher-scale DDoS workflows. (verify — drifts)

**Limits:**
- Free tier hard caps: 10 routers, 25 rules, 250 flows/sec/account
- DDoS-flow detection on public IPs and the automated Magic Transit mitigation workflow are aimed at enterprise / Magic Transit customers
- AWS VPC flow logs are beta and API-only (no dashboard setup)
- Sampling-based: accuracy depends on chosen sampling rate; expect ~5–10 min before flows appear
- It's monitoring/alerting on flows — it does not itself mitigate; mitigation comes from Magic Transit

**Notes:** Genuinely useful even free and even without the rest of Cloudflare's network stack — a real replacement for a DIY flow collector. The renamed product (was Magic Network Monitoring) still uses 'mnm' in API paths, so detection/grep should look for both names. Data retention windows and paid-tier exact caps weren't quoted on fetched pages — verify. Not a packet-capture/full-PCAP tool (that's a separate Magic Transit feature); it works on sampled flow records.

**Docs:** https://developers.cloudflare.com/network-flow/llms.txt, https://developers.cloudflare.com/network-flow/index.md, https://developers.cloudflare.com/network-flow/get-started/index.md, https://developers.cloudflare.com/network-flow/network-flow-free/index.md, https://developers.cloudflare.com/network-flow/api/index.md

---

## Workers Analytics Engine
`analytics-engine` · Observability / Custom Analytics · confidence: `high` · lock-in: `portable`

**Is:** A Worker binding that writes unlimited-cardinality time-series data points and a SQL API to query them, for building custom analytics, usage metering, or per-customer dashboards.

**Replaces:** A self-hosted ClickHouse/TimescaleDB/InfluxDB box (plus its ingestion pipeline and retention ops) that a team stands up just to record custom app/usage events at high write volume.

**Use it via:** Worker binding via wrangler.jsonc `analytics_engine_datasets: [{ binding, dataset }]`; write with `env.<BINDING>.writeDataPoint({ blobs, doubles, indexes })`; query via REST `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/analytics_engine/sql` with a Bearer token and a raw SQL body.

**Capabilities:**
- writeDataPoint() from inside a Worker — non-blocking, no await-the-network cost on the hot path
- Unlimited cardinality: high-cardinality dimensions (per-user, per-customer) go in blobs without exploding storage
- SQL API for querying (ClickHouse-style SQL), incl. SUM(_sample_interval * doubleN) sampling math
- Schema is implicit: up to 20 blobs (strings), 20 doubles (numbers), 1 index (sampling key)
- Built for usage-based billing, per-customer service-health, and instrumenting hot code paths

**Detection signals — the lens fires on these:**
- Self-hosted OLAP in the stack: `clickhouse`, `clickhouse-client`, `@clickhouse/client`, TimescaleDB, InfluxDB, `influxdb-client`, Prometheus remote-write for app metrics
- Env vars like CLICKHOUSE_URL / INFLUXDB_TOKEN / TIMESCALE_DSN feeding a custom events/metrics table
- A Worker (or any app) hand-rolling per-customer usage counters in KV/D1/Postgres and aggregating with cron — high write, low-precision-OK analytics
- A bespoke `events` or `usage_events` table with (timestamp, customer_id, metric, value) being bulk-inserted for dashboards or metering
- StatsD/dogstatsd custom metrics where the cardinality (user IDs, tenant IDs) is the whole point

**Ideas:**
- Meter per-tenant API usage for usage-based billing by calling writeDataPoint on each request, then roll up monthly with the SQL API
- Build a per-customer 'service health' panel (latency, error counts by customer) without standing up a metrics DB
- Instrument an existing Worker's hot path (cache hit rate, route timings) with near-zero added latency

**Pairs with:** workers, grafana (CF plugin / GraphQL), log-explorer

**Pricing:** Free (Workers Free): 100k data points written/day + 10k read queries/day. Paid (Workers Paid): 10M writes/mo included (+$0.25/additional million) and 1M read queries/mo included (+$1.00/additional million). Docs note billing is not currently enforced. (verify — drifts)

**Limits:**
- Max ~20 blobs, ~20 doubles, 1 index per data point; index limited to a single value today
- Data is sampled — query math must multiply by _sample_interval; not exact-count accounting for finance-grade ledgers
- Querying is read-only SQL against your datasets; not a general-purpose database

**Notes:** The right tool for high-volume, sampling-tolerant custom metrics — NOT for exact financial counts or as a transactional store (use D1/Postgres there). Querying is its own SQL dialect; some ClickHouse functions are unsupported. Lock-in is moderate: write API and SQL endpoint are Cloudflare-specific.

**Docs:** https://developers.cloudflare.com/analytics/analytics-engine/index.md, https://developers.cloudflare.com/analytics/analytics-engine/get-started/index.md, https://developers.cloudflare.com/analytics/analytics-engine/pricing/index.md

---

## Workers Observability / Workers Logs
`workers-observability` · Observability · confidence: `high` · lock-in: `portable`

**Is:** Built-in logs, live tail, traces, and invocation analytics for Workers — queryable in the dashboard with no log-shipping agent or third-party APM.

**Replaces:** Shipping Worker console output and invocation metadata to Datadog / CloudWatch / Splunk / New Relic (and the agents, log drains, and per-GB ingest bills that come with them) just to see what your Worker is doing.

**Use it via:** wrangler config: `[observability] enabled = true` + `head_sampling_rate` (0–1) in wrangler.toml/wrangler.jsonc (per-env under `[env.<name>.observability]`); requires Wrangler 3.78.6+. CLI: `wrangler tail` for real-time logs. Binding-style: `tail_consumers` to attach a Tail Worker. Logpush: `logpush = true` in wrangler config to enable Workers Trace Events Logpush. Dashboard: Workers & Pages > (Worker) > Observability (logs view + Query Builder + metrics). MCP server available for querying observability data.

**Capabilities:**
- Workers Logs: automatically ingest, store, filter, and analyze logs emitted from a Worker, retained in your Cloudflare account and queryable per-Worker in the dashboard Observability tab (enable via `[observability] enabled = true`).
- Captures `console.log()` output, structured JSON (auto-indexed for querying), invocation/event metadata, and uncaught exceptions.
- Query Builder: write structured queries with filters, aggregations, and groupings to investigate and visualize telemetry and spot patterns.
- Built-in metrics & analytics: request counts, error rates, CPU time, wall time, and execution duration, per-Worker or aggregated.
- Real-time logs: stream live log events via `wrangler tail` or the dashboard for immediate feedback.
- Tail Workers (`tail_consumers`): a Worker that receives another Worker's telemetry to apply custom filtering, sampling, and transformation.
- Traces: end-to-end request visibility with automatic instrumentation.
- Export to any OTLP endpoint (Honeycomb, Grafana Cloud, Axiom, Sentry) and Workers Logpush to external destinations (R2, Datadog, Splunk, etc.) when you do want to keep an external sink.

**Detection signals — the lens fires on these:**
- `datadog`, `dd-trace`, `@datadog/browser-logs`, `winston-cloudwatch`, `aws-sdk` CloudWatch Logs `putLogEvents`, or Splunk HEC calls inside a Worker just to emit logs.
- A Worker doing `fetch()` to a log-collector endpoint (Datadog intake, Logtail, Logflare, Better Stack) on every request.
- `DD_API_KEY`, `DATADOG_API_KEY`, `LOGTAIL_TOKEN`, `NEW_RELIC_LICENSE_KEY`, Splunk HEC tokens in Worker secrets/vars.
- Hand-rolled structured-logging wrappers around `console.log` plus a buffer/flush to an external HTTP sink (and the `ctx.waitUntil` flush plumbing).
- No `[observability]` block in wrangler config despite heavy external logging — i.e. paying twice.

**Ideas:**
- This Worker POSTs every request's logs to Datadog via fetch + a DD API key — enable Workers Logs (`[observability] enabled = true`) and query in the dashboard instead of paying per-GB ingest.
- You wrote a console.log wrapper that buffers and ships to CloudWatch with the AWS SDK — drop it and use built-in Workers Logs + Query Builder, or Logpush if you still need an external sink.
- You poll a third-party APM for Worker error rate and CPU time — those are built-in Workers metrics; use the Observability tab / Query Builder.
- You need logs in your existing Grafana/Honeycomb — keep Workers Logs for debugging and add OTLP export instead of an in-Worker SDK.

**Pairs with:** Workers, Workers Builds, Wrangler, Workers Logpush, Tail Workers, R2 (Logpush destination)

**Pricing:** Workers Logs included with Workers (enable via observability config); head-based sampling via `head_sampling_rate`. Workers Logpush requires the Workers Paid plan. OTLP/Logpush egress and any third-party destination billed by that destination. (verify — drifts.)

**Limits:**
- Workers Logs retention is 7 days (max).
- Account limit ~5 billion logs/account/day; individual log capped at 256 KB.
- Logpush `logs` + `exceptions` fields share a 16,384-character cap before truncation.
- Logpush is Workers Paid only; Tail Workers is beta.
- head_sampling_rate controls what fraction of invocations are logged (default 1.0) — sampling below 1 means not every request is captured.

**Notes:** Best for debugging, live tail, and short-window analytics native to Workers. NOT a full-retention log warehouse or cross-service APM: 7-day retention and per-Worker scope mean you still want Logpush-to-R2/SIEM or OTLP export for compliance retention, long-term analytics, or unifying with non-Cloudflare services. Structured JSON logging maximizes query value. Enabling observability without sampling on very high-volume Workers can hit the daily log cap — tune head_sampling_rate.

**Docs:** https://developers.cloudflare.com/workers/observability/, https://developers.cloudflare.com/workers/observability/logs/, https://developers.cloudflare.com/workers/observability/logs/workers-logs/, https://developers.cloudflare.com/workers/observability/logs/logpush/

---
