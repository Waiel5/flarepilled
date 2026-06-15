# Zero Trust & SASE

_12 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Cloudflare Access
`cloudflare-access` · Zero Trust / SASE · confidence: `high` · lock-in: `deep`

**Is:** Identity-aware proxy that gates any web app, SaaS tenant, or SSH/RDP target behind per-request Zero Trust policy — no VPN, no public exposure.

**Replaces:** Stop running a VPN concentrator, bastion/jump hosts, or a self-hosted oauth2-proxy/Pomerium/Teleport in front of internal apps.

**Use it via:** Zero Trust dashboard (Access > Applications + reusable Policies UI); full Cloudflare API under /accounts/{id}/access/apps, /access/policies, /access/service_tokens, /access/identity_providers; Terraform cloudflare_zero_trust_access_application / _access_policy / _access_service_token resources. Apps are typically fronted by a Cloudflare Tunnel (cloudflared) rather than a binding/wrangler.

**Capabilities:**
- Application types: self-hosted web apps (incl. Workers), SaaS apps via SAML or OIDC federation, private/non-HTTP network destinations, and infrastructure apps (SSH/RDP) with protocol-aware authorization
- Infrastructure access issues short-lived certificates and controls ports/usernames/commands, eliminating long-lived SSH keys
- Up to 50 identity providers per account; combine multiple IdPs and require specific ones per app
- Reusable Access policies (allow/block/bypass) evaluating identity, group, device posture, country, IP, mTLS cert, and more
- Service tokens (CF-Access-Client-Id / CF-Access-Client-Secret headers) and mTLS client certs for machine-to-machine / automation auth
- Device posture signals (WARP client, OS version, disk encryption, third-party EDR) as policy conditions
- App Launcher portal plus Bookmarks for visibility-only links; event subscriptions for audit logging
- Authenticate coding agents / AI controls as first-class policy targets

**Detection signals — the lens fires on these:**
- oauth2-proxy / Pomerium / Authelia / Teleport in docker-compose or k8s manifests sitting in front of an internal app
- nginx auth_request directives, basic-auth .htpasswd files, or hand-rolled JWT-cookie middleware guarding a dashboard
- OpenVPN/WireGuard/IPsec configs (client.ovpn, wg0.conf) used purely to reach internal web apps
- A bastion/jump host (jumpbox, ProxyJump in ~/.ssh/config) and long-lived authorized_keys distribution
- App env vars like OIDC_CLIENT_ID/SAML_METADATA_URL wired into per-app SSO plumbing repeated across services

**Ideas:**
- Replace the oauth2-proxy + nginx auth_request layer guarding our Grafana with a Cloudflare Access self-hosted app behind a Tunnel.
- Issue short-lived SSH access to prod via an Access infrastructure application instead of distributing authorized_keys.
- Gate our internal admin Worker with an Access policy requiring Okta group membership plus a WARP-enrolled device.

**Pairs with:** cloudflare-tunnel, cloudflare-gateway, cloudflare-browser-isolation, warp-device-posture

**Pricing:** Free Zero Trust plan covers up to 50 users; beyond that Pay-as-you-go/Contract per-seat. SaaS + self-hosted app gating included on Free tier (verify — drifts).

**Limits:**
- 500 applications, 500 reusable policies, 50 identity providers per account
- 1,000 rules per application; 1,000 email addresses and 1,000 IP addresses per rule
- Self-hosted web app gating needs the origin reachable by Cloudflare (Tunnel or proxied DNS); not a fit for thick-client/native protocols beyond the supported SSH/RDP infra paths
- Browser-rendered SSH/RDP/VNC sessions require Browser Isolation seats

**Notes:** Lock-in is moderate: policies and IdP wiring are CF-specific, but apps stay on your origin so exit is mostly reconfiguration. Not an IdP itself — it federates your existing Okta/Entra/Google. For pure SaaS SSO it is an SP/federation layer, not a replacement for the IdP. Infra (SSH/RDP) access is the strongest VPN-killer; deep non-HTTP L4 reachability is Gateway/WARP territory, not Access.

**Docs:** https://developers.cloudflare.com/cloudflare-one/access-controls/index.md, https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/index.md, https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/index.md, https://developers.cloudflare.com/cloudflare-one/account-limits/index.md

---

## Cloudflare Browser Isolation
`cloudflare-browser-isolation` · Zero Trust / SASE · confidence: `high` · lock-in: `sticky`

**Is:** Remote Browser Isolation that runs risky web sessions in Cloudflare's network and streams a safe vector representation to the user, with copy/paste/download/upload/keyboard controls.

**Replaces:** Stop running Menlo / Ericom / Symantec Web Isolation, or maintaining disposable-VDI / Kasm browser fleets, for risky-site and untrusted-link browsing.

**Use it via:** Configured as optional settings inside the Gateway HTTP policy builder when the Isolate action is selected (no separate isolation API object for the controls); clientless mode is enabled in Zero Trust settings ('Allow users to open a remote browser without the device client'). Same Gateway rules API/Terraform surface as Gateway policies. No wrangler/binding.

**Capabilities:**
- Executes page JavaScript/plugins in a remote browser in Cloudflare's edge; user device renders a streamed representation (Network Vector Rendering), protecting against drive-by/zero-day web threats
- Triggered by Gateway HTTP policy Isolate action, or by category/risk (e.g. isolate uncategorized or security-risk domains)
- Clientless / link-based isolation: wrap any URL via https://<team-name>.cloudflareaccess.com/browser/<URL> — no device client needed, ideal for third-party/unmanaged users
- Data-protection controls in the Isolate policy: Copy and Paste (allow / only-within-isolated / disallow), File downloads (allow / disallow / view-in-remote-browser), File uploads (allow/disallow), Keyboard (allow/disallow), Printing (allow/disallow)
- Isolate Access applications so internal apps render in a remote browser for high-risk or BYOD users
- Connection modes: Traffic+DNS (WARP), Access, Gateway proxy endpoint, Cloudflare WAN (GRE/IPsec), and Clientless prefixed-URL
- Sessions auto-delete when the browser closes; integrates with Email Security to open suspicious links in isolation

