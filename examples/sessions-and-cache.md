# Sessions, cache, counters (the Redis box)

**Task:** "We run Redis for three things: session storage, a cached config blob, and a
per-user rate-limit counter." (This one has a **trap** — read to the end.)

## The old way (one Redis for everything)

```ts
import Redis from 'ioredis'
const redis = new Redis(process.env.REDIS_URL)          // a box to run + scale
await redis.set(`sess:${id}`, json, 'EX', 3600)         // sessions
await redis.get('config:flags')                          // hot read-mostly blob
await redis.incr(`rl:${userId}`)                         // write-hot counter
```

## With Cloudflare — but split by access pattern (this is the point)

**Read-mostly (sessions, config) → Workers KV:**
```jsonc
{ "kv_namespaces": [{ "binding": "SESSIONS", "id": "<id>" }] }
```
```bash
npx wrangler kv namespace create SESSIONS
```
```ts
await env.SESSIONS.put(`sess:${id}`, json, { expirationTtl: 3600 })
const flags = await env.SESSIONS.get('config:flags', 'json')   // edge-cached, global
```

**Write-hot / read-after-write (the counter) → Durable Object, NOT KV:**
```ts
// a DO gives you a single consistent, transactional home for the counter
const id = env.RATE.idFromName(userId)
const n = await env.RATE.get(id).fetch('https://rl/incr').then(r => r.json())
```

**Why it's the swap:** the Redis box disappears — KV serves read-mostly data from the
edge globally, Durable Objects give you the strongly-consistent counter.

### The honest catch — why you must split
- **Workers KV is eventually consistent (~60s) and ~1 write/sec *per key***. Putting the
  rate-limit counter in KV would silently break it (stale reads, dropped writes) and the
  writes cost ~10× reads. That's why counters/locks/read-after-write go to **Durable Objects**, not KV.
- **Lock-in:** KV sticky, DO deep (its model is designed-around).
- **Verify** current KV consistency/limits + DO pricing against the docs before you commit —
  `https://developers.cloudflare.com/kv/llms.txt`, `https://developers.cloudflare.com/durable-objects/llms.txt`.
