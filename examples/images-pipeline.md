# User-Uploaded Images

**Task:** "Users upload photos for their product listings. We need thumbnails, a
square, and a hero banner, in WebP where the browser supports it."

## The old way (roll your own pipeline)

```ts
// 1. Parse + validate the upload on your server
const form = await parseMultipart(req)          // busboy/multer
assertSize(form.file, 5 * 1024 * 1024)
assertMime(form.file, ['image/jpeg', 'image/png', 'image/heic'])

// 2. Store the raw original
await s3.putObject({ Bucket: 'uploads', Key: id, Body: form.file })   // + egress later

// 3. Generate every variant (CPU-heavy → background queue)
import sharp from 'sharp'
for (const v of [
  { name: 'thumb',  w: 200,  h: 200 },
  { name: 'square', w: 800,  h: 800 },
  { name: 'hero',   w: 1366, h: 900 },
]) {
  const out = await sharp(buf).resize(v.w, v.h, { fit: 'cover' }).toBuffer()
  await s3.putObject({ Bucket: 'variants', Key: `${id}/${v.name}`, Body: out })
}

// 4. CDN + cache rules in front of the bucket … (CloudFront config, TTLs)

// 5. Serve WebP/AVIF only to browsers that accept it
function pickFormat(req: Request) {
  const accept = req.headers.get('accept') ?? ''
  if (accept.includes('image/avif')) return 'avif'
  if (accept.includes('image/webp')) return 'webp'
  return 'jpeg'
}
// … plus a worker pool, retry logic, and HEIC decoding nobody enjoyed writing
```

Storage buckets, a resize pipeline, a queue, a CDN, content-negotiation middleware,
and HEIC handling — all undifferentiated plumbing, all yours to babysit.

## With Cloudflare Images

```ts
// Upload once. Store the returned image ID in your DB.
const { id } = await uploadToCloudflareImages(file)   // HEIC decoded for you
listing.imageId = id
```

```html
<!-- Every variant is just a URL. Format negotiation is automatic. -->
<img src="https://imagedelivery.net/<hash>/{{imageId}}/thumbnail" />   <!-- 200×200, ~2.3 KB -->
<img src="https://imagedelivery.net/<hash>/{{imageId}}/hero" />        <!-- wide banner -->

<!-- Flexible variants: transform by query param, no pre-definition -->
<!-- remove the background (needs an alpha format → WebP/PNG, not JPEG) -->
<img src="https://imagedelivery.net/<hash>/{{imageId}}/w=800,segment=foreground,format=webp" />
<!-- face-aware hero crop -->
<img src="https://imagedelivery.net/<hash>/{{imageId}}/gravity=face,zoom=0.2,format=webp" />
```

**A whole pipeline → an upload and a URL.** No buckets to manage, no resize queue,
no CDN cache rules, no `Accept`-header middleware. Background removal and smart face
crops — which you would otherwise pay a separate API for — become URL parameters.

### The honest catch

- Delivery URLs and the transform grammar are **Cloudflare-specific** (lock-in).
- **Flexible variants expose the full-resolution original + metadata** — a security
  tradeoff you opt into.
- `segment=foreground` needs WebP/PNG (JPEG has no alpha channel).
- **Pricing/quotas: verify against the docs** before committing — they drift.

> Verified `high` from video #1 (2026-06-15). Exact URL param grammar and the Workers
> binding: confirm via the `cloudflare-docs` MCP before quoting. See
> `knowledge/videos/2026-06-15-cloudflare-images.md`.