**Detection signals — the lens fires on these:**
- Kasm Workspaces / Apache Guacamole / Selenium-grid 'disposable browser' deployments for safe browsing
- A fleet of throwaway VMs or containers spun up per-session just to open untrusted links
- Menlo/Ericom/Symantec Web Isolation agents or PAC entries in endpoint config
- Internal 'open this link safely' tooling that screenshots or proxies URLs through a sandbox VM
- Helpdesk runbooks instructing analysts to open suspicious URLs only inside an isolated VM

**Ideas:**
- Add a Gateway Isolate policy that opens all uncategorized and security-risk domains in a remote browser with downloads disabled.
- Give external contractors clientless browser-isolation links to our internal app instead of provisioning Kasm sessions.
- Retire our per-session disposable-browser VMs by isolating high-risk categories at the Gateway HTTP layer.

**Pairs with:** cloudflare-gateway, cloudflare-access, cloudflare-email-security, cloudflare-dlp

**Pricing:** Add-on to Zero Trust Pay-as-you-go and Enterprise plans; consumes per-seat Browser Isolation (RBI) licenses (verify — drifts).

**Limits:**
- Requires RBI seats assigned; inline (non-clientless) isolation depends on Gateway/WARP being deployed
- Data-protection controls (copy/paste/download/upload/keyboard/print) live only within the Isolate HTTP policy, so they require HTTP inspection + the root CA
- Latency/UX overhead versus local browsing; some heavy web apps degrade
- Clientless prefixed-URL mode is per-link/hostname, not a transparent whole-session proxy

**Notes:** Almost never deployed standalone — it is an action surfaced by Gateway/Access/Email Security. If a codebase has Gateway but no isolation, untrusted-link handling is the gap to flag. Not a fit when sub-50ms interactivity or full native-browser fidelity is required. Lock-in is low since it is policy-driven, but the data-protection controls assume CF's TLS-decrypting proxy is already in path.

**Docs:** https://developers.cloudflare.com/cloudflare-one/remote-browser-isolation/index.md, https://developers.cloudflare.com/cloudflare-one/remote-browser-isolation/setup/index.md, https://developers.cloudflare.com/cloudflare-one/remote-browser-isolation/isolation-policies/index.md

---

## Cloudflare CASB
`cloudflare-casb` · Zero Trust / SASE · confidence: `high` · lock-in: `sticky`

**Is:** API-based (out-of-band) Cloud Access Security Broker that connects to SaaS/cloud tenants and scans for misconfigurations, risky sharing, shadow IT, and data-exposure findings after login.

**Replaces:** Stop paying for Netskope SaaS Security Posture / Microsoft Defender for Cloud Apps just to audit SaaS misconfigurations and oversharing.

**Use it via:** Zero Trust dashboard (CASB / Cloud & SaaS integrations) with guided OAuth connection per SaaS app; findings managed in the dashboard and exportable via webhooks. Configuration is integration-driven (connect tenant), not code/binding/wrangler. Findings are also reachable through the Cloudflare API CASB endpoints.

**Capabilities:**
- Connects to SaaS and cloud APIs read-only (least-privilege OAuth) to find post-authentication security issues — no inline proxy required
- Detects misconfigurations (overly permissive sharing), unauthorized user activity, shadow IT, and other data-security issues
- Surfaces discrete 'findings' per integration that can be reviewed, triaged, and managed in the dashboard
- Combines with DLP to scan files inside connected SaaS apps for sensitive data (CASB+DLP)
- Export of posture finding instances via webhooks for SIEM/ticketing workflows
- Step-by-step in-dashboard OAuth integration setup per provider

**Detection signals — the lens fires on these:**
- Home-grown scripts hitting Google Workspace Admin SDK / Microsoft Graph / Slack / GitHub org APIs to audit sharing and permissions
- Scheduled jobs pulling Drive/SharePoint public-link reports or 'who has access' exports into a spreadsheet
- A separate SSPM/CASB vendor agent or API connector (Netskope, Defender for Cloud Apps) in the SaaS admin console
- Manual quarterly access-review runbooks for SaaS tenants instead of continuous scanning
- Custom GitHub Actions / cron checking for public repos, exposed secrets, or org-member misconfig

**Ideas:**
- Connect Google Workspace and GitHub to Cloudflare CASB and replace our custom oversharing-audit scripts with managed findings.
- Use CASB+DLP to flag files shared publicly in our SaaS tenants that contain credit-card or SSN data.
- Wire CASB finding webhooks into our SIEM so misconfig detections open tickets automatically.

**Pairs with:** cloudflare-dlp, cloudflare-gateway, cloudflare-access

**Pricing:** Free users can configure up to two CASB integrations; you must upgrade to an Enterprise plan to view the details of a finding instance (verify — drifts).

