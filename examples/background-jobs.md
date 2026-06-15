# Background jobs (emails, thumbnails, webhooks)

**Task:** "Offload slow work from the request path — send the welcome email, generate a
thumbnail, fan out webhooks. Today it's BullMQ on a Redis box (or SQS + a worker)."

## The old way (a broker + a worker pool you babysit)

```ts
import { Queue, Worker } from 'bullmq'                    // + a Redis instance to run
const jobs = new Queue('jobs', { connection: { url: process.env.REDIS_URL } })
await jobs.add('welcome-email', { userId })

new Worker('jobs', async (job) => { /* ... */ }, { connection })  // a process to keep alive,
// + retry/backoff config, + dead-letter handling, + scaling the worker dynos.
```

## With Cloudflare Queues (producer binding + a consumer Worker)

```jsonc
// wrangler.jsonc
{
  "queues": {
    "producers": [{ "binding": "JOBS", "queue": "jobs" }],
    "consumers": [{ "queue": "jobs", "max_batch_size": 10, "max_retries": 3, "dead_letter_queue": "jobs-dlq" }]
  }
}
```
```bash
npx wrangler queues create jobs && npx wrangler queues create jobs-dlq
```
```ts
// produce (from any Worker) — no Redis, no connection string
await env.JOBS.send({ type: 'welcome-email', userId })

// consume — batching, retries, and the DLQ are declarative, not your code
export default {
  async queue(batch, env) {
    for (const msg of batch.messages) { /* do work */; msg.ack() }
  },
}
```

**Why it's the swap:** no broker to run and no egress fees; batching, retries, and a
dead-letter queue are config. For **durable multi-step** workflows (saga-style, with
state across steps and sleeps), reach for **Workflows**; for a fixed schedule, a Worker
**Cron Trigger**.

### The honest catch
- **Lock-in: sticky** — the producer/consumer wiring is Cloudflare-specific.
- Queues is at-least-once with batch semantics — design consumers **idempotent** (same
  as SQS), don't assume exactly-once.
- **Verify** throughput limits, max batch size, and per-message size against
  `https://developers.cloudflare.com/queues/llms.txt` before committing.
