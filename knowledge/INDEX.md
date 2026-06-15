# Flarepilled — Cloudflare catalog index

> **124 products** across 12 categories · 118 high-confidence · seeded 2026-06-15 from `developers.cloudflare.com/llms.txt` + live per-product docs.
>
> **Catalog confidence:** `high` = docs/source-grounded at build time · `medium` = asserted or beta/unsettled, re-verify. Final flare confidence also requires observed repo fit, maturity, and no blocker. Re-check specifics (limits / pricing / bindings / API shape) against live docs before quoting. The deep entries live in `catalog/<category>.md`.

## Rules & Edge Logic (11)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Bulk Redirects** | Stop hand-managing giant nginx `map`/return-301 files, _redirects spreadsheets, or a homegrown redirect-map m… | `high` | [›](catalog/rules-edge-logic.md#bulk-redirects) |
| **Cloud Connector** | Stop running a reverse-proxy/origin-router box (nginx/HAProxy or a small app) whose only job is to forward ce… | `high` | [›](catalog/rules-edge-logic.md#cloud-connector) |
| **Cloudflare Ruleset Engine** | A hand-built edge policy engine spread across nginx maps, Envoy filters, app middleware, Terraform modules, a… | `high` | [›](catalog/rules-edge-logic.md#cloudflare-ruleset-engine) |
| **Cloudflare Snippets** | Stop deploying a full Worker, a tiny Lambda@Edge/CloudFront Function, or a VCL snippet just to do a JWT check… | `high` | [›](catalog/rules-edge-logic.md#cloudflare-snippets) |
| **Compression Rules** | Stop tuning nginx `gzip`/`brotli`/`gzip_types`/`brotli_types` and ngx_brotli module config, or Apache mod_def… | `high` | [›](catalog/rules-edge-logic.md#compression-rules) |
| **Configuration Rules** | Stop building conditional edge/CDN config or per-path nginx server blocks that toggle TLS strictness, caching… | `high` | [›](catalog/rules-edge-logic.md#configuration-rules) |
| **Custom Errors** | Stop maintaining custom error_page templates in nginx, ErrorDocument in Apache, or per-app 4xx/5xx HTML and a… | `high` | [›](catalog/rules-edge-logic.md#custom-errors) |
| **Managed Transforms** | Stop hand-writing nginx `proxy_set_header X-Forwarded-For/CF-Connecting-IP`, geo-IP header injection, or `mor… | `high` | [›](catalog/rules-edge-logic.md#managed-transforms) |
| **Origin Rules** | Stop juggling nginx `proxy_pass` upstreams + `proxy_set_header Host` + `proxy_ssl_name`/SNI, or maintaining a… | `high` | [›](catalog/rules-edge-logic.md#origin-rules) |
| **Single Redirects** | Stop maintaining nginx `return 301`/`rewrite ... redirect` blocks, Apache Redirect/RedirectMatch, framework r… | `high` | [›](catalog/rules-edge-logic.md#single-redirects) |
| **Transform Rules** | Stop hand-rolling nginx rewrite/headers-more/sub_filter, Apache mod_rewrite, or Lambda@Edge/CloudFront-Functi… | `high` | [›](catalog/rules-edge-logic.md#transform-rules) |

## Zero Trust & SASE (12)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Cloudflare Access** | Stop running a VPN concentrator, bastion/jump hosts, or a self-hosted oauth2-proxy/Pomerium/Teleport in front… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-access) |
| **Cloudflare Browser Isolation** | Stop running Menlo / Ericom / Symantec Web Isolation, or maintaining disposable-VDI / Kasm browser fleets, fo… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-browser-isolation) |
| **Cloudflare CASB** | Stop paying for Netskope SaaS Security Posture / Microsoft Defender for Cloud Apps just to audit SaaS misconf… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-casb) |
| **Cloudflare DLP** | Stop licensing Symantec / Forcepoint / Microsoft Purview DLP to catch sensitive data leaving over the web. | `high` | [›](catalog/zero-trust-sase.md#cloudflare-dlp) |
| **Cloudflare Email Security** | Stop paying for Proofpoint / Mimecast / Abnormal / Microsoft Defender for O365 as your inbound anti-phishing… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-email-security) |
| **Cloudflare Gateway** | Stop renting Cisco Umbrella / Zscaler Internet Access / Netskope SWG or self-hosting Squid + pi-hole/Pi-hole… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-gateway) |
| **Cloudflare Network Firewall (formerly Magic Firewall)** | On-prem firewall hardware and its ACLs (Palo Alto / Fortinet / Cisco ASA / Juniper SRX appliances) plus a sep… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-network-firewall-formerly-magic-firewall) |
| **Cloudflare One** | A stack of perimeter appliances + point SaaS: a hardware VPN concentrator (Cisco AnyConnect/Palo Alto GlobalP… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-one) |
| **Cloudflare Risk Score / UEBA** | A lightweight UEBA/risk-adaptive access glue stack: impossible-travel cron jobs, SIEM correlation rules, Okta… | `high` | [›](catalog/zero-trust-sase.md#cloudflare-risk-score-ueba) |
| **Data Localization (Data Localization Suite)** | A DIY data-residency build: standing up region-locked infrastructure (EU-only LBs/CDN PoPs), self-hosting TLS… | `high` | [›](catalog/zero-trust-sase.md#data-localization-data-localization-suite) |
| **Digital Experience Monitoring (DEX)** | Stop deploying Catchpoint / ThousandEyes endpoint agents or Nexthink just to see why remote users' apps and n… | `high` | [›](catalog/zero-trust-sase.md#digital-experience-monitoring-dex) |
| **WARP Client (Cloudflare One Agent)** | A traditional always-on corporate VPN client (AnyConnect/GlobalProtect/Pulse) plus a separate MDM/EDR posture… | `high` | [›](catalog/zero-trust-sase.md#warp-client-cloudflare-one-agent) |

## AI & Agents (8)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Agent Lee (Cloudflare dashboard AI assistant)** | Not a build-it-yourself substitute — it's an operator-productivity tool. Closest analog: hand-navigating the… | `high` | [›](catalog/ai-agents.md#agent-lee-cloudflare-dashboard-ai-assistant) |
| **Agent Memory** | A hand-rolled long-term-memory stack: an embeddings cron + a vector DB (pgvector/Pinecone/Vectorize) + a Post… | `high` | [›](catalog/ai-agents.md#agent-memory) |
| **Cloudflare AI (umbrella)** | A self-assembled AI stack: GPU boxes or a hosted inference API for models + a separate vector DB (self-hosted… | `high` | [›](catalog/ai-agents.md#cloudflare-ai-umbrella) |
| **Cloudflare AI Gateway** | A hand-rolled LLM proxy/middleware layer: a Redis cache for prompt responses + token/cost accounting code + p… | `high` | [›](catalog/ai-agents.md#cloudflare-ai-gateway) |
| **Cloudflare AI Search** | The hand-rolled RAG stack: an embeddings cron job + a self-hosted pgvector/Pinecone/Weaviate index + a chunki… | `high` | [›](catalog/ai-agents.md#cloudflare-ai-search) |
| **Cloudflare Agents (Agents SDK)** | A self-hosted stateful-agent backend: a long-running Node/Python process (LangGraph/CrewAI on a VM or contain… | `high` | [›](catalog/ai-agents.md#cloudflare-agents-agents-sdk) |
| **Cloudflare Vectorize** | A self-hosted pgvector/Postgres box (or a paid Pinecone/Weaviate/Qdrant subscription) plus a separate embeddi… | `high` | [›](catalog/ai-agents.md#cloudflare-vectorize) |
| **Workers AI** | A GPU box / managed inference vendor (OpenAI/Anthropic API spend, Replicate, Hugging Face Inference Endpoints… | `high` | [›](catalog/ai-agents.md#workers-ai) |

## Media (4)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Cloudflare Images** | A self-hosted sharp/ImageMagick resize pipeline writing variants to S3 + a CDN, or a SaaS like Cloudinary / i… | `high` | [›](catalog/media.md#cloudflare-images) |
| **Cloudflare Realtime (RealtimeKit + SFU + TURN)** | A self-run WebRTC stack: a SaaS like Agora / Twilio Video (sunset) / Daily / LiveKit Cloud / 100ms, OR self-h… | `high` | [›](catalog/media.md#cloudflare-realtime-realtimekit-sfu-turn) |
| **Cloudflare Stream** | Mux or Cloudinary video (or a DIY pipeline of S3 + ffmpeg transcode workers + an HLS packager + a CDN with eg… | `high` | [›](catalog/media.md#cloudflare-stream) |
| **Media over QUIC (MoQ) at Cloudflare** | A self-run low-latency live stack: an SFU/relay fleet (mediasoup/Janus/LiveKit) or RTMP-ingest + LL-HLS/DASH… | `high` | [›](catalog/media.md#media-over-quic-moq-at-cloudflare) |

## Security (15)

| Product | Replaces | Conf | |
|---|---|---|---|
| **AI Crawl Control (formerly AI Audit)** | Hand-maintained robots.txt rules plus brittle user-agent/IP blocklists in nginx/WAF that a team curates to ke… | `high` | [›](catalog/security.md#ai-crawl-control-formerly-ai-audit) |
| **Cloudflare API Shield** | Hand-built API gateway security — Kong/Apigee plugins for schema validation and JWT checks, a self-managed mT… | `high` | [›](catalog/security.md#cloudflare-api-shield) |
| **Cloudflare Bot Management / Bot Fight Mode** | Rolling your own bot detection — user-agent allowlists, reCAPTCHA Enterprise / DataDome / PerimeterX (HUMAN)… | `high` | [›](catalog/security.md#cloudflare-bot-management-bot-fight-mode) |
| **Cloudflare Challenges (Managed Challenge + Turnstile)** | Google reCAPTCHA v2/v3 or hCaptcha — the visual 'select the traffic lights' puzzles, the per-call scoring you… | `high` | [›](catalog/security.md#cloudflare-challenges-managed-challenge-turnstile) |
| **Cloudflare Client-Side Security (Page Shield)** | Hand-writing and babysitting your own Content-Security-Policy, standing up a CSP violation-report collector (… | `high` | [›](catalog/security.md#cloudflare-client-side-security-page-shield) |
| **Cloudflare DDoS Protection** | Paying for AWS Shield Advanced / a scrubbing-center provider (Arbor, Radware) or trying to absorb volumetric… | `high` | [›](catalog/security.md#cloudflare-ddos-protection) |
| **Cloudflare DMARC Management** | Paying a DMARC SaaS (Dmarcian, Valimail, EasyDMARC, Postmark's DMARC Digests) or building your own RUA mailbo… | `medium` | [›](catalog/security.md#cloudflare-dmarc-management) |
| **Cloudflare Rate Limiting Rules** | express-rate-limit, Rack::Attack, Django ratelimit, nginx `limit_req`, Redis INCR+TTL token buckets, API Gate… | `high` | [›](catalog/security.md#cloudflare-rate-limiting-rules) |
| **Cloudflare SSL/TLS** | Hand-rolled certbot/Let's Encrypt renewal cron on every box, a paid cert vendor (DigiCert, Sectigo), and DIY… | `high` | [›](catalog/security.md#cloudflare-ssl-tls) |
| **Cloudflare Secrets Store** | HashiCorp Vault / AWS Secrets Manager / Doppler — or the common DIY pattern of copy-pasting the same API key… | `high` | [›](catalog/security.md#cloudflare-secrets-store) |
| **Cloudflare Security Center** | A grab-bag of paid tools — an external attack-surface-management product (e.g. expanse-style ASM), a threat-i… | `high` | [›](catalog/security.md#cloudflare-security-center) |
| **Cloudflare Turnstile** | Google reCAPTCHA / hCaptcha (and the DIY honeypot-field + rate-limit bot-defense a team bolts onto signup, lo… | `high` | [›](catalog/security.md#cloudflare-turnstile) |
| **Cloudflare WAF (Web Application Firewall)** | A self-hosted ModSecurity/Coraza + OWASP CRS stack (or an AWS WAF / Imperva / Akamai subscription) plus the n… | `high` | [›](catalog/security.md#cloudflare-waf-web-application-firewall) |
| **Key Transparency** | Building and operating your own transparency-log auditor (signed checkpoints, epoch consistency proofs, AKD v… | `high` | [›](catalog/security.md#key-transparency) |
| **Magic Transit** | On-prem DDoS scrubbing appliances (Arbor/NETSCOUT, Radware) plus a scrubbing-center contract (Akamai Prolexic… | `high` | [›](catalog/security.md#magic-transit) |

## Messaging & Email (3)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Cloudflare Email Service** | SendGrid / Postmark / Amazon SES for outbound transactional email, plus ImprovMX / ForwardEmail / Google Work… | `high` | [›](catalog/messaging-email.md#cloudflare-email-service) |
| **Cloudflare Queues** | A self-hosted Redis/BullMQ box (or AWS SQS + its read/write/egress bills) used to offload background jobs fro… | `high` | [›](catalog/messaging-email.md#cloudflare-queues) |
| **Email Routing / Email Workers** | ImprovMX, ForwardEmail, Google Workspace catch-all routing, SendGrid/Mailgun inbound parse webhooks, MX mailb… | `high` | [›](catalog/messaging-email.md#email-routing-email-workers) |

## Observability & Analytics (10)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Cloudflare Analytics / Custom Dashboards** | A homegrown Cloudflare metrics dashboard, scheduled GraphQL/API scraper into Grafana/Looker/BigQuery, or one-… | `high` | [›](catalog/observability.md#cloudflare-analytics-custom-dashboards) |
| **Cloudflare Logs (Logpush / Logpull / Instant Logs)** | A DIY log-shipping pipeline (Fluentd/Vector/Logstash + a Kafka/Kinesis hop + retry/batching code) that a team… | `high` | [›](catalog/observability.md#cloudflare-logs-logpush-logpull-instant-logs) |
| **Cloudflare Notifications (Alerting)** | A homegrown alerting layer (cron jobs polling Cloudflare's API + a rules engine + a Slack/PagerDuty webhook p… | `high` | [›](catalog/observability.md#cloudflare-notifications-alerting) |
| **Cloudflare Web Analytics** | Google Analytics (GA4) for basic traffic/RUM, or a paid privacy-analytics SaaS like Plausible / Fathom / Simp… | `high` | [›](catalog/observability.md#cloudflare-web-analytics) |
| **GraphQL Analytics API** | Hand-rolled scrapers/cron jobs that hit a dozen per-product Cloudflare REST endpoints and stitch the results,… | `high` | [›](catalog/observability.md#graphql-analytics-api) |
| **Log Explorer** | A Splunk / Datadog Logs / Elastic (ELK) / self-hosted OpenSearch cluster — and the Logpush-to-SIEM plumbing f… | `high` | [›](catalog/observability.md#log-explorer) |
| **Network Error Logging (NEL)** | Building your own client-side connectivity beacon (a fetch-with-retry-and-report-to-an-endpoint script) plus… | `high` | [›](catalog/observability.md#network-error-logging-nel) |
| **Network Flow (formerly Magic Network Monitoring)** | A self-hosted flow-collector stack (nfdump/nfsen, pmacct, ntopng, Akvorado, Elastiflow, or a Grafana+InfluxDB… | `high` | [›](catalog/observability.md#network-flow-formerly-magic-network-monitoring) |
| **Workers Analytics Engine** | A self-hosted ClickHouse/TimescaleDB/InfluxDB box (plus its ingestion pipeline and retention ops) that a team… | `high` | [›](catalog/observability.md#workers-analytics-engine) |
| **Workers Observability / Workers Logs** | Shipping Worker console output and invocation metadata to Datadog / CloudWatch / Splunk / New Relic (and the… | `high` | [›](catalog/observability.md#workers-observability-workers-logs) |

## Performance & CDN (10)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Argo Smart Routing** | Paying for premium transit / a private backbone or accepting default BGP routing and slow cross-continent ori… | `high` | [›](catalog/performance-cdn.md#argo-smart-routing) |
| **Automatic Platform Optimization (APO)** | A WordPress page-cache plugin (WP Rocket / W3 Total Cache / LiteSpeed Cache) and/or paying up for managed Wor… | `high` | [›](catalog/performance-cdn.md#automatic-platform-optimization-apo) |
| **Cloudflare Cache / CDN** | A third-party CDN vendor (Fastly/Akamai/CloudFront) plus the egress bills you pay your origin host/S3 for eve… | `high` | [›](catalog/performance-cdn.md#cloudflare-cache-cdn) |
| **Cloudflare China Network** | Standing up a separate China stack — a licensed China CDN/cloud (Alibaba Cloud, Tencent Cloud) plus a second… | `high` | [›](catalog/performance-cdn.md#cloudflare-china-network) |
| **Cloudflare Load Balancing** | A self-managed NGINX/HAProxy LB pair plus a hand-rolled failover script, or AWS ELB/ALB + Route 53 health-che… | `high` | [›](catalog/performance-cdn.md#cloudflare-load-balancing) |
| **Cloudflare Speed (Observatory)** | A standalone web-perf monitoring/RUM vendor (SpeedCurve, Calibre, Datadog RUM) plus the front-end build plumb… | `high` | [›](catalog/performance-cdn.md#cloudflare-speed-observatory) |
| **Cloudflare Waiting Room** | A hand-built queue/throttle (Redis-backed rate limiter + a custom waiting page) or a dedicated virtual-queue… | `high` | [›](catalog/performance-cdn.md#cloudflare-waiting-room) |
| **Google Tag Gateway (for Advertisers)** | Building your own server-side GTM / first-party tagging proxy (a reverse proxy + container that rehosts gtag.… | `high` | [›](catalog/performance-cdn.md#google-tag-gateway-for-advertisers) |
| **Health Checks (standalone)** | A self-hosted uptime monitor (a cron + curl + PagerDuty glue, Uptime Kuma) or a paid uptime SaaS (Pingdom, Up… | `high` | [›](catalog/performance-cdn.md#health-checks-standalone) |
| **Smart Shield** | Assembling and tuning each origin-shielding piece separately (tiered cache config + a self-built health-check… | `high` | [›](catalog/performance-cdn.md#smart-shield) |

## Networking & DNS (17)

| Product | Replaces | Conf | |
|---|---|---|---|
| **1.1.1.1 Resolver** | Hand-rolled DNS lookups via a flaky upstream resolver or a paid DNS-over-HTTPS provider; a self-hosted recurs… | `high` | [›](catalog/networking-dns.md#1-1-1-1-resolver) |
| **BYOIP (Bring Your Own IP)** | Keeping a colo/transit setup (your own ASN announced via your ISPs + scrubbing-center contracts) just to pres… | `high` | [›](catalog/networking-dns.md#byoip-bring-your-own-ip) |
| **Cloudflare DNS** | A self-run BIND/PowerDNS/CoreDNS cluster, or a paid managed-DNS plan (Route 53, NS1, Dyn, DNSimple) plus your… | `high` | [›](catalog/networking-dns.md#cloudflare-dns) |
| **Cloudflare DNS Firewall** | Authoritative DNS DDoS appliances, dnsdist/anycast cache layers, random-prefix attack runbooks, or overbuilt… | `high` | [›](catalog/networking-dns.md#cloudflare-dns-firewall) |
| **Cloudflare Internal DNS** | CoreDNS/dnsmasq/Bind split-horizon configs, Consul DNS, Route 53 private hosted zones, ad hoc .internal/.corp… | `medium` | [›](catalog/networking-dns.md#cloudflare-internal-dns) |
| **Cloudflare Network Interconnect (CNI)** | Reaching Cloudflare (for Magic Transit/Magic WAN) over the public Internet or hand-built GRE/IPsec tunnels, o… | `high` | [›](catalog/networking-dns.md#cloudflare-network-interconnect-cni) |
| **Cloudflare Registrar** | Markup-and-upsell registrars (GoDaddy, Namecheap, Google Domains successor Squarespace) where renewals creep… | `high` | [›](catalog/networking-dns.md#cloudflare-registrar) |
| **Cloudflare Spectrum** | Exposing a raw origin IP behind a HAProxy/iptables box, a hardware DDoS scrubbing appliance, or a paid L4 ant… | `high` | [›](catalog/networking-dns.md#cloudflare-spectrum) |
| **Cloudflare Tunnel** | Poking holes in your firewall: public IPs + inbound port-forwarding + an nginx reverse proxy, or a self-manag… | `high` | [›](catalog/networking-dns.md#cloudflare-tunnel) |
| **Cloudflare WAN (formerly Magic WAN)** | MPLS circuits + traditional SD-WAN appliances + the hub-and-spoke model where every branch backhauls through… | `high` | [›](catalog/networking-dns.md#cloudflare-wan-formerly-magic-wan) |
| **Cloudflare Web3 Gateways** | Running and babysitting your own IPFS node / pinning infra, or paying a hosted node provider (Infura, Alchemy… | `medium` | [›](catalog/networking-dns.md#cloudflare-web3-gateways) |
| **Cloudflare for SaaS (SSL for SaaS / Custom Hostnames)** | A DIY custom-domains feature: scripting Let's Encrypt/ACME + certbot, managing cert storage/renewal cron, wir… | `high` | [›](catalog/networking-dns.md#cloudflare-for-saas-ssl-for-saas-custom-hostnames) |
| **Multi-Cloud Networking (formerly Magic Cloud Networking)** | Hand-stitching multi-cloud connectivity: AWS Transit Gateway + Azure Virtual WAN + GCP Network Connectivity C… | `medium` | [›](catalog/networking-dns.md#multi-cloud-networking-formerly-magic-cloud-networking) |
| **Network & Protocol Settings (zone toggles)** | Hand-tuning protocol support on nginx/HAProxy/Envoy or your cloud load balancer: nginx `listen 443 ssl http2`… | `high` | [›](catalog/networking-dns.md#network-protocol-settings-zone-toggles) |
| **Privacy Gateway** | Building your own OHTTP/mixnet relay tier, or trusting a single proxy you operate to 'promise' it won't link… | `high` | [›](catalog/networking-dns.md#privacy-gateway) |
| **Privacy Proxy** | Operating your own VPN/proxy egress fleet (WireGuard/OpenVPN boxes, SOCKS gateways, rotating egress IPs) to g… | `high` | [›](catalog/networking-dns.md#privacy-proxy) |
| **Workers VPC** | The DIY 'let my edge function reach my private VPC' stack: public API gateway/ALB or bastion+VPN, IP allowlis… | `high` | [›](catalog/networking-dns.md#workers-vpc) |

## Storage, Databases & Data (8)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Cloudflare Artifacts** | Standing up and babysitting your own Git server (Gitea/GitLab on a VM with replication + backups), or bolting… | `high` | [›](catalog/storage-data.md#cloudflare-artifacts) |
| **Cloudflare D1** | A managed Postgres/MySQL instance (RDS, Neon, PlanetScale, Supabase) plus its connection-pooling layer — or a… | `high` | [›](catalog/storage-data.md#cloudflare-d1) |
| **Cloudflare Hyperdrive** | A self-hosted connection pooler (PgBouncer/RDS Proxy) plus a hand-rolled read-through cache (a Redis box in f… | `high` | [›](catalog/storage-data.md#cloudflare-hyperdrive) |
| **Cloudflare Pipelines** | A self-hosted Kafka + Flink/Spark Streaming + S3 sink stack (or a Kinesis Firehose / Confluent + a custom Par… | `high` | [›](catalog/storage-data.md#cloudflare-pipelines) |
| **Cloudflare R2** | AWS S3 + its egress/data-transfer bills (the single biggest hook); also the wider 'S3 bucket + CloudFront CDN… | `high` | [›](catalog/storage-data.md#cloudflare-r2) |
| **R2 Data Catalog** | AWS Glue Data Catalog, Hive Metastore, Apache Nessie, a self-hosted Iceberg REST catalog, or custom metadata… | `medium` | [›](catalog/storage-data.md#r2-data-catalog) |
| **R2 SQL** | A self-managed analytics stack: an S3 data lake + AWS Athena/Presto/Trino (or DuckDB/Spark on a box) + Glue c… | `high` | [›](catalog/storage-data.md#r2-sql) |
| **Workers KV** | A Redis/Memcached box (or Upstash/ElastiCache) fronting config, feature flags, sessions, or allow/deny-lists… | `high` | [›](catalog/storage-data.md#workers-kv) |

## Compute & Workers (11)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Cloudflare Containers** | A box you keep warm to run code Workers can't: an ECS/Fargate task, a Fly.io app, a Kubernetes deployment, or… | `high` | [›](catalog/compute-workers.md#cloudflare-containers) |
| **Cloudflare Durable Objects** | A Redis box (or upstash) for sessions/locks/coordination + Pusher/Ably/Socket.io for realtime fan-out — colla… | `high` | [›](catalog/compute-workers.md#cloudflare-durable-objects) |
| **Cloudflare Sandbox SDK** | A self-hosted code-execution sandbox built on Firecracker/gVisor microVMs or Docker-on-a-VM (plus the EC2/Far… | `high` | [›](catalog/compute-workers.md#cloudflare-sandbox-sdk) |
| **Cloudflare Workers** | AWS Lambda + API Gateway (or an always-on Express/Fastify box on EC2/a VPS behind a load balancer) — plus the… | `high` | [›](catalog/compute-workers.md#cloudflare-workers) |
| **Cloudflare Workflows** | A hand-rolled durable-job stack: a queue + a worker pool + a state table that records 'which step did we reac… | `high` | [›](catalog/compute-workers.md#cloudflare-workflows) |
| **Dynamic Workers (Worker Loader)** | A self-hosted code-execution sandbox: Firecracker/gVisor microVMs, Docker-per-execution on a container host,… | `high` | [›](catalog/compute-workers.md#dynamic-workers-worker-loader) |
| **Workers Builds** | A GitHub Actions / GitLab CI / CircleCI pipeline whose entire job is to checkout, install, build, and run `wr… | `high` | [›](catalog/compute-workers.md#workers-builds) |
| **Workers Cron Triggers** | A cron box, Kubernetes CronJob, GitHub scheduled workflow, EventBridge Scheduler, node-cron/APScheduler proce… | `high` | [›](catalog/compute-workers.md#workers-cron-triggers) |
| **Workers Service Bindings / RPC** | Public workers.dev/internal HTTP calls between Workers, internal API gateways, service-to-service bearer toke… | `high` | [›](catalog/compute-workers.md#workers-service-bindings-rpc) |
| **Workers Static Assets** | S3 + CloudFront static hosting, Vercel/Netlify for greenfield Cloudflare-hosted static/full-stack apps, nginx… | `high` | [›](catalog/compute-workers.md#workers-static-assets) |
| **Workers for Platforms** | A hand-rolled multi-tenant code-execution layer: spinning up per-customer containers/VMs/Lambdas, a homegrown… | `high` | [›](catalog/compute-workers.md#workers-for-platforms) |

## Platform & DevEx (15)

| Product | Replaces | Conf | |
|---|---|---|---|
| **Cloudflare Billing, Usage-Based Billing & Budget Alerts** | A DIY cost-monitoring pipeline — cron jobs scraping GraphQL Analytics into a spreadsheet/Datadog dashboard an… | `high` | [›](catalog/platform-devex.md#cloudflare-billing-usage-based-billing-budget-alerts) |
| **Cloudflare Browser Run (formerly Browser Rendering)** | A self-hosted headless Chrome/Puppeteer farm (Dockerized chrome-aws-lambda / browserless boxes, or a Lambda l… | `high` | [›](catalog/platform-devex.md#cloudflare-browser-run-formerly-browser-rendering) |
| **Cloudflare Flagship** | A self-hosted LaunchDarkly/Unleash/Flagsmith deployment, or a hand-rolled flags system (config in KV/a DB + a… | `high` | [›](catalog/platform-devex.md#cloudflare-flagship) |
| **Cloudflare Fundamentals (Accounts, API Tokens, RBAC, Audit Logs, SCIM/SSO, 2FA)** | Rolling your own access layer in front of Cloudflare — sharing one Global API Key, building custom role/permi… | `high` | [›](catalog/platform-devex.md#cloudflare-fundamentals-accounts-api-tokens-rbac-audit-logs-scim-sso-2fa) |
| **Cloudflare Pages** | Vercel / Netlify hosting bills (plus the Jamstack stack of an S3 bucket + CloudFront + a CI build runner + a… | `high` | [›](catalog/platform-devex.md#cloudflare-pages) |
| **Cloudflare Pulumi Provider** | Custom provisioning scripts (or a Terraform setup the team doesn't want) — letting you define Cloudflare infr… | `high` | [›](catalog/platform-devex.md#cloudflare-pulumi-provider) |
| **Cloudflare Radar** | Paying for a threat-intel / internet-measurement data feed (e.g. Cisco Umbrella popularity list, commercial B… | `high` | [›](catalog/platform-devex.md#cloudflare-radar) |
| **Cloudflare Randomness Beacon (drand / League of Entropy)** | Trusting a single server's local RNG (crypto.randomBytes / /dev/urandom) for anything that must be provably f… | `medium` | [›](catalog/platform-devex.md#cloudflare-randomness-beacon-drand-league-of-entropy) |
| **Cloudflare Tenant Platform (Tenant API)** | A home-grown multi-tenant control plane — your own per-customer account abstraction, manual onboarding runboo… | `high` | [›](catalog/platform-devex.md#cloudflare-tenant-platform-tenant-api) |
| **Cloudflare Terraform Provider** | Hand-rolled bash/Python scripts that POST to api.cloudflare.com/client/v4 to create DNS records, WAF rules, a… | `high` | [›](catalog/platform-devex.md#cloudflare-terraform-provider) |
| **Cloudflare Time Services (NTP / NTS / Roughtime)** | Pointing servers at random pool.ntp.org hosts or a single upstream NTP server with no authentication — i.e. t… | `high` | [›](catalog/platform-devex.md#cloudflare-time-services-ntp-nts-roughtime) |
| **Cloudflare Zaraz** | Google Tag Manager + Segment (client-side script soup) — and the per-vendor <script> tags / dataLayer plumbin… | `high` | [›](catalog/platform-devex.md#cloudflare-zaraz) |
| **Resource Tagging** | A homegrown resource inventory/tagging convention — a spreadsheet, a naming hack like `team-prod-svc-*`, or a… | `high` | [›](catalog/platform-devex.md#resource-tagging) |
| **Version Management** | A DIY 'config as code' safety net — Terraform plan/apply discipline plus a manual change-management runbook a… | `high` | [›](catalog/platform-devex.md#version-management) |
| **Workers Local Development & Testing** | Hand-rolled KV/R2/D1/Durable Object mocks, old remote-only `wrangler dev --remote` loops for normal developme… | `high` | [›](catalog/platform-devex.md#workers-local-development-testing) |

## Also in the knowledge base

- [`catalog/frameworks-ecosystem.md`](catalog/frameworks-ecosystem.md) — Cloudflare's native frameworks & build tooling (Astro, Vite/VoidZero, C3 + the framework matrix).
- [`community-patterns.md`](community-patterns.md) — community-sourced patterns, clever combos, and gotchas (confidence-tagged, anecdotal).
- [`FRESHNESS.md`](FRESHNESS.md) — canonical sources + how to detect & fix catalog drift.