**Limits:**
- Free tier capped at 2 integrations and cannot view finding details (Enterprise required)
- Out-of-band only — it audits/posture-checks, it does not inline-block SaaS sessions (that is Gateway's job)
- Coverage is limited to supported SaaS/cloud integrations; verify your specific apps are supported in-dashboard before assuming parity
- Account-limits page does not publish a CASB integration ceiling for paid tiers

**Notes:** Honest caveat: the docs index page does not enumerate the exact supported-integration list (Google Workspace, Microsoft 365, Salesforce, GitHub, Slack, Box, Dropbox, AWS are commonly cited but were not verbatim-confirmed on the fetched pages) — confirm the live integrations catalog in-dashboard. This is posture/SSPM, not inline CASB; for inline tenant control and DLP-on-the-wire use Gateway. Strongest value is continuous misconfig detection replacing manual access reviews.

**Docs:** https://developers.cloudflare.com/cloudflare-one/cloud-and-saas-findings/index.md, https://developers.cloudflare.com/cloudflare-one/cloud-and-saas-findings/casb-dlp/index.md, https://developers.cloudflare.com/cloudflare-one/account-limits/index.md

---

## Cloudflare DLP
`cloudflare-dlp` · Zero Trust / SASE · confidence: `high` · lock-in: `sticky`

**Is:** Data Loss Prevention that detects sensitive data (PII, financial, credentials) in proxied HTTP traffic, SaaS files, and AI prompts, enforced inline through Gateway policies.

**Replaces:** Stop licensing Symantec / Forcepoint / Microsoft Purview DLP to catch sensitive data leaving over the web.

**Use it via:** Zero Trust dashboard DLP Profiles + detection entries; applied via the DLP Profile selector inside Gateway HTTP policies. Cloudflare API /accounts/{id}/dlp/profiles + /dlp/datasets; Terraform cloudflare_zero_trust_dlp_profile. Detection runs in the Gateway data path — no app-side binding/wrangler.

**Capabilities:**
- Scans HTTP body content (uploads/downloads, messages, forms), SaaS application files (via CASB), and AI prompts/responses (via AI Gateway) for sensitive data
- Predefined profiles for financial information and SSN/tax-identifier numbers, plus broader predefined detection entries
- Custom detection: profiles, regex custom entries, and exact-data-match / dataset uploads (datasets up to ~1,000,000 cells/account)
- Optical Character Recognition (OCR) to detect sensitive data inside images
- Supports text, CSV, Microsoft Office (2007+), PDF, and ZIP file formats
- Payload logging stores an encrypted copy of matched content for review
- Enforced inline by selecting a DLP Profile in a Gateway HTTP policy (block/allow/log on match)

**Detection signals — the lens fires on these:**
- Regex sweeps for SSNs/credit cards (e.g. \d{3}-\d{2}-\d{4}, Luhn checks) baked into app middleware or a logging pipeline
- git-secrets / truffleHog / detect-secrets / gitleaks wired in to catch credentials in outbound content
- A commercial DLP agent (Symantec/Forcepoint/Purview) endpoint or ICAP server in the egress path
- Custom 'redact PII before it leaves' code in proxies or API gateways, or homemade EDM fingerprint matching
- Manual processes reviewing uploads for sensitive data, or ad-hoc OCR scripts on screenshots

**Ideas:**
- Add a Gateway HTTP policy with a DLP profile that blocks uploads containing credit-card numbers to non-sanctioned apps.
- Replace our regex-based PII scrubber with a Cloudflare DLP custom profile plus exact-data-match dataset.
- Inspect AI prompts through AI Gateway with a DLP profile so source code and secrets can't be pasted into external LLMs.

**Pairs with:** cloudflare-gateway, cloudflare-casb, cloudflare-ai-gateway, cloudflare-email-security

**Pricing:** Available as an add-on to Zero Trust Enterprise plans; Free/Pay-as-you-go users get limited predefined profiles and payload-logging features (verify — drifts).

**Limits:**
- 25 custom entries; 1,000 custom wordlist keywords per account; ~1,000,000 dataset cells per account
- Inline web DLP requires Gateway HTTP inspection (TLS decryption + root CA) to see content
- Full custom/EDM detection and rich profiles are Enterprise-gated
- Header content is excluded from scanning; only HTTP body is inspected on the wire

**Notes:** DLP is a detection engine, not a standalone product — it only acts where it is wired in: Gateway (web), CASB (SaaS at rest), AI Gateway (prompts), Email Security (outbound). Flag a codebase that has Gateway TLS inspection but no DLP profiles. Lock-in is low (profiles are portable concepts) but EDM datasets and payload logging create CF-side state. Not endpoint DLP — it does not watch local USB/clipboard off-network.

**Docs:** https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/index.md, https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/dlp-profiles/index.md, https://developers.cloudflare.com/cloudflare-one/account-limits/index.md

---

## Cloudflare Email Security
`cloudflare-email-security` · Zero Trust / SASE · confidence: `high` · lock-in: `sticky`

**Is:** Cloud email security (formerly Area 1) that analyzes every inbound message with AI + threat intel to stop phishing, BEC, vendor fraud, malware, and spam — deployable inline or via API.

**Replaces:** Stop paying for Proofpoint / Mimecast / Abnormal / Microsoft Defender for O365 as your inbound anti-phishing and BEC layer.

**Use it via:** Cloudflare One dashboard (Email Security: Investigation, Settings > Detection/Link Actions, allow/block policies, impersonation registry). Deployment via Microsoft Graph / Google Workspace API authorization, MX-record edits / mail connector (inline), or BCC/Journal rules. Cloudflare Email Security API for submissions and configuration. Distinct from outbound Email Service (sending) and from DMARC Management.

**Capabilities:**
- Analyzes every incoming email for phishing, Business Email Compromise (executive/authority impersonation), vendor email fraud, malware, and spam using AI, threat intelligence, and security rules
- API deployment (post-delivery) with Microsoft 365 (Microsoft Graph) and Google Workspace — no MX change, auto-moves malicious mail out of every inbox when disposition upgrades
- Inline / MX deployment (pre-delivery) for highest protection: blocks before inbox, supports link rewrite, text/banner add-ons, and move actions at delivery
- BCC / Journaling deployment (Google BCC rules, Microsoft Exchange Journal Rules) for post-delivery analysis
- Email Link Isolation: rewrite suspicious links (or all links of a chosen disposition) to open in a clientless remote browser via Browser Isolation
- Investigation tooling: search/reclassify messages, open links safely in Browser Isolation or Security Center, manage allow policies, blocked senders, trusted domains, and an impersonation registry
- Phishing submission and retroactive remediation (auto-move/clawback) of delivered threats

**Detection signals — the lens fires on these:**
- Existing Proofpoint/Mimecast/Abnormal connectors, or Microsoft Defender for O365 Safe Links/Safe Attachments policies
- Hand-built mail rules that quarantine on SPF/DKIM/DMARC failure as the primary anti-phishing control
- Custom journaling/BCC pipelines feeding a homemade phishing-analysis service or a SOAR playbook
- Transport rules doing display-name/impersonation string matching for exec names
- A 'report phish' add-in feeding a manual triage mailbox instead of automated disposition + clawback

**Ideas:**
- Connect Microsoft 365 to Cloudflare Email Security via API so malicious mail is auto-moved post-delivery without changing MX.
- Deploy inline (MX) Email Security and rewrite suspicious links to open in Browser Isolation instead of relying on Defender Safe Links.
- Replace our journaling-to-custom-analyzer pipeline with Email Security BCC/Journaling deployment and the impersonation registry.

**Pairs with:** cloudflare-browser-isolation, cloudflare-dlp, cloudflare-area1-security-center, cloudflare-dmarc-management

**Pricing:** Sold in packages — Advantage, Enterprise, and Enterprise + PhishGuard; feature availability (e.g. expanded link isolation = Enterprise/PhishGuard) varies by package (verify — drifts).

**Limits:**
- Link rewrite / text add-ons / pre-delivery blocking require Inline (MX) deployment; API and BCC/Journaling modes are post-delivery and remediate mainly via move/delete
- Email Link Isolation requires Browser Isolation (RBI) seats and the clientless-browser setting enabled
- API auto-move needs Graph/Google read-write authorization; some actions only fire if an integration is associated
- Inbound only — does not cover outbound transactional sending (Email Service) or DMARC reporting/enforcement (DMARC Management)

**Notes:** Explicitly the INBOUND product — do not conflate with Cloudflare Email Service (outbound/transactional) or DMARC Management (auth reporting). Lock-in is low in API mode (revoke OAuth) but inline/MX mode reroutes your mail flow, which is a heavier migration. Strongest pitch is replacing the expensive SEG (Proofpoint/Mimecast) — API mode lets it run alongside Defender as a second layer with near-zero deployment risk.

**Docs:** https://developers.cloudflare.com/cloudflare-one/email-security/index.md, https://developers.cloudflare.com/cloudflare-one/email-security/setup/index.md, https://developers.cloudflare.com/cloudflare-one/email-security/settings/detection-settings/configure-link-actions/, https://developers.cloudflare.com/changelog/post/2025-08-07-expanded-link-isolation/

---

## Cloudflare Gateway
`cloudflare-gateway` · Zero Trust / SASE · confidence: `high` · lock-in: `sticky`

**Is:** Cloud Secure Web Gateway that filters DNS, L4 network, and L7 HTTP egress traffic with TLS decryption, content/security categories, and inline DLP — no on-prem proxy box.

**Replaces:** Stop renting Cisco Umbrella / Zscaler Internet Access / Netskope SWG or self-hosting Squid + pi-hole/Pi-hole + a perimeter firewall for outbound filtering.

**Use it via:** Zero Trust dashboard Gateway rule builder (Selector / Operator / Value with And/Or); Gateway API /accounts/{id}/gateway/rules + /lists + /locations using Wirefilter traffic expressions (e.g. http.request.uri matches "/gaming"); Terraform cloudflare_zero_trust_gateway_policy (provider v5 recommended to avoid precedence conflicts). Onboarding via WARP client, DNS locations (agentless), PAC/proxy endpoints, or IPsec/GRE tunnels (Magic WAN).

**Capabilities:**
- Three policy layers: DNS (block before connection), Network/L4 (TCP/UDP/GRE by IP, port, protocol, SNI), and HTTP/L7 (URL, headers, files) with HTTPS decryption via installed root cert
- DNS actions: Allow, Block (custom block page), Override, Safe Search (Google/Bing/Yandex/YouTube/DuckDuckGo), YouTube Restricted Mode
- HTTP actions: Allow, Block, Redirect, Isolate (hand off to Browser Isolation), Do Not Inspect, Do Not Scan, Quarantine (sandbox detonation)
- Content categories + Security Threats categories (malware, phishing, C2, compromised domain, potentially-unwanted software) for category-based blocking
- Built-in antivirus scanning and file sandboxing; blocks password-protected/unscannable Office/PDF/ZIP files
- Inline DLP via DLP Profile selector on HTTP policies; Application controls and security-risk selectors for shadow-IT and tenant control
- Identity-aware policies (user email, group, SAML attributes) and device-posture selectors when traffic comes from the WARP client
- Dedicated egress IPs and custom resolver policies for source-IP allowlisting at SaaS vendors

**Detection signals — the lens fires on these:**
- squid.conf / Privoxy / e2guardian configs, or a Squid container doing outbound URL filtering
- pi-hole / Pi-hole / AdGuard Home / Unbound blocklists used as the corporate DNS sink
- Umbrella/Zscaler/Netskope PAC files, ZIA tunnels, or umbrella_roaming_client / Zscaler agent in MDM profiles
- Hand-maintained /etc/hosts or RPZ zone files as a domain blocklist; iptables/nftables OUTPUT rules enumerating blocked IPs/ports for egress control
- A proxy.pac referencing an internal gateway host, or HTTP_PROXY/HTTPS_PROXY env vars pointed at an on-prem filtering proxy

**Ideas:**
- Migrate our Squid egress allowlist and pi-hole blocklists into Cloudflare Gateway DNS + HTTP policies routed through WARP.
- Add a Gateway HTTP policy that quarantines executable downloads and blocks password-protected ZIPs for the finance group.
- Replace per-vendor IP allowlisting hacks with a Gateway dedicated egress IP so SaaS providers see one stable source IP.

**Pairs with:** cloudflare-warp, cloudflare-dlp, cloudflare-browser-isolation, cloudflare-access, magic-wan

**Pricing:** DNS filtering available on Free Zero Trust plan; HTTP/Network filtering, AV, and inline DLP scale with Pay-as-you-go/Enterprise seats. Some advanced selectors (DLP, sandbox) are Enterprise/add-on (verify — drifts).

**Limits:**
- 500 DNS + 500 HTTP + 500 Network policies; 250 DNS locations; 100 lists; list entries 1,000 (Standard) / 5,000 (Enterprise) per account
- HTTP inspection requires distributing the Cloudflare root CA to devices; breaks on cert-pinned apps unless added to Do Not Inspect
- Full L4/HTTP enforcement on roaming devices requires the WARP client; agentless DNS-location mode only does DNS-layer filtering
- TLS decryption has privacy/compliance implications and per-app exceptions to manage

**Notes:** Lock-in is low-to-moderate: rules are CF-specific Wirefilter but the data plane is just your egress path. The big operational cost is cert distribution + TLS-decryption exceptions. Network/L4 policies need WARP or a tunnel; do not assume HTTP-policy parity in pure agentless DNS mode. Inbound app protection is WAF/Access, not Gateway — Gateway is egress/forward-proxy only.

**Docs:** https://developers.cloudflare.com/cloudflare-one/traffic-policies/index.md, https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/index.md, https://developers.cloudflare.com/cloudflare-one/traffic-policies/dns-policies/index.md, https://developers.cloudflare.com/cloudflare-one/account-limits/index.md

---

## Cloudflare Network Firewall (formerly Magic Firewall)
`cloudflare-network-firewall` · Network Security / Firewall-as-a-Service · confidence: `high` · lock-in: `portable`

**Is:** A cloud firewall-as-a-service that filters and inspects L3/L4 packets and flows at Cloudflare's edge using Wireshark-style rule expressions, with optional IDS, managed threat-intel rulesets, geo/ASN blocking, and on-demand packet captures.

**Replaces:** On-prem firewall hardware and its ACLs (Palo Alto / Fortinet / Cisco ASA / Juniper SRX appliances) plus a separate IDS/IPS box — moving packet filtering off your data-center edge and onto Cloudflare's network in front of Magic Transit/WAN.

**Use it via:** REST API (Magic Firewall rulesets: /accounts/{id}/rulesets with phase magic_transit / magic_transit_managed), the Magic Firewall dashboard, GraphQL analytics API, Logpush, and Terraform (cloudflare_magic_firewall_ruleset / cloudflare_ruleset). PCAPs configured to a bucket. No Worker binding — it operates on network traffic, not in app code.

**Capabilities:**
- Stateless/flow packet filtering with first-match-wins ruleset logic across a Custom phase (your rules) and a Managed phase (Cloudflare-maintained); actions allow / block / log
- Wireshark-style filter fields: ip.src, ip.dst, ip.proto, ip.len, ip.ttl, tcp.dstport, tcp.flags.syn, udp.dstport, icmp.type, ip.src.country, ip.src.asnum, cf.colo.region (e.g. `ip.proto == "tcp" && tcp.dstport == 443`)
- Advanced plan: managed threat-intel IP lists (Anonymizer, Botnet, Malware, Open Proxies, VPN), geo/ASN block, protocol validation rules (positive security model), IDS (Intrusion Detection), Secure Web Gateway egress filtering (TCP/UDP all ports, RFC1918), on-demand packet captures (PCAPs to an R2/S3 bucket)
- Rule propagation under 60 seconds; analytics via dashboard + GraphQL; Logpush for IDS
- Programmable API with Terraform support

**Detection signals — the lens fires on these:**
- On-prem firewall configs / vendor mentions: Palo Alto PAN-OS, Fortinet FortiGate, Cisco ASA/Firepower, Juniper SRX, pfSense/OPNsense rule sets, iptables/nftables megafiles at the network edge
- A self-managed Suricata/Snort IDS box or zeek deployment
- Manually-maintained threat-intel IP blocklists (FireHOL, Spamhaus DROP, abuse.ch) cron-pulled into firewall ACLs
- Geo/ASN blocking implemented in app or LB layer because the network can't do it
- Already a Magic Transit / Cloudflare WAN customer (it's the natural firewall layer for that traffic)
- tcpdump-on-a-jumpbox runbooks for packet capture / forensics

**Ideas:**
- Move the data-center edge ACLs (currently a Fortinet/Palo Alto rulebase) into Network Firewall expressions so filtering happens in Cloudflare's network before traffic reaches your routers
- Enable the Advanced managed threat-intel rulesets to auto-block Botnet/Malware/Open-Proxy source IPs instead of hand-maintaining Spamhaus/FireHOL lists in iptables
- Turn on IDS + Logpush to ship intrusion alerts to your SIEM, retiring a self-managed Suricata sensor

**Pairs with:** Cloudflare WAN, Cloudflare One, Multi-Cloud Networking

**Pricing:** Two tiers: Standard is included free with a Magic Transit or Cloudflare WAN subscription (basic protocol/port/IP/packet-length filtering + analytics); Advanced is a paid add-on (IDS, managed rulesets, geo/ASN, protocol validation, SWG egress, packet captures). Both require Magic Transit or Cloudflare WAN. (verify — drifts)

**Limits:**
- Hard dependency: requires Magic Transit or Cloudflare WAN — not a standalone firewall you can buy for an app behind the normal CDN
- Source-IP block rules can misbehave because rules evaluate after Cloudflare terminates incoming TCP connections (per the docs)
- It's L3/L4 network filtering + IDS, not a full app-layer WAF (that's Cloudflare WAF) — different layer, different product
- IDS, managed rulesets, and PCAPs are Advanced-plan (paid) features

**Notes:** Renamed from Magic Firewall. Genuinely an enterprise-network product — only relevant to teams already running their network through Cloudflare (Magic Transit/WAN). Strong lock-in via the Magic Transit/WAN dependency. Rate limiting is beta. For typical app/API protection the answer is Cloudflare WAF, not this.

**Docs:** https://developers.cloudflare.com/cloudflare-network-firewall/llms.txt, https://developers.cloudflare.com/cloudflare-network-firewall/about/ruleset-logic/index.md, https://developers.cloudflare.com/cloudflare-network-firewall/plans/index.md, https://developers.cloudflare.com/cloudflare-network-firewall/reference/network-firewall-fields/index.md

---

## Cloudflare One
`cloudflare-one` · Zero Trust / SASE / Networking Security · confidence: `high` · lock-in: `sticky`

**Is:** Cloudflare's SASE/SSE platform that unifies Zero Trust access (ZTNA), a secure web gateway, CASB, DLP, browser isolation, email security, and device posture on its global network, replacing the legacy security perimeter.

**Replaces:** A stack of perimeter appliances + point SaaS: a hardware VPN concentrator (Cisco AnyConnect/Palo Alto GlobalProtect) plus a legacy SWG/proxy (Zscaler/Netskope/Forcepoint) plus separate CASB and DLP vendors — collapsed into one control plane.

**Use it via:** Primarily a managed control plane: configured in the Zero Trust dashboard, the cloudflare-go / cloudflare-python SDKs, the Cloudflare v4 REST API (/accounts/{id}/access/*, /gateway/*, /access/apps), and Terraform (cloudflare_zero_trust_access_application, cloudflare_zero_trust_gateway_policy). Not a Worker binding — it sits in the request path via WARP enrollment + Tunnel connectors, not in your app code.

**Capabilities:**
- Access (ZTNA): identity- and context-aware policies in front of self-hosted and SaaS apps; clientless (browser-rendered) and client-based access
- Gateway (SWG): DNS, network (L4), HTTP, and egress filtering with category/threat-intel blocklists
- CASB: API-driven scanning of SaaS apps (Google Workspace, M365, etc.) for misconfig and data findings
- DLP: detects sensitive data (PII, secrets) across HTTP traffic and SaaS
- Browser Isolation (RBI): runs untrusted page code in Cloudflare's cloud, streams pixels/DOM to the user
- Email Security: phishing/BEC detection and policy
- Digital Experience Monitoring (DEX): per-device/network experience telemetry
- Three connectivity patterns: device-to-network (remote access), device-to-device (Mesh IPs), network-to-network (site interconnect)

**Detection signals — the lens fires on these:**
- VPN appliances / configs: OpenVPN, WireGuard server configs, Cisco AnyConnect, Palo Alto GlobalProtect, Pulse/Ivanti Connect Secure
- Existing SWG/proxy vendors in code or DNS: zscaler, netskope, forcepoint, mcafee web gateway, squid proxy + ACLs
- Home-grown app auth gateways / bastion hosts: nginx auth_request + oauth2-proxy, an internal SSO reverse proxy fronting admin panels
- IP allowlists hard-coded to office/VPN CIDRs in security groups, nginx 'allow/deny', or app middleware
- DLP/CASB point tools, manual SaaS audit scripts hitting Google Admin SDK / Microsoft Graph for misconfig
- jump boxes / SSH bastions, 'corp VPN required' in READMEs, RBAC tied to being on the VPN

**Ideas:**
- Replace the OpenVPN/WireGuard concentrator gating the internal admin panel with Access (ZTNA) + WARP, so access is identity- and posture-based instead of network-location-based
- Put clientless browser-rendered Access in front of a self-hosted dashboard so contractors reach it without a VPN client or a published public IP
- Route all corporate device egress through Gateway to enforce DNS + HTTP threat filtering and DLP instead of a separate Zscaler/Netskope subscription

**Pairs with:** Cloudflare Tunnel, WARP Client, Cloudflare WAN, Cloudflare Network Firewall, Data Localization

**Pricing:** Free Zero Trust plan covers up to 50 users for Access + Gateway; paid Pay-as-you-go and Enterprise contracts add seats and advanced modules (RBI, DLP, CASB, Email Security) priced per seat/user. (verify — drifts)

**Limits:**
- Module breadth varies by plan tier — RBI/DLP/CASB/Email Security are typically paid/Enterprise add-ons, not in the free 50-seat tier
- Pricing per-page not in the docs index; confirm seat counts and which modules are bundled
- Full value assumes WARP on devices and/or Tunnel for self-hosted apps — it is a platform, not a single drop-in API

**Notes:** This is an umbrella product; the real flag is usually one of its modules (Access for the home-grown auth proxy, Gateway for the DIY egress filter). Heavy operational lock-in: device enrollment, identity-provider wiring, and policy live in Cloudflare's dashboard. Not the right tool for purely in-app user authz (that's still your app's job / Access only fronts the app); it secures access to apps, it is not an in-code auth library. 'Cloudflare One Client' is the enterprise name for the WARP agent. Did not fetch a per-module pricing page this run.

**Docs:** https://developers.cloudflare.com/cloudflare-one/llms.txt, https://developers.cloudflare.com/cloudflare-one/index.md, https://developers.cloudflare.com/cloudflare-one/setup/replace-vpn/index.md

---

## Cloudflare Risk Score / UEBA
`cloudflare-risk-score` · Zero Trust / SASE / UEBA · confidence: `high` · lock-in: `sticky`

**Is:** Cloudflare One's user-risk layer: assigns Low/Medium/High scores from identity, device, DLP, Gateway, and partner signals so Access policies can adapt instead of trusting every logged-in user equally.

**Replaces:** A lightweight UEBA/risk-adaptive access glue stack: impossible-travel cron jobs, SIEM correlation rules, Okta/Entra risk copy-paste, and hand-written Access policy exceptions.

**Use it via:** Zero Trust dashboard: Team & resources > Users > Risk score for behaviors and scores; Access policy rules expose a User Risk Score selector. Okta risk exchange is configured from the Risk score integrations flow. No Worker binding.

**Capabilities:**
- User risk scores shown in Zero Trust, with Low/Medium/High levels driven by active risk behaviors
- Predefined behaviors include impossible travel, high DLP profile match count, malicious file interaction, suspicious DNS domains, high-risk DNS domains, and SentinelOne/CrowdStrike ZTA posture signals
- Access policies can use a User Risk Score selector to require, allow, block, or step up access based on current risk
- Okta integration can exchange risk signals between Cloudflare and Okta when Okta is the SSO provider
- Designed to combine Cloudflare Access, Gateway, DLP, WARP/device posture, and partner telemetry rather than one-off app logic

**Detection signals — the lens fires on these:**
- Homegrown 'impossible travel' detection over login/IP geolocation events
- Access/auth middleware that blocks users after DLP, EDR, DNS, or SIEM risk events
- Okta risk, Entra ID Protection, Exabeam, Splunk UBA, SentinelOne, or CrowdStrike ZTA signals manually copied into authorization logic
- A SIEM rule whose only job is to tag users high risk and tell admins to revoke app access
- Conditional Access / Access policy design that wants risk-adaptive decisions but lacks a shared user-risk primitive

**Ideas:**
- Replace a bespoke impossible-travel detector and manual app blocklist with Cloudflare Risk Score plus an Access policy that steps up or blocks High-risk users.
- If DLP/Gateway already see risky behavior, feed that into Cloudflare One user risk instead of building per-app risk tables.
- Use the Okta integration to exchange risk signals rather than polling Okta and rewriting Access rules yourself.

**Pairs with:** Cloudflare Access, Gateway, DLP, Device Posture / WARP, CASB, Cloudflare Logs / Logpush

**Pricing:** Part of Cloudflare One / Zero Trust entitlements; exact plan gating can change, so verify against the current Zero Trust plan docs before promising it.

**Limits:**
- Risk score is only as good as the Cloudflare One signals and integrations enabled in the account
- Some behaviors are disabled by default and must be enabled/configured
- Okta risk exchange requires Okta as the SSO provider and explicit integration setup
- Do not treat it as a general-purpose fraud engine; it is a user-risk signal for Cloudflare One / Access decisions

**Notes:** This is a strong 'stop hand-rolling risk glue' product when the organization already routes identity, device, Gateway, DLP, and Access through Cloudflare One. It is not a substitute for an enterprise SIEM/UEBA if you need arbitrary cross-vendor analytics, custom ML, or non-Cloudflare enforcement. The honest pitch is risk-adaptive Access decisions from signals Cloudflare already sees.

**Docs:** https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/risk-score/, https://developers.cloudflare.com/cloudflare-one/policies/access/, https://developers.cloudflare.com/cloudflare-one/identity/idp-integration/okta/

---

## Data Localization (Data Localization Suite)
`data-localization` · Compliance / Data Residency / Sovereignty · confidence: `high` · lock-in: `portable`

**Is:** A suite that controls where Cloudflare decrypts, processes, and stores your traffic and metadata — Regional Services pins TLS termination/inspection to a region, the Customer Metadata Boundary keeps logs in-region (EU/US), and Geo Key Manager controls where private TLS keys live.

**Replaces:** A DIY data-residency build: standing up region-locked infrastructure (EU-only LBs/CDN PoPs), self-hosting TLS termination in-country to avoid foreign key custody, scrubbing/region-partitioning your own logging pipeline, and the compliance/legal lift of proving GDPR/data-sovereignty boundaries.

**Use it via:** Regional Services configured per-hostname/per-zone (dashboard 'Regionalized for X', or addressing/API with a region/country setting; some setups use the Cloudflare for SaaS custom-hostname region field). CMB toggled at the account level (region + out-of-region access flag) via dashboard/API. Geo Key Manager set when uploading/managing certs. Logpush + GraphQL datasets for log access. Configured at the platform/account layer, not in Worker code.

**Capabilities:**
- Regional Services: accepts traffic at any data center worldwide (L3/L4 DDoS applied globally) but performs TLS decryption + app-layer processing (WAF, Bot Management, Workers, Cache, Load Balancing) only at in-region locations; e.g. a US request to an EU-regionalized hostname is forwarded encrypted to an EU data center before decryption
- Customer Metadata Boundary (CMB): keeps Customer Logs (request URLs, timestamps, firewall events) stored only in the selected region (EU or US); 'Allow out-of-region access' toggle gates who can read them; integrates with GraphQL analytics datasets and Logpush
- Geo Key Manager: restricts the geographic storage locations of private TLS/SSL keys
- Logpush to your own storage/SIEM for further control; compatibility matrix of which Cloudflare products honor localization

**Detection signals — the lens fires on these:**
- GDPR / Schrems II / data-residency requirements in compliance docs, DPAs, or customer contracts
- Region-locked infra: eu-only S3 buckets, region-pinned RDS, separate EU vs US deployments solely for data-residency
- Self-hosted TLS termination on-prem/in-region specifically to keep private keys out of a US vendor's hands; HSM/KMS region constraints (eu-central KMS, on-prem HSM)
- Log pipelines manually partitioned or scrubbed by region; 'EU logs must not leave the EU' rules
- Customers in regulated sectors (healthcare, finance, public sector) or EU/CH/AU/IN/JP data-sovereignty asks
- Comments about not being able to use a global CDN/WAF because of residency

**Ideas:**
- Turn on Regional Services (EU) for the regulated hostnames so WAF/Bot Management/Workers still run, but decryption only happens in EU data centers — instead of self-hosting TLS termination in-country
- Enable the Customer Metadata Boundary (EU) so request logs and firewall events never leave the EU, satisfying a data-residency clause without rebuilding the logging stack
- Use Geo Key Manager to keep private TLS keys stored only in approved regions to satisfy a sovereignty audit

**Pairs with:** Cloudflare One, Cloudflare WAN

**Pricing:** Enterprise add-on (no public price in the docs index); sold as part of/alongside Enterprise plans. (verify — drifts)

**Limits:**
- Regionalizing means non-region requests get forwarded in-region before decryption — adds latency and reduces the edge-locality benefit of a global network for those users
- Has documented limitations/compatibility caveats: not every Cloudflare product fully honors localization — check the compatibility + limitations pages before relying on it
- Region coverage is finite (docs explicitly call out EU and US for CMB; Regional Services supports more regions but verify the current list)
- Enterprise-gated; not self-serve

**Notes:** Compliance/residency product, not a dev primitive — flag it when you see GDPR/Schrems/data-sovereignty pressure or region-locked infra built only to satisfy residency. Did not fetch the region-support, limitations, or Geo Key Manager detail pages this run, so exact current region list and Geo Key Manager specifics are unverified. Lock-in is moderate (it's a config layer on top of Cloudflare you're already using).

**Docs:** https://developers.cloudflare.com/data-localization/llms.txt, https://developers.cloudflare.com/data-localization/regional-services/index.md, https://developers.cloudflare.com/data-localization/metadata-boundary/index.md

---

## Digital Experience Monitoring (DEX)
`cloudflare-dex` · Zero Trust / SASE · confidence: `high` · lock-in: `sticky`

**Is:** Endpoint + synthetic + network telemetry collected from the WARP/Cloudflare One client — device health, fleet status, HTTP application tests, traceroutes, and remote packet captures.

**Replaces:** Stop deploying Catchpoint / ThousandEyes endpoint agents or Nexthink just to see why remote users' apps and networks feel slow.

**Use it via:** Zero Trust dashboard (DEX: Monitoring, Tests, Diagnostics, Remote Captures) where HTTP/traceroute tests are created and fleet/device metrics are viewed; Cloudflare API for DEX tests and fleet-status data; Logpush job for DEX test data export. Telemetry source is the installed WARP/Cloudflare One client — no app binding/wrangler.

**Capabilities:**
- Device monitoring from the client: CPU usage, memory utilization, disk I/O, battery percentage/cycles, network I/O, and unique Wi-Fi networks (SSID) over time
- Fleet status: connectivity by Cloudflare data center, client connection state (Connected/Disconnected/Paused/Connecting), client mode, OS distribution, and client-version tracking with historical 'over time' views
- Synthetic HTTP tests: target URL + method + interval + expected codes, returning DNS time, connection time, Time to First Byte, server response time, and availability
- Traceroute tests: network path/hops, packet loss, latency, and round-trip time between device and endpoint
- Remote diagnostics: on-demand speed tests and remote packet captures (pcap) from a specific device
- DEX rules to scope which users/groups run which tests
- Logpush export of DEX application-test data to R2 / third-party storage / SIEM for retention beyond the standard ~7-day window

**Detection signals — the lens fires on these:**
- ThousandEyes Endpoint Agent / Catchpoint / Nexthink collectors pushed via MDM alongside the VPN client
- Home-grown cron scripts running curl-timing / mtr / traceroute on laptops and shipping results to a dashboard
- Helpdesk asking users to run speedtest-cli or manually capture a pcap to debug 'app is slow' tickets
- Custom RMM checks polling CPU/RAM/battery/Wi-Fi and forwarding to a TSDB just for endpoint health
- Synthetic uptime checks for internal apps run only from cloud probes, with no visibility from the actual user's device/network path

**Ideas:**
- Create DEX HTTP and traceroute tests for our internal app so we can see DNS/TTFB and packet loss from real remote devices instead of a ThousandEyes agent.
- Use DEX fleet status to find which Cloudflare data centers and client versions correlate with our slow-app tickets.
- Trigger a remote packet capture from a complaining user's device and Logpush DEX results to our SIEM for retention.

**Pairs with:** cloudflare-warp, cloudflare-gateway, cloudflare-access, logpush

**Pricing:** Available across Cloudflare Zero Trust / SASE plans; test and capture ceilings scale by tier (Free / Standard / Enterprise) (verify — drifts).

**Limits:**
- DEX Tests capped at 10 (Free) / 30 (Standard) / 50 (Enterprise) per account
- Remote captures/day: 100 (Free) / 200 (Standard) / 800 (Enterprise)
- Requires the WARP/Cloudflare One client installed and enrolled — no agent, no endpoint telemetry
- Default ~7-day data retention unless exported via Logpush; test types are HTTP + traceroute (not arbitrary protocol synthetics)

**Notes:** Only as good as WARP coverage — it observes the Cloudflare-One client's view, so unmanaged/agentless devices are invisible. Synthetic tests are HTTP + traceroute, not the full ThousandEyes path-viz/BGP suite, so set expectations for network teams. Lock-in is low (telemetry/exports), value is highest where WARP is already the access path; pairs naturally with Gateway/Access to explain 'is it the app, the network, or the device?'

**Docs:** https://developers.cloudflare.com/cloudflare-one/insights/dex/index.md, https://developers.cloudflare.com/cloudflare-one/insights/dex/monitoring/index.md, https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/index.md, https://developers.cloudflare.com/cloudflare-one/account-limits/index.md

---

## WARP Client (Cloudflare One Agent)
`warp-client` · Device Agent / Zero Trust Enrollment · confidence: `high` · lock-in: `sticky`

**Is:** Cloudflare's device agent that encrypts and routes traffic to Cloudflare's edge (MASQUE, with post-quantum crypto), enrolls devices into Zero Trust, and supplies device-posture signals for Access and Gateway policies.

**Replaces:** A traditional always-on corporate VPN client (AnyConnect/GlobalProtect/Pulse) plus a separate MDM/EDR posture agent — the on-device piece that forces all traffic through your security stack and proves the device is healthy.

**Use it via:** Not a code SDK — it's an installed OS agent. Deployed/managed via the Zero Trust dashboard device-enrollment settings, MDM (Intune/Jamf) with org/auth_client config, and configured by device profiles + WARP settings; posture and split-tunnel rules are set server-side in Zero Trust.

**Capabilities:**
- Connection modes (enterprise / Cloudflare One Agent): Traffic and DNS (default — full tunnel, enables DNS+network+HTTP policies, Browser Isolation, posture, AV scan, DLP); DNS Only (DNS policies only); Traffic Only (full tunnel, OS handles DNS); Local Proxy (only HTTP/SOCKS5 proxy-directed traffic); Posture Only (no routing, collects device health for Access policies)
- Transports: MASQUE (current default) and historically WireGuard; consumer DNS-only modes support DoH/DoT
- Device posture: feeds Access/Gateway policy decisions (device health = part of Zero Trust context)
- Platforms: Windows, macOS, Linux, iOS, Android
- MDM/managed deployment of the enterprise agent (Cloudflare One Agent)

**Detection signals — the lens fires on these:**
- An existing always-on VPN client mandated org-wide (AnyConnect, GlobalProtect, Pulse/Ivanti, OpenVPN Connect)
- MDM configs (Intune, Jamf, Kandji) pushing a VPN profile or per-app VPN
- 'Must be on the corporate VPN' in onboarding docs; conditional-access rules keyed to being on a VPN IP
- Home-grown device-posture checks or no posture enforcement at all on remote machines
- Per-app proxy/PAC files distributed to force browser traffic through a gateway

**Ideas:**
- Deploy the Cloudflare One Agent in Traffic-and-DNS mode via MDM so every managed laptop's egress runs through Gateway filtering + DLP, retiring the standalone VPN client
- Use Posture-Only mode to add device-health checks to Access policies (require disk encryption / EDR running) without forcing a full tunnel
- Use Local Proxy mode to send only specific app/browser traffic through Cloudflare on developer machines that can't take a full tunnel

**Pairs with:** Cloudflare One, Cloudflare Tunnel, Cloudflare WAN, Cloudflare Network Firewall

**Pricing:** The WARP app is free; consumer WARP+ is a paid upgrade for the larger network. Enterprise device enrollment is part of Cloudflare One/Zero Trust seat pricing (free up to 50 users, then per-seat). (verify — drifts)

**Limits:**
- Two distinct products share the WARP name: the consumer 1.1.1.1/WARP app vs the enterprise Cloudflare One Agent (Zero Trust-managed) — the modes and management differ
- It's an endpoint agent: requires install + MDM rollout + OS support, and end-user devices must be enrolled
- Posture signals are Cloudflare's own checks / EDR integrations, not a full replacement for a dedicated EDR/MDM

**Notes:** The consumer WARP docs deliberately omit enterprise specifics (protocols, posture, enrollment) — the enterprise modes (Traffic and DNS, Posture Only, etc.) come from the Cloudflare One configure-warp page, which I fetched. Lock-in is operational (enrollment + device profiles in Cloudflare). Not a standalone product you'd buy without the rest of Cloudflare One; it's the on-device on-ramp.

**Docs:** https://developers.cloudflare.com/warp-client/llms.txt, https://developers.cloudflare.com/warp-client/index.md, https://developers.cloudflare.com/warp-client/warp-modes/index.md, https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/warp/configure-warp/warp-modes/index.md

---
