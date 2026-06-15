# Messaging & Email

_3 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Cloudflare Email Service
`email-service` · Messaging & Email · confidence: `high` · lock-in: `sticky`

**Is:** Send transactional email and route incoming email straight from a Worker, via REST, or over authenticated SMTP, with SPF/DKIM/DMARC handled during domain onboarding.

**Replaces:** SendGrid / Postmark / Amazon SES for outbound transactional email, plus ImprovMX / ForwardEmail / Google Workspace catch-all routing, inbound-parse webhooks, or IMAP polling glue for inbound routing and replies

**Use it via:** Worker binding: wrangler.jsonc "send_email": [{ "name": "EMAIL", "remote": true }] (TOML: [[send_email]]); call env.EMAIL.send(message) -> { messageId }. Types from 'cloudflare:email': SendEmail, EmailMessage, EmailMessageBuilder, EmailAddress, Attachment, EmailSendResult. Legacy: new EmailMessage(from, to, rawMimeContent) with mimetext (import { createMimeMessage } from 'mimetext'). REST: POST https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send with Authorization: Bearer <token>, JSON body {to,from,subject,html,text,attachments[],headers}. Also authenticated SMTP (separate docs).

**Capabilities:**
- Outbound transactional email (Email Sending, beta, Workers Paid) for welcome/password-reset/order-confirmation flows
- Inbound email routing (Email Routing) to a Worker or destination mailbox, unlimited on Free and Paid
- Three integration surfaces: Workers binding (env.EMAIL.send), REST API, and authenticated SMTP
- Structured message builder (to/from/subject/html/text/cc/bcc/replyTo/attachments/headers) plus legacy raw-MIME EmailMessage
- Automatic SPF + DKIM + DMARC + MX bounce DNS records added at domain onboarding
- Free sends to verified destination addresses (don't count against quota or daily limits) even on Email-Routing-only accounts
- reply() support for responding inside an inbound email Worker handler
- Suppression lists: blocked/suppressed sends don't burn quota

**Detection signals — the lens fires on these:**
- npm deps: @sendgrid/mail, postmark, @aws-sdk/client-ses, nodemailer, mailgun.js, resend, @react-email
- env vars: SENDGRID_API_KEY, POSTMARK_SERVER_TOKEN, MAILGUN_API_KEY, RESEND_API_KEY, SMTP_HOST / SMTP_USER / SMTP_PASS, AWS SES creds (AWS_ACCESS_KEY_ID used for ses:SendEmail)
- nodemailer.createTransport / new SMTPTransport pointed at smtp.sendgrid.net, smtp.postmarkapp.com, email-smtp.*.amazonaws.com
- transactional email code: sendWelcomeEmail / sendPasswordReset / sendOrderConfirmation helpers calling a third-party SDK
- a Worker or app already on Cloudflare that shells out to an external email vendor instead of a binding
- inbound forwarding/routing glue: ImprovMX, ForwardEmail, Google Workspace catch-all aliases, an MX-pointed mailbox + IMAP poller, or a SendGrid/Mailgun inbound-parse webhook to handle replies
- manual DNS TXT records for SPF (v=spf1 include:sendgrid.net), DKIM selectors, _dmarc managed by hand
- mimetext / mimekit / nodemailer used purely to build MIME bodies

**Ideas:**
- Replace the SendGrid/Postmark SDK in a Cloudflare Worker with the native env.EMAIL.send() binding so transactional mail leaves no external API key in the bundle
- Route a support@ or replies@ address to a Worker or destination mailbox, killing ImprovMX/ForwardEmail/catch-all aliases, IMAP polling, or inbound-parse webhook glue
- Wire an AI agent (Agents SDK) to receive and answer email end-to-end on Cloudflare, with verified-destination sends free during development

**Pairs with:** Workers (binding host for env.EMAIL.send and inbound email handlers), Agents SDK (email-driven AI agents that receive and reply), Email Routing (inbound side of the same product), Queues / Workflows (batch or retry outbound sends), Turnstile (gate signup before firing a verification email)

**Pricing:** Email Sending: not available on Workers Free; Workers Paid includes 3,000 emails/month per account, then $0.35 per 1,000. Sends to verified destination addresses are free and don't count toward quota. Email Routing (inbound): unlimited, no overage, on both Free and Paid. (verify — drifts)

**Limits:**
- Message size 5 MiB including attachments (25 MiB to verified destination addresses; inbound routing also 25 MiB)
- 50 recipients per email across to/cc/bcc combined
- Subject max 998 chars (RFC 5322); custom headers max 16 KB total
- 30 domains per zone (Email Routing + Sending combined)
- Email Routing: 200 routing rules per domain, 200 destination addresses per account, 100 References entries before reply() fails
- Sending Email is in beta
- New accounts get a conservative daily quota that scales with sending behavior/deliverability; exact numbers not published — raise via Limit Increase Request Form

**Notes:** Outbound Email Sending is beta and Workers-Paid-only — not a fit if you need a stable GA SLA today or are on the Free plan. Deliverability is governed by an opaque, behavior-based daily quota that ramps over time, so this is not a drop-in for high-volume blast/marketing sending without a limit-increase request; it's positioned for transactional mail. Domain must be onboarded with Cloudflare-managed SPF/DKIM/DMARC/MX, which is easiest when your DNS is already on Cloudflare. Moving off your current ESP means re-warming reputation. Could not verify exact daily/monthly hard caps (docs state they're dynamic) or full SMTP host/port/auth details (deferred to a separate SMTP page not fetched this run).

