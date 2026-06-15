# Object Storage (uploads, exports, backups)

**Task:** "Store user uploads and serve them back. We're on S3 and the egress line on
the bill keeps climbing."

## The old way (S3 + the egress meter)

```ts
import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3'
const s3 = new S3Client({ region: 'us-east-1' })           // creds in env, IAM policy to maintain

await s3.send(new PutObjectCommand({ Bucket: 'uploads', Key: key, Body: bytes }))
// every GET that leaves AWS is billed egress; add CloudFront + an OAI to soften it,
// now you own a CDN distribution + cache-invalidation logic too.
```

## With R2 (zero egress, S3-compatible)

```jsonc
// wrangler.jsonc
{
  "r2_buckets": [{ "binding": "UPLOADS", "bucket_name": "uploads" }]
}
```
```bash
npx wrangler r2 bucket create uploads      # one command provisions it
```
```ts
// in the Worker — the binding carries the credential; nothing in env
await env.UPLOADS.put(key, bytes)
const obj = await env.UPLOADS.get(key)
return new Response(obj.body)               // served from the edge, no egress fee
```

**Why it's the swap:** R2 is S3-API-compatible (point the `@aws-sdk` client at the R2
endpoint if you'd rather not rewrite), so migration is mostly a data copy, and **egress
is free** — the line item that motivated this disappears.

### The honest catch
- **Lock-in: sticky** — leaving means copying data back out (egress-free, at least).
- R2 is object storage — **not** for hot mutable state or low-latency random writes
  (→ Durable Objects / KV).
- **Verify** current Class A/B operation pricing and storage rates against the docs
  before quoting numbers — `https://developers.cloudflare.com/r2/llms.txt`.
