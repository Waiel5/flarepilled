# Networking & DNS

_17 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## 1.1.1.1 Resolver
`cloudflare-1111-resolver` · Networking / DNS · confidence: `high` · lock-in: `portable`

**Is:** Cloudflare's free public DNS resolver, reachable over plain DNS, DNS-over-HTTPS (including a JSON API), and DNS-over-TLS.

**Replaces:** Hand-rolled DNS lookups via a flaky upstream resolver or a paid DNS-over-HTTPS provider; a self-hosted recursive resolver (Unbound/BIND) you maintain just to do programmatic name resolution.

**Use it via:** REST-ish DoH JSON: GET https://cloudflare-dns.com/dns-query?name=example.com&type=AAAA with header Accept: application/dns-json (no token). Also wireformat DoH (POST/GET, application/dns-message) and DoT on 853. Returns {Status, Answer:[{name,type,TTL,data}], ...}.

**Capabilities:**
- Public recursive DNS at 1.1.1.1 / 1.0.0.1 and 2606:4700:4700::1111 / ::1001
- DNS-over-HTTPS JSON API: GET https://cloudflare-dns.com/dns-query with Accept: application/dns-json, params name, type, do (DNSSEC), cd (disable validation) — no auth
- DNS-over-HTTPS RFC 8484 wireformat and DNS-over-TLS (port 853)
- DNSSEC validation built in; Oblivious DNS-over-HTTPS (ODoH) support to decouple identity from query
- 1.1.1.1 for Families filtered variants: malware-blocking (1.1.1.2 / 1.0.0.2 / 2606:4700:4700::1112) and malware+adult (1.1.1.3 / 1.0.0.3 / 2606:4700:4700::1113)
- Privacy posture: does not sell user data; query logs not used to build ad profiles

**Detection signals — the lens fires on these:**
- dns.resolve / dns.lookup in Node against a hardcoded resolver, or python dnspython / socket.getaddrinfo with a configured upstream
- Hardcoded resolver IPs like 8.8.8.8 / 8.8.4.4 / 9.9.9.9 in config, /etc/resolv.conf, or container DNS settings
- Code calling a third-party DoH endpoint (e.g. dns.google/resolve) — swap to cloudflare-dns.com/dns-json
- Manual TXT/MX/SPF/DKIM/CAA record checks for email or domain-verification flows (fetching DNS in app code)
- DoH/DoT client libraries, doh-* npm packages, stub resolver containers
- Self-hosted Unbound/BIND/dnsmasq purely for outbound recursion
- Domain-verification or health-check workers that need a fast, reliable resolver

**Ideas:**
- Replace a custom DNS-lookup helper (for SPF/DKIM/MX validation in an email-verification flow) with a fetch to the 1.1.1.1 DoH JSON API — no resolver infra to run.
- Add encrypted DNS (DoT/DoH) to a Worker or edge app's outbound name resolution to avoid plaintext DNS leakage.
- Offer 1.1.1.1 for Families (1.1.1.2 / 1.1.1.3) as a one-line parental-control / malware-filtering option instead of building a blocklist-driven resolver.

**Pairs with:** Cloudflare Radar (DNS datasets sourced from 1.1.1.1), Cloudflare DNS (authoritative), Gateway / WARP

**Pricing:** Free, no API token for the public resolver and DoH JSON/wireformat endpoints (verify — drifts).

**Limits:**
- Filtered variants block by category; not a configurable per-domain policy engine (that is Cloudflare Gateway)
- DoH JSON API is convenience-shaped, not the IETF wireformat standard; for strict RFC 8484 use application/dns-message
- Public resolver — no SLA on the free tier for programmatic use at scale

**Notes:** DoH JSON API endpoint, headers, params, and the family-filter IPs are verified from fetched pages. The standard 1.1.1.1/1.0.0.1 IPv4 and 2606:4700:4700::1111/::1001 IPv6 are well-established but not literally quoted on the two pages fetched this run (they appear across the setup subpages); treat the exact IPv6 of the primary resolver as verify-if-load-bearing. Not the right tool when you need policy-based filtering or logging/visibility — that is Gateway. No lock-in: it is just a resolver address.

**Docs:** https://developers.cloudflare.com/1.1.1.1/llms.txt, https://developers.cloudflare.com/1.1.1.1/index.md, https://developers.cloudflare.com/1.1.1.1/setup/index.md, https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/make-api-requests/dns-json/index.md

---

## BYOIP (Bring Your Own IP)
`byoip` · Network / IP & Routing · confidence: `high` · lock-in: `portable`

**Is:** Announce IP prefixes you already own across Cloudflare's global anycast network, so you keep your IP space while getting Cloudflare's security and performance.

**Replaces:** Keeping a colo/transit setup (your own ASN announced via your ISPs + scrubbing-center contracts) just to preserve customer-facing IPs you can't renumber — or accepting a hard cutover to vendor-owned IPs.

**Use it via:** REST under /accounts/{account_id}/addressing/prefixes. Advertise/withdraw: PATCH /accounts/{account_id}/addressing/prefixes/{prefix_id}/bgp/prefixes/{bgp_prefix_id} (and POST .../bgp/prefixes) with on_demand {advertised: true|false}; advertisement_status edit method. Onboarding requires Letter of Agency (LOA), IRR entries, and RPKI ROAs. Dashboard: IP Prefixes page. Auth via email+API key or scoped service token.

**Capabilities:**
- Cloudflare advertises your owned prefixes (BGP) from all its edge locations under its anycast network
- Service bindings: control per-IP whether traffic routes to Magic Transit, CDN, or Spectrum
- Address maps: map specific IPs to zones/DNS records when proxied
- Dynamic advertisement: advertise/withdraw prefixes on demand via API or dashboard
- RPKI + IRR validation and Route Leak Detection to guard against hijacks
- AS prepending for graceful traffic migration when changing providers (added 2025-06-30)
- Static IPs and prefix delegation to other accounts
- Works with dedicated egress IPs and Gateway DNS locations

**Detection signals — the lens fires on these:**
- Org owns an ASN and PI (provider-independent) IPv4/IPv6 space announced to multiple transit providers
- Hard requirement to keep existing public IPs (allowlisted by partners, hardcoded in client configs, regulatory) — blocks moving to vendor IPs
- Existing RPKI ROAs / IRR route objects / LOA paperwork in infra repos
- BGP configs, bird.conf / FRR (frr.conf) / Quagga, route-maps, AS-path prepend statements
- Mentions of /24 (or larger) prefixes, RIR allocations (ARIN/RIPE/APNIC) in network docs
- Currently paying a scrubbing provider but still announcing your own space

**Ideas:**
- Migrate your owned /24s onto Cloudflare so you get edge DDoS + CDN without renumbering allowlisted IPs
- Use service bindings to send some IPs in a prefix to Magic Transit (L3 protection) and others to the CDN/Spectrum pipeline
- Set up dynamic advertisement + AS prepending so you can fail traffic back to your own DC during a provider migration without packet loss

**Pairs with:** magic-transit, network-interconnect, spectrum, cdn, gateway

**Pricing:** Enterprise-only; commercial terms are account-team negotiated (typically bundled with Magic Transit / Spectrum / CDN). No public self-serve price. (verify — drifts)

**Limits:**
- Enterprise plans only — no self-serve onboarding
- Minimum advertisable prefix is generally /24 for IPv4 (BGP global-table reachability); smaller nets must use Cloudflare-owned IPs instead
- You must own the space and prove it (LOA + IRR + RPKI); onboarding/validation can take time
- Prefix validation failures are a common onboarding snag (dedicated troubleshooting page exists)

**Notes:** BYOIP is about WHICH IPs front your traffic, not a standalone product — it's the on-ramp that lets Magic Transit/Spectrum/CDN run on your addresses. Not relevant unless the org actually owns routable PI space and has a reason to keep it; if they're fine using Cloudflare IPs, skip it. Lock-in is modest since you retain ownership of the prefixes and can withdraw them, but the BGP/RPKI/LOA setup is operationally heavy. Exact minimum prefix size and onboarding SLAs were not fully quoted on the pages fetched — verify with account team.

**Docs:** https://developers.cloudflare.com/byoip/llms.txt, https://developers.cloudflare.com/byoip/index.md, https://developers.cloudflare.com/byoip/concepts/dynamic-advertisement/index.md, https://developers.cloudflare.com/byoip/concepts/dynamic-advertisement/best-practices/index.md, https://developers.cloudflare.com/changelog/post/2025-06-30-graceful-byoip-withdrawal/

---

## Cloudflare DNS
`cloudflare-dns` · Networking / DNS · confidence: `high` · lock-in: `portable`

**Is:** Fast, anycast authoritative DNS with record management, one-click DNSSEC, CNAME flattening at the apex, and (Enterprise) AXFR/IXFR secondary/primary zone transfers.

**Replaces:** A self-run BIND/PowerDNS/CoreDNS cluster, or a paid managed-DNS plan (Route 53, NS1, Dyn, DNSimple) plus your own DNSSEC key management.