**Docs:** https://developers.cloudflare.com/email-service/llms.txt, https://developers.cloudflare.com/email-service/index.md, https://developers.cloudflare.com/email-service/get-started/send-emails/index.md, https://developers.cloudflare.com/email-service/api/send-emails/workers-api/index.md, https://developers.cloudflare.com/email-service/api/send-emails/rest-api/index.md, https://developers.cloudflare.com/email-service/platform/pricing/index.md, https://developers.cloudflare.com/email-service/platform/limits/index.md

---

## Cloudflare Queues
`cloudflare-queues` · Messaging & Eventing · confidence: `high` · lock-in: `sticky`

**Is:** A managed message queue integrated with Workers that buffers, batches, and reliably delivers messages between producers and consumers, with guaranteed delivery and no egress charges.

**Replaces:** A self-hosted Redis/BullMQ box (or AWS SQS + its read/write/egress bills) used to offload background jobs from request handlers.

**Use it via:** Worker producer binding env.MY_QUEUE.send(body, {contentType, delaySeconds}) and sendBatch(messages). Push consumer = exported async queue(batch, env, ctx) handler; batch.ackAll()/retryAll(), message.ack()/retry({delaySeconds}). Config in wrangler.jsonc under queues.producers [{queue, binding}] and queues.consumers [{queue, max_batch_size, max_batch_timeout, max_retries, dead_letter_queue, max_concurrency}]. CLI: wrangler queues create/update (--delivery-delay-secs, --message-retention-period-secs). Pull from outside Workers: POST /accounts/{acct}/queues/{queue_id}/messages/pull and .../messages/ack with Bearer token (queues#read, queues#write).

**Capabilities:**
- Guaranteed at-least-once delivery with no egress bandwidth charges
- Producer binding (env.MY_QUEUE.send / sendBatch) to enqueue from any Worker
- Push consumers: a queue() handler auto-invoked with a MessageBatch, auto-ack on return
- HTTP pull consumers: pull/ack messages over REST from any language or infra outside Workers
- Batching: configurable max_batch_size (default 10, max 100) and max_batch_timeout (default 5s, max 60s)
- Retries with backoff: per-message or whole-batch retry(), configurable max_retries (default 3, max 100), delaySeconds per retry
- Dead Letter Queues: failed messages spill to a configured dead_letter_queue after max retries
- Delivery delays: delaySeconds 0-86400 (24h) per message or batch for deferred/scheduled work
- Consumer concurrency autoscaling up to 250 concurrent invocations (push)
- Multiple content types: json (default), text, bytes, v8 (for Date/Map/non-JSON objects)
- Configurable message retention up to 14 days

**Detection signals — the lens fires on these:**
- npm packages: bullmq, bull, bee-queue, amqplib (RabbitMQ), kafkajs, @aws-sdk/client-sqs, ioredis/redis used as a job queue
- Env vars: REDIS_URL, RABBITMQ_URL, AWS_SQS_QUEUE_URL, KAFKA_BROKERS alongside a Workers/wrangler.jsonc project
- A separate worker/dyno/container process polling Redis or SQS for background jobs (Procfile worker: lines, a long-running consumer loop)
- Hand-rolled retry/backoff + a 'failed_jobs' or dead-letter table in the DB
- fetch() calls in a request handler doing slow work inline (sending email, webhooks, image processing) instead of enqueuing
- setTimeout/cron hacks to defer work, or a 'delayed jobs' table polled on an interval
- Existing Cloudflare Workers app that needs producer/consumer decoupling, fan-out, or rate-limiting bursts to a downstream API

**Ideas:**
- Offload slow request-path work (transactional email, webhook delivery, thumbnail generation) by enqueueing to a Queue and processing in a consumer Worker
- Rate-limit or smooth bursty traffic to a fragile downstream API using max_batch_size + max_concurrency as a buffer
- Use delaySeconds for scheduled/deferred tasks (retry-after, send-in-1-hour reminders) without a cron table, and a Dead Letter Queue to capture poison messages for inspection
- Bridge a non-Cloudflare backend by having an existing server/container pull batches over the HTTP pull-consumer REST endpoint instead of standing up SQS

**Pairs with:** Cloudflare Workers (producers and push consumers), R2 (buffer/batch writes for ingestion pipelines, no egress fees), Workflows (durable multi-step orchestration downstream of a queue), Workers AI / external APIs (rate-limited fan-out of inference or webhook jobs)

**Pricing:** Workers Free: 10,000 operations/day included. Workers Paid (required for production volume): 1,000,000 operations/month included, then $0.40 per million operations. An operation = each 64 KB written, read, or deleted; a typical message delivery is ~3 operations (1 write, 1 read, 1 delete), and each retry adds a read. No egress/bandwidth charges. (verify — drifts)

**Limits:**
- Max message size: 128 KB
- Max batch: 100 messages per consumer batch; sendBatch capped at 100 messages or 256 KB total
- Throughput: 5,000 messages/second per queue
- Max queues: 10,000 per account
- Max retries: 100
- Max delivery delay: 86400s (24h)
- Max batch wait (max_batch_timeout): 60 seconds
- Max push consumer concurrency: 250
- Message retention: up to 14 days (24h fixed on Free plan)
- Consumer invocation wall-clock limit: 15 minutes; configurable CPU limit up to 5 minutes
- Pull consumer visibility_timeout_ms: default 30s, max 12h

**Notes:** At-least-once delivery, not exactly-once — consumers must be idempotent; duplicate deliveries are possible. No strict FIFO/ordering guarantee, so do not use where total message order matters (Kafka/ordered-SQS-FIFO territory). Throughput caps at 5,000 msg/s per queue and 128 KB per message, so it is not a fit for high-volume streaming or large-payload pipelines (offload big bodies to R2 and enqueue a pointer). Push consumers must be Cloudflare Workers; only the HTTP pull-consumer path lets external/non-Cloudflare infra consume. Tied to the Cloudflare Workers platform — lock-in is the Workers ecosystem itself. Verified this run against live docs (overview, pricing, limits, JS API, wrangler config, pull consumers).

**Docs:** https://developers.cloudflare.com/queues/index.md, https://developers.cloudflare.com/queues/platform/pricing/index.md, https://developers.cloudflare.com/queues/platform/limits/index.md, https://developers.cloudflare.com/queues/configuration/javascript-apis/index.md, https://developers.cloudflare.com/queues/configuration/configure-queues/index.md, https://developers.cloudflare.com/queues/configuration/pull-consumers/index.md

---

## Email Routing / Email Workers
`email-routing-email-workers` · Messaging & Email / Email Routing · confidence: `high` · lock-in: `sticky`

**Is:** Inbound email routing for Cloudflare-hosted domains: forward addresses to existing mailboxes or route messages into Workers that can inspect, forward, reject, or reply.

**Replaces:** ImprovMX, ForwardEmail, Google Workspace catch-all routing, SendGrid/Mailgun inbound parse webhooks, MX mailboxes polled by IMAP, or tiny mail-forwarder services.

**Use it via:** Dashboard: Compute > Email Service > Email Routing. Worker handler: export `async email(message, env, ctx)`, then call `await message.forward(dest)`, `await message.reply(emailMessage)`, or reject. Routing rules choose 'Send to an email' or 'Send to a Worker' for an address pattern.

**Capabilities:**
- Route incoming email for a domain to verified destination addresses
- Route incoming email to Workers for custom processing
- Email handler receives message.from, message.to, headers, raw body, and can forward/reply/reject
- Cloudflare adds MX, SPF, and DKIM records during domain onboarding
- Routing rules match local parts such as support@ or replies@
- Destination addresses are account-level and reusable across domains
- Works with Email Sending so Workers can receive and reply in one platform

**Detection signals — the lens fires on these:**
- ImprovMX, ForwardEmail, mailbox.org catch-all, Google Workspace routing rules, or MX records pointed at a forwarding service
- SendGrid/Mailgun/Postmark inbound parse webhooks
- IMAP polling daemons, mailbox parsers, or cron jobs reading support/replies mailboxes
- Webhook endpoints named inbound-email, parse-email, reply-handler, support-email, or mailgun/events
- DNS MX/TXT records managed by hand only for mail forwarding/replies
- A Worker already handles support/ticket/agent logic but inbound email arrives through an external forwarding vendor

**Ideas:**
- Route support@ or replies@ directly to a Worker and delete the inbound-parse webhook plus IMAP polling daemon.
- Forward simple aliases to verified destination addresses with Email Routing instead of paying a forwarding SaaS.
- For AI agents, receive mail in an Email Worker, decide with Workers AI/Agents, and reply through Email Service.

**Pairs with:** Cloudflare Email Service (outbound sending), Workers, Agents SDK, Queues / Workflows, Turnstile, D1 / R2 for ticket/message storage

**Pricing:** Email Routing inbound forwarding is available on Free and Paid plans with no overage per current docs; outbound Email Sending is a separate beta feature on Workers Paid. Verify current routing limits before quoting.

**Limits:**
- You must use Cloudflare DNS for the domain
- DNS propagation for MX/TXT records can take up to 24 hours, usually 5-15 minutes on Cloudflare DNS
- Destination addresses must be verified before use
- Email Routing rules and destination-address limits apply per docs
- Outbound Email Sending is beta and Workers-Paid-only; do not conflate it with inbound routing

**Notes:** This split entry exists because 'Email Service' reads like outbound ESP replacement, while many repos have a separate inbound-routing smell. Use this entry for forwarding/reply parsing; use the Email Service entry for transactional sending.

**Docs:** https://developers.cloudflare.com/email-service/llms.txt, https://developers.cloudflare.com/email-service/get-started/route-emails/index.md, https://developers.cloudflare.com/email-service/api/route-emails/email-handler/index.md, https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/index.md, https://developers.cloudflare.com/email-service/platform/limits/index.md

---