**Use it via:** REST: GET/POST/PUT/DELETE /client/v4/zones/{zone_id}/dns_records; DNSSEC at /zones/{zone_id}/dnssec; secondary/primary via /zones/{zone_id}/secondary_dns and /secondary_dns/* (Enterprise). Also cloudflare_record / cloudflare_zone in the Cloudflare Terraform provider, and wrangler-managed records for Workers/Pages custom domains.

**Capabilities:**
- Authoritative DNS on Cloudflare's anycast network, available on all plans (including Free)
- Full DNS record management (A/AAAA, CNAME, MX, TXT, SRV, CAA, etc.) via dashboard, REST API, or Terraform
- One-click DNSSEC (cryptographic signing) plus multi-signer DNSSEC for multi-provider setups
- CNAME flattening at the zone apex (and flatten-all on paid plans) so you can point the root at a CNAME target
- Secondary DNS (Cloudflare as secondary, receiving AXFR/IXFR from your primary) and primary DNS with outgoing transfers — Enterprise only
- TSIG-authenticated zone transfers, up to 30 peer associations per zone
- Zone setups: full (Cloudflare as primary nameservers), partial/CNAME (keep existing provider), and subdomain setup

**Detection signals — the lens fires on these:**
- BIND/named, PowerDNS, CoreDNS, or knot config files (named.conf, Corefile, zonefiles checked into the repo)
- Route 53 / NS1 usage: aws_route53_record in Terraform, @aws-sdk/client-route-53, boto3 route53 calls
- Hand-rolled DNSSEC key/ZSK/KSK rotation scripts or dnssec-keygen in cron
- Apex-domain hacks: ALIAS/ANAME records, or app code resolving the root domain to an IP because a CNAME at apex was not possible
- A second managed-DNS vendor kept only for redundancy (candidate to make Cloudflare the secondary)
- dig/nsupdate scripts or TSIG keys in CI used to push zone changes

**Ideas:**
- Add Cloudflare as a secondary DNS provider via AXFR/IXFR so your existing primary (e.g. Route 53) gains a redundant answer path without a full migration
- Turn on one-click DNSSEC instead of maintaining your own key-signing rotation cron
- Replace ALIAS/ANAME apex workarounds with native CNAME flattening at the zone root

**Pairs with:** cloudflare-ssl-tls, cloudflare-registrar, cloudflare-spectrum

**Pricing:** Authoritative DNS is free on all plans; record management and one-click DNSSEC included. Secondary/primary DNS (zone transfers) require Enterprise. (verify — drifts)

**Limits:**
- Zone transfers (secondary/primary, AXFR/IXFR) are Enterprise-only
- Max 30 peer associations per zone for transfers
- Private network DNS / private-origin proxying is Enterprise beta
- Flatten-all-CNAMEs requires a paid plan (apex flattening is on all plans)

**Notes:** If you proxy through Cloudflare you are already on their DNS, so this is often a zero-cost win. Honest limit: the high-availability redundancy story (secondary DNS) and private DNS are gated behind Enterprise. Multi-signer DNSSEC details were referenced in the index but not deeply fetched this run.

**Docs:** https://developers.cloudflare.com/dns/llms.txt, https://developers.cloudflare.com/dns/index.md, https://developers.cloudflare.com/dns/zone-setups/zone-transfers/index.md

---

## Cloudflare DNS Firewall
`cloudflare-dns-firewall` · DNS / Authoritative protection · confidence: `high` · lock-in: `portable`

**Is:** A DNS proxy/cache/DDoS shield in front of your existing authoritative nameservers, letting you keep BIND/PowerDNS/Knot/NSD upstream while Cloudflare absorbs attack traffic and caches responses.

**Replaces:** Authoritative DNS DDoS appliances, dnsdist/anycast cache layers, random-prefix attack runbooks, or overbuilt self-hosted nameserver fleets kept alive mostly for resilience and QPS absorption.

**Use it via:** Enterprise DNS Firewall configuration in Cloudflare dashboard/API. You configure upstream authoritative nameservers and receive Cloudflare DNS Firewall IPs/hostnames to publish as delegated nameservers for protected zones.

**Capabilities:**
- Proxies all DNS queries to your authoritative nameservers through Cloudflare's global network
- Caches DNS responses to reduce upstream nameserver load
- Protects upstream authoritative nameservers from DNS DDoS attacks
- Provides high availability, global distribution, performance, and bandwidth savings
- Optional per-data-center rate limiting, min/max cache TTL settings, and DNS ANY query blocking
- Lets teams keep upstream authoritative nameserver control instead of moving every zone to Cloudflare Authoritative DNS

**Detection signals — the lens fires on these:**
- BIND/PowerDNS/Knot/NSD authoritative nameservers fronted by dnsdist, anycast, or custom cache layers
- Runbooks for random-prefix attacks, NXDOMAIN floods, DNS DDoS, or authoritative nameserver saturation
- Authoritative DNS appliances or managed DNS DDoS add-ons
- Monitoring alerts on named/pdns/knot QPS, cache hit ratio, or upstream DNS bandwidth
- A requirement to retain authoritative DNS control while adding Cloudflare edge protection

**Ideas:**
- Put DNS Firewall in front of self-hosted authoritative nameservers to absorb DDoS/caching load without migrating zone management.
- Use Cloudflare Authoritative DNS for simple zones; use DNS Firewall when the team must keep its existing authoritative nameserver stack.
- Flag Enterprise add-on status before suggesting it for a small project.

**Pairs with:** Cloudflare Authoritative DNS, DDoS Protection, DNS Analytics, Magic Transit / Network Firewall

**Pricing:** Enterprise-only paid add-on; verify current contract terms and DNS Firewall limits before quoting.

**Limits:**
- Intended for protecting entire authoritative nameservers; use normal Cloudflare DNS setups for individual zones
- Enterprise-only paid add-on
- Does not remove the need to operate upstream authoritative nameservers

**Notes:** This is not the same as 'move DNS to Cloudflare.' It is the right flare when the upstream authoritative DNS stack stays but the protection/cache/anycast layer can be outsourced.

**Docs:** https://developers.cloudflare.com/dns/llms.txt, https://developers.cloudflare.com/dns/dns-firewall/index.md, https://developers.cloudflare.com/dns/dns-firewall/setup/index.md, https://developers.cloudflare.com/dns/dns-firewall/analytics/index.md

---

## Cloudflare Internal DNS
`cloudflare-internal-dns` · DNS / Private name resolution · confidence: `medium` · lock-in: `portable`

**Is:** Private DNS zones and views resolved through Cloudflare Gateway resolver policies, so internal hostnames are managed in Cloudflare instead of CoreDNS/dnsmasq/Consul/Route 53 private-zone glue.

**Replaces:** CoreDNS/dnsmasq/Bind split-horizon configs, Consul DNS, Route 53 private hosted zones, ad hoc .internal/.corp resolver forwarding, or regional private resolver glue.

**Use it via:** Cloudflare dashboard/API for Internal DNS zones, DNS views, internal records, reference zones, and Gateway resolver policies. Clients must on-ramp DNS traffic to Cloudflare Gateway resolver; internal zones are not queried through public Cloudflare nameservers.

**Capabilities:**
- Internal DNS zones contain records only answerable inside the private network
- DNS views group internal zones for different locations or contexts
- Gateway resolver policies select the view based on query context such as source IP
- Internal zones do not receive public Cloudflare nameservers; queries go through Cloudflare Gateway resolver
- Reference zones let one internal zone fall through to another zone for missing records
- Analytics and logs for Internal DNS queries

**Detection signals — the lens fires on these:**
- Corefile / CoreDNS, dnsmasq.conf, named.conf, Consul DNS, or Unbound configs for private app names
- Terraform `aws_route53_zone` with `private_zone = true` or cloud-provider private DNS zones
- .internal, .corp, .local, split-horizon, or private resolver forwarding runbooks
- Regional DNS views or per-office resolver config duplicated across clouds
- Gateway resolver policies already in use but private names still managed elsewhere

**Ideas:**
- Move private service names into Internal DNS zones selected by Gateway resolver policies instead of maintaining dnsmasq/CoreDNS files per network.
- Use DNS views for office/region-specific private answers instead of separate Route 53 private hosted zones.
- Do not recommend for production-critical DNS without naming beta risk and Enterprise gating first.

**Pairs with:** Cloudflare Gateway resolver policies, Cloudflare WAN, Cloudflare Mesh, Zero Trust logs

**Pricing:** Enterprise-only. Docs label Internal DNS beta and state production use is at your own risk; verify entitlement and support status before recommending.

**Limits:**
- Beta; production traffic is at the user's risk per docs
- Enterprise-only
- Requires Cloudflare Gateway resolver/on-ramp path for clients
- Internal zones do not get public Cloudflare nameservers

**Notes:** This is a strong loud-mode/explicit-ask flare for enterprises already on Cloudflare One/Gateway. Because it is beta and Enterprise-only, normal-mode production recommendations should usually stop at 'consider and verify,' not 'migrate now.'

**Docs:** https://developers.cloudflare.com/dns/llms.txt, https://developers.cloudflare.com/dns/internal-dns/index.md, https://developers.cloudflare.com/dns/internal-dns/get-started/index.md, https://developers.cloudflare.com/dns/internal-dns/internal-zones/index.md, https://developers.cloudflare.com/dns/internal-dns/dns-views/index.md, https://developers.cloudflare.com/dns/internal-dns/connectivity/index.md

---

## Cloudflare Network Interconnect (CNI)
`network-interconnect` · Network / Private Connectivity · confidence: `high` · lock-in: `portable`

**Is:** Private, non-public-Internet links into Cloudflare — either a physical cross-connect in a shared data center or a virtual circuit through a connectivity/cloud partner — for lower latency, more consistent throughput, and a smaller attack surface.

**Replaces:** Reaching Cloudflare (for Magic Transit/Magic WAN) over the public Internet or hand-built GRE/IPsec tunnels, or buying a bespoke private interconnect from your carrier/colo and wiring it yourself.

**Use it via:** Provisioning is request/ticket-driven, not self-serve API: open a CNI request with your account team (Direct), or order through a partner portal (Megaport/Equinix Fabric/etc.) / cloud provider console (AWS DC, Google Cloud Interconnect). Port speeds 10GBASE-LR / 100GBASE-LR(4) single-mode fiber (cloud: 1 or 10 Gbps). Health checks + maintenance alerts surface in dashboard/API after activation.

**Capabilities:**
- Direct Interconnect: dedicated physical fiber cross-connect in a colo where you and Cloudflare are both present (LOA-CFA, you order the cross-connect)
- Partner Interconnect: virtual connection via partners (Megaport, Equinix Fabric, Console Connect, PacketFabric, CoreSite, Digital Realty, Zayo) when you're not co-located
- Cloud Interconnect: private circuit from AWS Direct Connect or Google Cloud Interconnect to Cloudflare
- Dataplane v1 (GRE tunnels, optional GRE-less for Magic Transit DSR) and v2 (Customer Connectivity Router, GRE-less, full 1500-byte MTU bidirectional)
- Underpins Magic Transit (clean-traffic return path) and Magic WAN
- Monitoring + maintenance-window alerts; device-level diversity for HA

**Detection signals — the lens fires on these:**
- Already a Magic Transit / Magic WAN customer reaching Cloudflare over the public Internet or GRE/IPsec, hitting latency/throughput/MTU pain
- Presence in carrier-neutral facilities (Equinix, CoreSite, Digital Realty) and existing cross-connects
- Existing Megaport / Equinix Fabric / PacketFabric / Console Connect accounts or virtual cross-connects
- AWS Direct Connect or Google Cloud Interconnect already provisioned in cloud configs
- High-volume or latency-sensitive traffic to/from Cloudflare; MTU fragmentation complaints with tunnels
- Network diagrams showing private WAN / SD-WAN backhaul to a scrubbing or cloud on-ramp

**Ideas:**
- Swap public-Internet GRE tunnels feeding Magic Transit for a private cross-connect (dataplane v2) to get full 1500-byte MTU and consistent throughput
- Use Partner Interconnect via Megaport/Equinix Fabric to reach Cloudflare privately without being physically co-located
- Land an AWS Direct Connect / Google Cloud Interconnect circuit straight into Cloudflare for cloud-to-edge private connectivity

**Pairs with:** magic-transit, magic-wan, byoip

**Pricing:** Enterprise-only; commercial terms via account team. Partner/cloud circuit and cross-connect fees are billed by the partner/colo/cloud provider, separate from Cloudflare. (verify — drifts)

**Limits:**
- Enterprise-only; provisioning typically takes 2–4 weeks (physical cross-connect is the long pole)
- Direct Interconnect requires you and Cloudflare to share a data center / PoP — check the locations list and which dataplane version is supported there
- Port speeds limited to 10G/100G optics (1G/10G for cloud); HA needs device-level diversity to avoid a single point of failure
- Not a product you 'code against' — it's physical/virtual circuit provisioning, mostly a networking/procurement task

**Notes:** CNI is plumbing, not an app feature — it only makes sense alongside Magic Transit or Magic WAN (or BYOIP) where private, high-throughput reach to Cloudflare matters. Skip for pure Workers/Pages/CDN apps. Third-party costs (partner circuit, cross-connect, cloud interconnect) sit outside Cloudflare billing. Specific per-PoP availability and dataplane-v2 location coverage are in a separate locations PDF not fetched here — verify.

**Docs:** https://developers.cloudflare.com/network-interconnect/llms.txt, https://developers.cloudflare.com/network-interconnect/index.md, https://developers.cloudflare.com/network-interconnect/get-started/index.md

---

## Cloudflare Registrar
`cloudflare-registrar` · Domains / Registrar · confidence: `high` · lock-in: `portable`

**Is:** An at-cost domain registrar that charges exactly the registry + ICANN wholesale price with zero markup, free WHOIS redaction, and free DNSSEC.

**Replaces:** Markup-and-upsell registrars (GoDaddy, Namecheap, Google Domains successor Squarespace) where renewals creep and WHOIS privacy is an upsell.

**Use it via:** REST under /client/v4/accounts/{account_id}/registrar/domains (list, get, update for auto-renew/lock) and the Registrar API for availability search and registration. Documented at developers.cloudflare.com/api/resources/registrar.

**Capabilities:**
- At-cost pricing: you pay only what registries and ICANN charge, with no markup on registration or renewal
- Register brand-new domains or transfer existing ones in (transfers add a year except where the TLD forbids it, e.g. .uk)
- Free WHOIS redaction / privacy by default
- Free DNSSEC for all Cloudflare customers
- Over 400 supported TLDs, with .UK and .US handled specially
- Manage domains via dashboard or the Registrar API (search availability, register, renew, auto-renew at registry list price)

**Detection signals — the lens fires on these:**
- Domains held at GoDaddy/Namecheap/Squarespace while DNS already runs on Cloudflare (the prime migration signal)
- A paid WHOIS-privacy / domain-privacy line item on a registrar invoice
- Renewal price noticeably above the registry wholesale price (markup you could eliminate)
- Registrar API keys for a third-party registrar in CI used only to renew/lock domains
- DNSSEC disabled because the current registrar charges or makes it hard

**Ideas:**
- Transfer domains already proxied through Cloudflare into Registrar to pay wholesale and stop paying for WHOIS privacy
- Turn on free DNSSEC at the registrar level instead of a paid add-on elsewhere
- Script bulk renewals/locks through the Registrar API to standardize auto-renew across a portfolio

**Pairs with:** cloudflare-dns, cloudflare-ssl-tls

**Pricing:** No Cloudflare markup — you pay the exact registry + ICANN fee (varies by TLD). WHOIS privacy and DNSSEC are free. (verify — drifts)

**Limits:**
- Hard requirement: every Registrar domain must use Cloudflare nameservers and be active on a Cloudflare full setup — you cannot keep external DNS
- Internationalized Domain Names (IDNs / 'xn--' Punycode) are not supported
- ICANN 60-day transfer lock after WHOIS/registrar changes (.uk exempt)
- To transfer a domain out you must move to a different registrar (Cloudflare requires its own nameservers)
- ~400+ TLDs but not all are supported; some restricted statuses block inbound transfers

**Notes:** The full-setup-on-Cloudflare-nameservers requirement is the real catch: this only fits domains you are willing to run DNS for on Cloudflare. Not a fit for IDNs or for teams that need vanity/external nameservers. At-cost pricing is the whole pitch — there is no resale margin, so it is genuinely a cost-killer, not a profit center.

**Docs:** https://developers.cloudflare.com/registrar/llms.txt, https://developers.cloudflare.com/registrar/index.md, https://developers.cloudflare.com/registrar/about/index.md, https://developers.cloudflare.com/registrar/faq/index.md, https://developers.cloudflare.com/registrar/top-level-domains/index.md

---

## Cloudflare Spectrum
`cloudflare-spectrum` · Networking / L4 Proxy · confidence: `high` · lock-in: `portable`

**Is:** A reverse proxy for arbitrary TCP and UDP applications (SSH, RDP, Minecraft, MQTT, mail, FTP, game servers) that masks the origin IP and absorbs L3/4 DDoS.

**Replaces:** Exposing a raw origin IP behind a HAProxy/iptables box, a hardware DDoS scrubbing appliance, or a paid L4 anti-DDoS proxy — for traffic that is not HTTP and so cannot sit behind a normal CDN.

**Use it via:** POST /client/v4/zones/{zone_id}/spectrum/apps with body like {"protocol":"tcp/22","dns":{"type":"CNAME","name":"ssh.example.com"},"origin_direct":["tcp://192.0.2.1:22"],"proxy_protocol":"off","ip_firewall":true,"tls":"full","argo_smart_routing":true}. Token needs Zone Settings:Write. Also cloudflare_spectrum_application in Terraform.

**Capabilities:**
- Proxies any TCP- or UDP-based protocol through Cloudflare's edge, not just HTTP
- Masks the origin IP so attackers cannot reach the server directly
- Always-on L3/4 DDoS protection for the proxied app
- Optional Argo Smart Routing for lower-latency paths
- PROXY protocol support to forward the real client IP to the origin
- IP Firewall / IP access rules on the Spectrum application
- TLS termination modes (off / full) for the proxied connection
- Origin via direct IP (origin_direct), CNAME (origin_dns), or a Cloudflare Load Balancer with health checks and failover
- Supports BYOIP and Static IP (API-only)

**Detection signals — the lens fires on these:**
- Game/real-time servers (Minecraft, Valheven-style, MQTT brokers like Mosquitto/EMQX) exposed on a public IP with DNS A records pointing straight at the box
- HAProxy / iptables / nftables / nginx stream{} configs doing raw TCP/UDP load balancing in front of an origin
- SSH or RDP reachable directly from the internet (sshd on 22 / 3389 open to 0.0.0.0/0)
- FTP/SMTP/IMAP or other non-HTTP services that cannot be put behind the normal HTTP CDN
- Origin IP hardcoded in client configs / mobile apps (no IP masking) and ad-hoc fail2ban/rate-limit scripts standing in for DDoS protection

**Ideas:**
- Put a Minecraft or game server behind Spectrum (tcp/udp) to hide the origin IP and shed L3/4 DDoS instead of relying on fail2ban
- Front an MQTT broker or SSH bastion with Spectrum + IP Firewall so the box is never directly addressable
- Use Spectrum with PROXY protocol to keep real client IPs for an SMTP/IMAP origin while gaining DDoS scrubbing

**Pairs with:** cloudflare-dns, cloudflare-ssl-tls

**Pricing:** Paid feature. Pro/Business get specific named apps only (e.g. Minecraft on Pro+; SSH on Pro+; RDP on Business+) — one app per plan. Arbitrary TCP/UDP (and HTTP/HTTPS over Spectrum) require Enterprise with Spectrum as a paid add-on, typically billed on data transfer. (verify — drifts)

**Limits:**
- General-purpose TCP/UDP is Enterprise-only; Pro/Business are limited to a single specific app (Minecraft/SSH/RDP) each
- Protocol-specific constraints documented under Spectrum 'Limitations' (not all protocols behave identically)
- BYOIP and Static IP origins are API-only (no dashboard)
- Not for plain HTTP/HTTPS sites — those belong on the normal Cloudflare HTTP proxy, not Spectrum

**Notes:** Spectrum is the answer specifically when traffic is NOT HTTP and therefore cannot use the standard reverse proxy. The big gotcha is cost/availability: real flexibility is Enterprise-gated, so a hobby game server on Pro only gets the one canned Minecraft app. Exact data-transfer pricing was not on the pages fetched and should be confirmed with sales.

**Docs:** https://developers.cloudflare.com/spectrum/llms.txt, https://developers.cloudflare.com/spectrum/index.md, https://developers.cloudflare.com/spectrum/get-started/index.md, https://developers.cloudflare.com/spectrum/protocols-per-plan/index.md

---

## Cloudflare Tunnel
`cloudflare-tunnel` · Connectivity / Private Networking · confidence: `high` · lock-in: `portable`

**Is:** A lightweight daemon (cloudflared) that opens outbound-only, post-quantum-encrypted connections from your origin to Cloudflare, exposing apps and private networks with no public IP and no inbound firewall ports.

**Replaces:** Poking holes in your firewall: public IPs + inbound port-forwarding + an nginx reverse proxy, or a self-managed VPN/SSH bastion, just to reach a box behind NAT. Also replaces ngrok for stable, authenticated ingress.

**Use it via:** CLI: `cloudflared tunnel login|create|route dns|run`; service install `sudo cloudflared service install <TUNNEL_TOKEN>`; Docker `docker run cloudflare/cloudflared:latest tunnel run --token <TOKEN>`; quick dev tunnel `cloudflared tunnel --url http://localhost:8080`. Config via `ingress:` array (hostname/service/originRequest + http_status:404 catch-all) in config.yml, or the dashboard (Networking > Tunnels), or REST API (/accounts/{id}/cfd_tunnel).

**Capabilities:**
- Outbound-only tunnel: cloudflared dials Cloudflare (4 long-lived connections to 2 data centers for redundancy); no open inbound ports, no public IP, no attack surface
- Public hostname routing: map app.example.com to a local service via ingress rules; CDN cache, WAF, Bot Management, and DDoS protection apply automatically
- Private network routing: advertise RFC1918 CIDRs so WARP-enrolled users reach internal services (VPN replacement), routed via <TUNNEL_ID>.cfargotunnel.com
- Remotely-managed (dashboard token) or locally-managed (config.yml / API) tunnels
- Deployment guides for Linux, macOS, Windows, Docker, Kubernetes, AWS/Azure/GCP, Terraform, Ansible

**Detection signals — the lens fires on these:**
- ngrok / localtunnel / localhost.run in scripts, README dev instructions, or CI
- nginx/Caddy/HAProxy reverse-proxy configs whose only job is to expose an internal service publicly
- Cloud security-group / firewall rules opening inbound 80/443/22 to 0.0.0.0/0; port-forwarding on a home/office router
- Dockerfiles or compose files that EXPOSE ports + map them to a public LB just to reach an internal admin/API
- A self-hosted VPN (WireGuard/OpenVPN) used only so the team can curl an internal service; bastion/jump-host SSH configs
- Apps bound to a public IP behind NAT with dynamic-DNS hacks (ddclient, no-ip)

**Ideas:**
- Swap the ngrok tunnel in the dev/demo workflow for a named Cloudflare Tunnel so the URL is stable, authenticated (gate it with Access), and free of session limits
- Expose the self-hosted admin panel via a Tunnel public hostname instead of opening an inbound port + nginx, getting WAF/DDoS in front for free
- Advertise the datacenter's 10.0.0.0/8 over a Tunnel + WARP so engineers reach internal databases without a VPN concentrator

**Pairs with:** Cloudflare One, WARP Client, Cloudflare WAN

**Pricing:** cloudflared and Cloudflare Tunnel are free; you pay only for whatever Cloudflare plan/Zero Trust features sit on top (WAF, Access seats). (verify — drifts)

**Limits:**
- cloudflared is a process you must run and keep alive on the origin (supervise it; deploy redundant replicas for HA)
- Private-network access (VPN-replacement) requires WARP on the client side and Access policies — the tunnel alone only solves origin connectivity
- Public-docs vs Cloudflare One docs are split: VPN replacement / private routing / network filtering live under the Cloudflare One Tunnel docs, not the public-app Tunnel docs

**Notes:** Very low lock-in for the connectivity primitive itself (it's just cloudflared + DNS), but the surrounding value (WAF, Access, private routing) is Cloudflare-specific. Not a fit if you genuinely need a public, directly-addressable static IP for the origin, or for raw non-HTTP protocols better served by Spectrum/Magic WAN. Could not fetch deep private-network CIDR routing details this run (that page deferred to linked sub-pages).

**Docs:** https://developers.cloudflare.com/tunnel/llms.txt, https://developers.cloudflare.com/tunnel/index.md, https://developers.cloudflare.com/tunnel/setup/index.md

---

## Cloudflare WAN (formerly Magic WAN)
`cloudflare-wan` · Networking / WAN-as-a-Service / SD-WAN · confidence: `high` · lock-in: `portable`

**Is:** A WAN-as-a-service that connects data centers, branch offices, cloud VPCs, and remote users through Cloudflare's global network via GRE/IPsec tunnels, CNI, an appliance, or WARP — replacing MPLS and hub-and-spoke backhaul.

**Replaces:** MPLS circuits + traditional SD-WAN appliances + the hub-and-spoke model where every branch backhauls through a central data-center firewall. The 'stop paying a telco for private circuits between sites' hook.

**Use it via:** Configured via the dashboard (Magic WAN), REST API (/accounts/{id}/magic/* — GRE/IPsec tunnels, routes, sites, connectors), and Terraform (cloudflare_magic_wan_gre_tunnel, cloudflare_magic_wan_ipsec_tunnel, cloudflare_magic_wan_static_route). Physical on-ramp via the Magic WAN Connector appliance. Not an app-code SDK.

**Capabilities:**
- On-ramps: anycast GRE tunnels, IPsec tunnels, Cloudflare Network Interconnect (CNI, private direct connection), the Cloudflare One Appliance / Magic WAN Connector (hardware/software that auto-connects and steers any IP traffic), WARP client for devices, Multi-Cloud Networking auto-built tunnels to cloud VPCs, and third-party SD-WAN partner integrations
- Routing: static routes plus BGP peering (beta) to auto-announce/withdraw routes as the network changes
- Traffic steered to the nearest Cloudflare data center instead of backhauling to a central hub; policies applied at the edge
- Integrated L3/L4 security via Cloudflare Network Firewall; Zero Trust (Gateway) for filtered egress
- Load balancing, NetFlow + network analytics, connectivity troubleshooting

**Detection signals — the lens fires on these:**
- Telco/MPLS circuit references, carrier WAN configs, DMVPN/hub-and-spoke topologies
- SD-WAN vendor configs: Cisco Viptela/Meraki SD-WAN, VeloCloud (VMware), Silver Peak/Aruba, Fortinet SD-WAN, Versa
- Site-to-site VPN/IPsec configs between offices and data centers; GRE tunnel definitions on edge routers
- BGP configs backhauling branch traffic to a central firewall for inspection
- AWS Transit Gateway / Azure Virtual WAN / Direct Connect / ExpressRoute used to stitch sites + clouds together
- Branch routers doing centralized internet breakout (all internet via HQ)

**Ideas:**
- Replace the MPLS links between the three offices and the data center with anycast GRE/IPsec tunnels into Cloudflare WAN, getting local internet breakout + edge security at each site
- Deploy the Magic WAN Connector at a branch so any IP traffic auto-onramps to Cloudflare without configuring tunnels by hand
- Use BGP peering (beta) into Magic WAN so route changes propagate automatically instead of hand-editing static routes across sites

**Pairs with:** Cloudflare Network Firewall, Multi-Cloud Networking, Cloudflare One, WARP Client, Cloudflare Tunnel

**Pricing:** Enterprise / custom-contract networking product (no public self-serve price in the docs index); typically priced by committed bandwidth/connectivity. Includes Standard Network Firewall. (verify — drifts)

**Limits:**
- Enterprise networking product — overkill for app/web teams; relevant when you actually run physical sites, data centers, or multi-cloud backbones
- Requires real network engineering (tunnels, routing, BGP) and often a contract + the Connector appliance
- BGP peering is beta
- Pricing not published in docs; assume sales-led

**Notes:** Renamed from Magic WAN. The docs show two names for the on-ramp appliance — 'Cloudflare One Appliance' and 'Magic WAN Connector' — likely the same hardware mid-rename; verify the current name. Strong lock-in (your WAN backbone runs on Cloudflare). Not a fit for a pure serverless/SaaS shop with no physical network footprint.

**Docs:** https://developers.cloudflare.com/cloudflare-wan/llms.txt, https://developers.cloudflare.com/cloudflare-wan/index.md, https://developers.cloudflare.com/cloudflare-wan/on-ramps/index.md

---

## Cloudflare Web3 Gateways
`cloudflare-web3-gateways` · Web3 / Decentralized Networks · confidence: `medium` · lock-in: `portable`

**Is:** HTTPS gateways that let standard HTTP clients read IPFS content and talk to the Ethereum JSON-RPC API without running your own IPFS or Ethereum node.

**Replaces:** Running and babysitting your own IPFS node / pinning infra, or paying a hosted node provider (Infura, Alchemy, Pinata) for RPC and gateway access.

**Use it via:** Gateways are configured as hostnames on a zone (DNSLink via a DNS TXT record + a Web3 hostname). Management API: /client/v4/zones/{zone_id}/web3/hostnames (list/create/get/edit/delete). Consumption is plain HTTPS GET against the gateway hostname (IPFS) or JSON-RPC POST (Ethereum).

**Capabilities:**
- IPFS Gateway: read-only HTTPS access to IPFS content (by CID) with no IPFS software or local storage
- DNSLink gateways (map a hostname to IPFS content via DNS) — available on all plans
- Universal Path gateway (path-style access) — Enterprise only
- Ethereum Gateway: read and write to Ethereum via the official Ethereum JSON-RPC API without running a node
- Served over Cloudflare's anycast network for global performance and DDoS resilience
- No per-file size limit on IPFS across tiers

**Detection signals — the lens fires on these:**
- ipfs-http-client, kubo / go-ipfs, js-ipfs, or a self-hosted IPFS daemon in the stack
- Pinata, web3.storage, nft.storage, or Infura/Alchemy API keys and SDKs (INFURA_PROJECT_ID, ALCHEMY_API_KEY) in env
- ethers.js / web3.js / viem pointed at a self-run Geth/Erigon node or a paid RPC URL
- Hardcoded public IPFS gateway URLs (ipfs.io, dweb.link) for serving NFT metadata/assets
- dApp front-ends resolving CIDs or making eth_call / JSON-RPC requests from the browser

**Ideas:**
- Serve NFT metadata and dApp assets through a Cloudflare IPFS DNSLink gateway on your own domain instead of running a pinning node or hardcoding ipfs.io
- Point ethers.js/viem at the Cloudflare Ethereum Gateway as a node-free JSON-RPC endpoint to reduce reliance on a single RPC vendor
- Map a branded hostname to IPFS content via DNSLink so users get HTTPS + Cloudflare performance over decentralized storage

**Pairs with:** cloudflare-dns, cloudflare-ssl-tls

**Pricing:** Usage-based. IPFS includes 50 GB bandwidth on Free/Pro/Business (100 GB Enterprise), billed beyond that; up to 15 gateways on Free/Pro/Business, unlimited on Enterprise. Ethereum Gateway includes a baseline of ~500k-1M HTTP requests by tier, usage-based after. Enterprise can run it as a no-meter preview. (verify — drifts)

**Limits:**
- IPFS Gateway is read-only (it serves content; it does not pin/host on your behalf)
- Universal Path gateway is Enterprise-only; non-Enterprise uses DNSLink gateways
- Gateway count capped at 15 on non-Enterprise plans
- Bandwidth/requests metered beyond the included tier

**Notes:** Honest caveat on currency: the Ethereum Gateway pages fetched THIS run show NO deprecation banner and present it as active and usage-billed across all plans — but Cloudflare's public Ethereum/IPFS gateway offering has historically been in flux, so treat write/RPC availability and new-signup status as UNVERIFIED and confirm before designing around it. IPFS gateway is read-only, so you still need a pinning service to keep content alive. Decentralization purists may object to routing 'Web3' through a single CDN.

**Docs:** https://developers.cloudflare.com/web3/llms.txt, https://developers.cloudflare.com/web3/index.md, https://developers.cloudflare.com/web3/ipfs-gateway/index.md, https://developers.cloudflare.com/web3/ethereum-gateway/index.md

---

## Cloudflare for SaaS (SSL for SaaS / Custom Hostnames)
`cloudflare-for-saas` · Custom domains / TLS automation for SaaS · confidence: `high` · lock-in: `portable`

**Is:** Lets your SaaS customers point their own vanity/custom domains at your service and get auto-provisioned, auto-renewed TLS certificates plus Cloudflare's WAF/cache/Argo, without them changing DNS providers.

**Replaces:** A DIY custom-domains feature: scripting Let's Encrypt/ACME + certbot, managing cert storage/renewal cron, wiring up a wildcard ingress / nginx-on-the-fly TLS layer (lego, Caddy on-demand TLS, AWS ACM + a CloudFront/ALB per tenant), and polling DNS for CNAME/TXT validation.

**Use it via:** REST: GET /zones/{zone_id}/custom_hostnames (list) and POST /zones/{zone_id}/custom_hostnames to create — body includes hostname, ssl.method (one of http | txt | email) and ssl.type 'dv'. Fallback origin managed via GET/PUT/DELETE /zones/{zone_id}/custom_hostnames/fallback_origin. No Workers binding and no wrangler config — it's a zone-level REST/dashboard feature (also Terraform cloudflare_custom_hostname).

**Capabilities:**
- Custom hostnames: customer-owned domains added to YOUR Cloudflare zone, routed to a 'fallback origin' (one default origin server on your domain)
- Automatic certificate issuance, validation, and renewal per customer hostname (DV certs); DCV via HTTP, TXT, email, or delegated DCV
- Extends Cloudflare WAF, caching, Argo, early hints to customers' domains
- Customer onboards with a single CNAME to your fallback hostname — they keep their DNS provider
- Pre-validation, realtime validation, and validation-status APIs; custom metadata attachable per hostname for routing/tenant config
- Custom certificate upload + enforce mTLS (Enterprise); apex proxying / BYOIP for root-domain customers (Enterprise add-on)

**Detection signals — the lens fires on these:**
- ACME/Let's Encrypt automation: certbot, lego, acme.sh, greenlock, @certificate-helper, Caddy on-demand TLS in a tenant app
- Env/config like LETSENCRYPT_EMAIL, ACME_*, a certs/ volume or DB table storing PEM/keys per customer, a cert-renewal cron/Lambda
- Per-tenant TLS termination infra: wildcard nginx + dynamic vhosts, AWS ACM + per-customer CloudFront/ALB, HAProxy SNI maps
- A 'custom domain' / 'connect your domain' / 'vanity URL' / 'white-label domain' feature with CNAME-verification + cert-status polling
- DNS validation polling code checking customer CNAME/TXT records before activating a domain
- SaaS/website-builder/e-commerce/newsletter products that host customers on subdomains today and want to upgrade them to bring-your-own-domain
- Per-customer custom-domain security settings, ModSecurity/Kong plugins, tenant WAF tables, or custom-hostname metadata used to decide WAF/rate-limit posture

**Ideas:**
- Add a self-serve 'bring your own domain' flow where customers CNAME in and certs provision automatically — no certbot, no renewal cron
- White-label your app on customers' apex/vanity domains with WAF + caching applied per hostname
- Attach per-hostname custom metadata so a single fallback origin can route/brand requests by tenant
- Use WAF for SaaS when each customer's custom hostname needs managed rules or rate limits at the edge instead of per-tenant origin middleware

**Pairs with:** WAF for SaaS (per-hostname managed rulesets), Cache for SaaS / Argo for SaaS / Early Hints for SaaS, Workers (worker-as-origin pattern lets a Worker, not a fixed server, back the fallback origin)

**Pricing:** 100 custom hostnames included free on all plans (Free, Pro, Business, Enterprise); $0.10 per additional active custom hostname on Free/Pro/Business. Max 50,000 hostnames on non-Enterprise (Enterprise unlimited via sales). Custom certificate upload, enforce-mTLS, apex proxying/BYOIP, and custom firewall rulesets are Enterprise-only; non-Enterprise gets WAF rules at the current zone plan. (verify — drifts)

**Limits:**
- 50,000 custom hostnames cap on Free/Pro/Business; Enterprise to go beyond
- Custom/BYO certificates restricted to Enterprise — Free/Pro/Business get Cloudflare-issued DV certs only
- Apex proxying / BYOIP and custom metadata gated to Enterprise (paid add-ons)

**Notes:** Two products live under 'Cloudflare for Platforms' — this is the CUSTOM-DOMAINS/TLS one (distinct from Workers for Platforms compute). Trade-off: your customers' domains now resolve through your Cloudflare zone, so you inherit responsibility for their TLS/availability and they depend on your CF account. The create-hostname POST body (ssl.method http|txt|email, ssl.type dv) and fallback-origin concept are grounded in fetched pages; the exact POST path was confirmed only as the GET list path /zones/{zone_id}/custom_hostnames from the API index — the POST shares that collection path (standard CF REST convention) but I could not fetch the POST page body this run. 'Argo for SaaS' exists in the index but its pricing was not on the plans page I fetched.

**Docs:** https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/index.md, https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/security/waf-for-saas/index.md, https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/plans/index.md, https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/start/common-api-calls/index.md, https://developers.cloudflare.com/api/resources/custom_hostnames/methods/list/index.md

---

## Multi-Cloud Networking (formerly Magic Cloud Networking)
`multi-cloud-networking` · Networking / Multi-Cloud Connectivity · confidence: `medium` · lock-in: `portable`

**Is:** A Cloudflare One service (beta) that discovers your public-cloud resources (VPCs, subnets, VMs, route tables across AWS, Azure, GCP) and auto-builds VPN tunnels from those cloud networks into Cloudflare WAN to interconnect clouds, offices, and data centers.

**Replaces:** Hand-stitching multi-cloud connectivity: AWS Transit Gateway + Azure Virtual WAN + GCP Network Connectivity Center, manual cross-cloud VPN/peering, and the Terraform sprawl to wire VPCs together — plus the cloud egress/transit bills that come with it.

**Use it via:** Cloudflare One dashboard (Multi-Cloud Networking), connected to cloud accounts via provider credentials/roles for discovery and tunnel creation; builds onto Cloudflare WAN. REST API/Terraform surface exists under the Magic networking APIs but the docs index is thin — verify exact endpoints. Closed beta, Enterprise-only.

**Capabilities:**
- Cloud resource discovery: enumerates VPCs, subnets, VMs, route tables, and routes across AWS, GCP, and Azure from the Cloudflare dashboard
- Cloud on-ramps: automatically builds VPN tunnels between cloud networks and Cloudflare WAN (auto-generated Magic WAN on-ramps)
- Unifies cloud networks with office/data-center networks into one Cloudflare-managed topology
- Manages cloud connections and routing centrally

**Detection signals — the lens fires on these:**
- Multi-cloud footprint: code/IaC touching two or more of AWS, Azure, GCP at once
- Cross-cloud connectivity primitives: AWS Transit Gateway, Azure Virtual WAN / VNet peering, GCP Network Connectivity Center, Megaport, Aviatrix
- Terraform/CloudFormation/Bicep modules creating VPC peering, site-to-site VPNs, or transit gateways between clouds
- Cloud egress/inter-region transfer cost complaints; data-transfer line items in cloud bills
- A central 'network hub' VPC pattern that all clouds route through

**Ideas:**
- Use Multi-Cloud Networking to auto-discover the AWS and Azure VPCs and build tunnels into Cloudflare WAN, replacing a hand-built Transit Gateway + Azure VWAN interconnect
- Connect a GCP VPC into the same Cloudflare WAN backbone as the offices so internal services are reachable cross-cloud without per-cloud VPN plumbing
- Centralize multi-cloud route management in Cloudflare instead of maintaining separate route tables per provider

**Pairs with:** Cloudflare WAN, Cloudflare Network Firewall, Cloudflare One

**Pricing:** Closed beta, limited to Enterprise customers; no public pricing. (verify — drifts)

**Limits:**
- Closed beta, Enterprise-only — not generally available; capabilities and APIs may change
- Depends on Cloudflare WAN as the backbone — it generates on-ramps into WAN, it is not standalone
- Requires granting Cloudflare credentials/roles into your AWS/Azure/GCP accounts for discovery and tunnel creation (trust + blast-radius consideration)
- Docs index is sparse (6 pages); IaC-generation / Terraform-export behavior is not documented — unverified

**Notes:** Renamed from Magic Cloud Networking. Only a handful of doc pages exist and it's a closed beta, so confidence is medium and several specifics (exact API, whether it emits IaC, full provider feature parity) could not be verified this run. Strong eventual lock-in since your cross-cloud backbone would run through Cloudflare WAN. Only relevant to genuine multi-cloud enterprises — irrelevant to single-cloud or serverless shops.

**Docs:** https://developers.cloudflare.com/multi-cloud-networking/llms.txt, https://developers.cloudflare.com/multi-cloud-networking/index.md, https://developers.cloudflare.com/multi-cloud-networking/cloud-on-ramps/index.md

---

## Network & Protocol Settings (zone toggles)
`network-protocol-settings` · Network / Edge config · confidence: `high` · lock-in: `portable`

**Is:** Zone-level toggles that turn on modern transport and protocol support — HTTP/2, HTTP/3 (QUIC), gRPC, WebSockets, IPv6, Onion Routing — at Cloudflare's edge instead of in your own server/LB config.

**Replaces:** Hand-tuning protocol support on nginx/HAProxy/Envoy or your cloud load balancer: nginx `listen 443 ssl http2`, ALPN/QUIC builds, `grpc_pass`, `proxy_set_header Upgrade` WebSocket plumbing, dual-stack AAAA/IPv6 listeners, and bespoke Tor handling.

**Use it via:** Dashboard: Network page for WebSockets, gRPC, IPv6 Compatibility, Onion Routing toggles; Speed > Settings > Protocol Optimization for HTTP/2, HTTP/3 (QUIC), 0-RTT, HTTP/2 to Origin. Zone Settings API: PATCH the zone setting by name — confirmed `http2`, `ipv6` (set value `"off"` to disable), `websockets` (value `"on"`), `opportunistic_onion` (value `"on"`); HTTP/3 and 0-RTT are toggled the same way (settings typically `http3` / `0rtt`). Terraform: `cloudflare_zone_settings_override` / per-setting resources.

**Capabilities:**
- HTTP/2: terminated at Cloudflare's edge, enabled by default for all plans (requires an SSL cert at the edge); API setting `http2`.
- HTTP/3 (QUIC): accept inbound requests over HTTP/3; toggled in dashboard Speed > Settings > Protocol Optimization (zone setting, typically `http3`).
- gRPC: 'Protect your APIs on any proxied gRPC endpoints' — edge support for gRPC over HTTP/2, reducing bandwidth/latency (Network > gRPC toggle).
- WebSockets: proxy WebSocket connections through Cloudflare with no extra setup; API setting `websockets`; only the initial upgrade counts as an HTTP request.
- IPv6 Compatibility: auto-generates AAAA records so IPv6 clients can reach an IPv4 origin; on by default; API setting `ipv6` (Pseudo IPv4 available for IPv4-only origins).
- Onion Routing: serve content directly over the Tor network without exit nodes, send an alt-svc header pointing Tor Browser to a `.onion`, and distinguish human Tor users from malicious bots; API setting `opportunistic_onion`.
- Related Protocol Optimization toggles: 0-RTT Connection Resumption, HTTP/2 to Origin, Enhanced HTTP/2 Prioritization.

**Detection signals — the lens fires on these:**
- nginx `listen 443 ssl http2;` / `listen 443 quic reuseport;` / `http3 on;`, or a custom-built nginx/Caddy for QUIC support.
- nginx `grpc_pass` / `grpc_set_header`, or an Envoy/HAProxy config dedicated to gRPC fronting.
- WebSocket reverse-proxy boilerplate: `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";` and connection-upgrade maps.
- Dual-stack listener config / explicit AAAA record management / IPv6 socket handling at the origin.
- Bespoke Tor/.onion handling, exit-node allowlists, or a separate hidden-service deployment.
- Cert/ALPN wrangling to advertise HTTP/2 over ALPN at the origin LB.

**Ideas:**
- Your nginx config hand-enables `http2` and a custom `quic`/`http3` build — if the zone is proxied through Cloudflare, flip the HTTP/2 and HTTP/3 toggles (Speed > Protocol Optimization) and let the edge terminate them.
- You maintain `grpc_pass` plumbing on nginx to front a gRPC service — enable Cloudflare's gRPC toggle (endpoint on 443, TLS + HTTP/2 over ALPN) and get WAF/edge in front of it.
- You run a separate Tor hidden service for .onion users — enable Onion Routing (`opportunistic_onion`) to serve the same site over Tor without exit nodes.
- You manually manage AAAA records / dual-stack listeners for IPv6 — IPv6 Compatibility (`ipv6`) is on by default and auto-generates AAAA so IPv4-only origins still serve v6 clients.

**Pairs with:** SSL/TLS (edge certificates), WAF, Bot Management, Spectrum, Load Balancing, Pseudo IPv4

**Pricing:** All of these toggles are available across Free, Pro, Business, and Enterprise (HTTP/2, gRPC, WebSockets, IPv6, Onion Routing all list Free–Enterprise availability). Some add-on products invoked by traffic (WAF, Bot Management) bill separately; Enterprise gets extra customization (e.g. WebSocket idle timeout, IPv6 setting control). (verify — drifts.)

**Limits:**
- HTTP/2: Free-plan domains cannot disable it; Pro+ can customize.
- HTTP/2 / HTTP/3 require an SSL certificate at Cloudflare's edge; HTTP/3 needs HTTP/2 prerequisites in place.
- gRPC requires endpoint on port 443, TLS + HTTP/2 advertised over ALPN, `application/grpc` content-type, proxied hostname, and at least Full SSL/TLS mode; WAF only inspects gRPC headers at connection phase (not stream content), and Cloudflare Access does not support gRPC through the reverse proxy.
- WebSockets: idle/no-data connections are terminated (custom timeout is Enterprise-only); only Cloudflare→client bytes count toward bandwidth; use session affinity behind Load Balancing.
- Onion Routing: Cloudflare does not issue certs for the `.onion` domain, so it cannot be served over HTTPS.
- IPv6: even when disabled the zone may still receive IPv6 traffic via other routes (e.g. Tor); only Enterprise can fully customize the setting.

**Notes:** These only help when the hostname is proxied (orange-cloud) through Cloudflare — they are edge-termination/optimization toggles, not origin changes, so your origin can keep speaking HTTP/1.1 plain. Lock-in is minimal (they're standard protocols), but the convenience disappears if you go DNS-only/grey-cloud. API setting name `http2` is confirmed verbatim; `ipv6`, `websockets`, `opportunistic_onion` are confirmed; `http3`/`0rtt` are the conventional Zone-Settings names but were not quoted verbatim in the pages fetched — verify against the Zone Settings API reference. HTTP/3 and gRPC live in different dashboard areas (Speed > Protocol Optimization vs Network) than the other Network toggles.

**Docs:** https://developers.cloudflare.com/network/, https://developers.cloudflare.com/network/grpc-connections/, https://developers.cloudflare.com/network/websockets/, https://developers.cloudflare.com/network/ipv6-compatibility/, https://developers.cloudflare.com/network/onion-routing/, https://developers.cloudflare.com/speed/optimization/protocol/http2/

---

## Privacy Gateway
`cloudflare-privacy-gateway` · Privacy / Networking (OHTTP) · confidence: `high` · lock-in: `portable`

**Is:** A managed Oblivious HTTP (OHTTP) relay run by Cloudflare that strips the client IP from requests before they reach your application backend, so your server never sees who sent what.

**Replaces:** Building your own OHTTP/mixnet relay tier, or trusting a single proxy you operate to 'promise' it won't link IPs to payloads; the DIY 'we anonymize telemetry' stack where one server still sees both identity and data.

**Use it via:** Route client OHTTP requests through https://privacy-relay.cloudflare.com/<GATEWAY_SERVER_NAME>. You deploy a gateway server (Go/Rust/JS gateway library) that decrypts OHTTP, publishes its HPKE key config, and forwards inner requests; register your gateway URL with Cloudflare to enable the relay. No simple Worker binding — it is a relay+gateway protocol integration.

**Capabilities:**
- Cloudflare operates the OHTTP relay; you operate an application gateway that decrypts inner requests and forwards them
- Cryptographically separates who (IP, seen only by the relay) from what (payload, seen only by your gateway) — neither party sees both
- Relay sees only encrypted message length and the destination gateway, not request content
- Implements the IETF Oblivious HTTP standard (HPKE-encrypted request/response encapsulation)
- Gateway libraries provided for Go, Rust, and JavaScript/TypeScript; sample gateway server in Go
- Client encrypts to the gateway's published HPKE public key config, sends via the Cloudflare relay URL
- Metrics available for relay traffic

**Detection signals — the lens fires on these:**
- Telemetry / crash-report / analytics ingestion endpoints that receive client IPs you would rather not log
- Code stripping or hashing client IPs server-side to 'anonymize' (you still received the IP — too late)
- App-config / safe-browsing / certificate-check style lookups where the query is sensitive but the response is generic
- Existing single-hop proxy you run and document as 'privacy-preserving'
- Privacy-policy commitments about 'we cannot link your identity to your usage' enforced only by trust, not crypto
- HPKE / OHTTP / 'oblivious' references in code or design docs

**Ideas:**
- Move privacy-sensitive telemetry or crash reports behind an OHTTP gateway so your backend literally cannot see the sender's IP.
- Use it for safe-browsing / breach-check / config-fetch lookups where the request reveals user intent but the response is the same for everyone.
- Replace a 'we promise not to correlate' single-proxy design with cryptographic IP/payload separation to back a stronger privacy claim.

**Pairs with:** Privacy Proxy (sibling privacy-edge product), Workers (could host the gateway logic), Privacy Pass

**Pricing:** Not publicly listed; closed beta, access via Cloudflare account team (verify — drifts).

**Limits:**
- Closed beta / select privacy-oriented partners — not self-serve; contact Cloudflare to onboard
- OHTTP suits stateless, transactional request/response (telemetry, lookups) — not interactive sessions, streaming, or anything needing cookies/long-lived identity
- Cloudflare cannot prevent destination services from sending identifying data in the payload itself — you must scrub PII client-side
- You still must build and run the gateway server

**Notes:** Relay/gateway split, the privacy-relay.cloudflare.com/<gateway> routing, OHTTP/HPKE basis, and the Go/Rust/JS gateway libraries are verified. Exact request-size/method limits were NOT on the limitations page fetched (it only stressed the 'payload may still leak PII' caveat) — leave specific size caps unverified. Strong lock-in to Cloudflare as the relay operator; that is somewhat the point (you want a relay you do not also operate). Wrong tool for interactive or authenticated sessions.

**Docs:** https://developers.cloudflare.com/privacy-gateway/llms.txt, https://developers.cloudflare.com/privacy-gateway/index.md, https://developers.cloudflare.com/privacy-gateway/get-started/index.md, https://developers.cloudflare.com/privacy-gateway/reference/limitations/index.md

---

## Privacy Proxy
`cloudflare-privacy-proxy` · Privacy / Networking (MASQUE) · confidence: `high` · lock-in: `portable`

**Is:** A managed MASQUE-based forward proxy on Cloudflare's network that hides a client's real IP from destination servers while preserving approximate geolocation — the infrastructure behind services like iCloud Private Relay's second hop and Microsoft Edge Secure Network.

**Replaces:** Operating your own VPN/proxy egress fleet (WireGuard/OpenVPN boxes, SOCKS gateways, rotating egress IPs) to give an app population private, geo-accurate connectivity; paying a consumer-VPN-as-infrastructure vendor.

**Use it via:** Network service, not an SDK. Clients (HTTP/2 or HTTP/3 capable) connect to a provisioned proxy endpoint and send Proxy-Authorization: Preshared <PSK> (or Privacy Pass). curl: --proxy <endpoint> --proxy-header 'Proxy-Authorization: ...'. Chaussette exposes a local SOCKS5 front. GraphQL Analytics + OpenTelemetry for metrics. Onboarding provides endpoint URL, PSK, and egress IP ranges.

**Capabilities:**
- Forward proxy over MASQUE using HTTP CONNECT (TCP) and CONNECT-UDP (UDP/QUIC) on HTTP/2 and HTTP/3
- Separates identity from activity: auth service knows the user, destination sees only a Cloudflare egress IP, proxy never links requests to users
- Geolocation-aware egress IP selection so destinations still see a plausible region (preserves geo-accuracy unlike a naive VPN)
- Encrypted tunnels; proxy sees only destination host+port, not content
- Auth via Proxy-Authorization header — pre-shared key (PSK) for PoC, Privacy Pass tokens for production
- Chaussette local SOCKS5 helper to bridge clients that can't send proxy auth headers natively
- Powers iCloud Private Relay (egress hop) and Microsoft Edge Secure Network

**Detection signals — the lens fires on these:**
- Self-managed VPN/egress fleet: WireGuard/OpenVPN configs, wg-quick, rotating egress IP pools, a 'proxy region' selector
- SOCKS5/HTTP forward-proxy infrastructure your app routes user traffic through for IP masking
- Consumer-VPN or residential-proxy vendor SDKs/credentials in the codebase
- Browser/app feature that 'hides your IP' or 'secure network' built on hand-run exit nodes
- Need for geo-accurate egress (locale-correct results) that a single-region VPN breaks
- MASQUE / CONNECT-UDP / Privacy Pass references; Proxy-Authorization handling

**Ideas:**
- Replace a self-run WireGuard egress fleet with Privacy Proxy to give your app an IP-masking 'secure network' feature without operating exit nodes.
- Add a privacy mode to a browser/mobile app via MASQUE so destinations see a Cloudflare egress IP but still get the right region.
- Use CONNECT-UDP to privacy-proxy QUIC/real-time traffic that a TCP-only SOCKS proxy can't carry.

**Pairs with:** Privacy Gateway (sibling OHTTP product), Privacy Pass (production auth tokens), WARP (related but distinct client)

**Pricing:** Available as a managed service for Enterprise customers; pricing not published — contact Cloudflare (verify — drifts).

**Limits:**
- Enterprise-only managed service; access via Cloudflare sales, configuration handed to you (not self-serve)
- It is plumbing — you bring the client/app integration that speaks MASQUE and presents credentials
- PSK auth is for PoC; production needs Privacy Pass setup
- Not the WARP consumer client and not a developer SDK you embed

**Notes:** MASQUE/CONNECT-UDP basis, identity-activity separation, Proxy-Authorization PSK→Privacy Pass path, Chaussette SOCKS5 helper, geolocation-preserving egress, and the iCloud Private Relay / Edge Secure Network customers are all verified from fetched pages. Enterprise-gated, so not relevant to small projects. Distinct from WARP — don't conflate. Lock-in is to Cloudflare's egress network; trade-off vs running your own fleet is operational burden for vendor dependence.

**Docs:** https://developers.cloudflare.com/privacy-proxy/llms.txt, https://developers.cloudflare.com/privacy-proxy/index.md, https://developers.cloudflare.com/privacy-proxy/concepts/how-it-works/index.md, https://developers.cloudflare.com/privacy-proxy/get-started/index.md

---

## Workers VPC
`workers-vpc` · Networking / Private connectivity · confidence: `high` · lock-in: `portable`

**Is:** Lets a Cloudflare Worker reach into private resources (databases, internal APIs, services) inside your AWS/GCP/Azure/on-prem network over a Cloudflare Tunnel, exposed to the Worker as a binding.

**Replaces:** The DIY 'let my edge function reach my private VPC' stack: public API gateway/ALB or bastion+VPN, IP allowlists, and SSRF/auth glue.

**Use it via:** Worker binding. For one fixed target, wrangler.jsonc key: "vpc_services": [{ "binding": "PRIVATE_API", "service_id": "<uuid>", "remote": true }]. For broad private-network reachability, use "vpc_networks": [{ "binding": "PRIVATE_NETWORK", "network_id": "cf1:network", "remote": true }] to reach Cloudflare Mesh nodes, Tunnel routes, and Cloudflare WAN on-ramps. In code: await env.PRIVATE_API.fetch(new Request("http://internal-api.company.local/users")) or env.PRIVATE_NETWORK.fetch("http://10.50.0.100:8080/api") (absolute URL controls destination). Provision VPC Services via `npx wrangler vpc service create my-private-api --type http --tunnel-id <id> --hostname <host>` or TCP examples; Tunnel side runs cloudflared. For DBs, pair with Hyperdrive binding (env.HYPERDRIVE.connectionString).

**Capabilities:**
- Worker -> private service connectivity for resources NOT on the public Internet (AWS, Azure, GCP, on-premise, others)
- VPC Service binding: configure one VPC Service per private endpoint; call it from the Worker via env.BINDING.fetch(request)
- Two service types: HTTP (fetch() to private HTTP/HTTPS endpoints) and TCP (e.g. PostgreSQL :5432, MySQL, with optional --app-protocol metadata)
- VPC Networks binding for broader access to private infra reachable via Cloudflare Tunnel/Mesh and WAN on-ramps (vs one-service-at-a-time VPC Services)
- Private databases: layer Hyperdrive on top of a TCP VPC Service for pooling + query acceleration (Postgres example uses node-postgres)
- Traffic can flow through Cloudflare Gateway so existing Zero Trust traffic policies and logs apply to Worker requests
- Connectivity established by Cloudflare Tunnel using the cloudflared connector from your private network outbound to Cloudflare (no inbound ports opened)
- Terraform-manageable VPC Services

**Detection signals — the lens fires on these:**
- A Worker / Pages Function needs data from a resource that lives in a private subnet (RDS/Aurora, Cloud SQL, internal microservice) and currently can't reach it
- Code that calls a public ALB/API-Gateway URL purely to expose an internal service to the edge, guarded by an IP allowlist or shared secret
- Existing cloudflared / Cloudflare Tunnel config (config.yml, `tunnel:` blocks, cloudflared in a Dockerfile or systemd unit) used to reach internal HTTP services
- Bastion host / jump box, VPN (WireGuard, OpenVPN, Tailscale) or SSH tunnel stood up so an external compute layer can reach a private DB
- Tailscale/Headscale/NetBird/ZeroTier/WireGuard mesh glue used mainly so edge compute can reach RFC1918 services
- Workers that need to call multiple private services across Cloudflare Tunnel, Mesh nodes, or Cloudflare WAN on-ramps
- DB connection strings pointing at private/RFC1918 hosts (10.x, 172.16-31.x, 192.168.x, *.internal, *.local, *.rds.amazonaws.com inside a VPC) that a Worker would need
- node-postgres (pg) / mysql2 in a Worker against a non-public database, often already alongside a Hyperdrive binding
- Security-group rules or NAT gateways opened to allow inbound from third-party/edge IP ranges
- wrangler.jsonc already present (Workers project) + a hybrid-cloud architecture where the data plane is private

**Ideas:**
- Expose an internal/legacy HTTP microservice (still living in EC2/on-prem) to a public Worker frontend without putting a load balancer on the public Internet — bind it as an HTTP VPC Service and call env.SVC.fetch().
- Query a private Postgres/MySQL from a Worker by creating a TCP VPC Service to :5432 and fronting it with Hyperdrive for pooling, instead of running a bastion or opening the DB to the world.
- Route Worker-originated calls to internal APIs through Cloudflare Gateway so Zero Trust policies and audit logs cover serverless traffic the same as user traffic.

**Pairs with:** Hyperdrive (connection pooling + acceleration over a TCP VPC Service to a private database), Cloudflare Tunnel / cloudflared (the actual transport from your private network to Cloudflare), Cloudflare Gateway + Zero Trust (apply traffic policies and logging to Worker-originated requests), Cloudflare Mesh / WAN on-ramps (broader private reachability via VPC Networks), Workers / Pages Functions (the compute that consumes the binding)

**Pricing:** Free during open beta to all Workers plans; standard Workers pricing applies for the underlying compute time and requests. A paid Workers plan is required. No separate per-GB/egress fee documented yet, and post-GA pricing for the VPC feature itself is not stated. (verify — drifts; currently beta, APIs and pricing may change before GA)

**Limits:**
- 1000 VPC Services per account
- Standard Workers limits apply for request size, timeout, and subrequests (the VPC fetch counts as a Worker subrequest)
- Beta: features and APIs may change before general availability
- VPC Networks limits and TCP/HTTP-specific numeric constraints not published on the limits page at time of fetch

**Notes:** Cloudflare-specific and beta — this is the inverse of Tunnel's usual job: instead of exposing a private service to the public web, it lets Workers dial into your private network, surfaced as a binding. Use VPC Services for scoped host/port targets; use VPC Networks with `network_id: "cf1:network"` when Workers need broad reach across Mesh, Tunnel routes, or Cloudflare WAN on-ramps. Lock-in: the binding model and `wrangler vpc`/cloudflared setup are Cloudflare-only; your app code calls env.BINDING.fetch() rather than a portable URL. NOT a fit if your services are already public (just fetch them), if you don't run Workers, or if you want a generic site-to-site VPN between your own clouds (that's Magic WAN / Mesh territory, not Workers VPC). You still run and maintain the cloudflared/Mesh/WAN connectors inside your network. Could not verify: post-GA price, per-request/egress unit, VPC Networks-specific limits, and full TCP feature maturity — all marked unknown from the pages fetched this run. Hyperdrive is the recommended path for private DBs; raw TCP service types existed in docs but DB access is framed through Hyperdrive.

**Docs:** https://developers.cloudflare.com/workers-vpc/llms.txt, https://developers.cloudflare.com/workers-vpc/index.md, https://developers.cloudflare.com/workers-vpc/api/index.md, https://developers.cloudflare.com/workers-vpc/get-started/index.md, https://developers.cloudflare.com/workers-vpc/configuration/vpc-services/index.md, https://developers.cloudflare.com/workers-vpc/reference/pricing/index.md, https://developers.cloudflare.com/workers-vpc/reference/limits/index.md, https://developers.cloudflare.com/workers-vpc/examples/private-database/index.md, https://developers.cloudflare.com/workers-vpc/configuration/vpc-networks/index.md, https://developers.cloudflare.com/changelog/post/2026-05-21-vpc-networks-cloudflare-wan/

---
