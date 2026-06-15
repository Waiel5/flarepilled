# Cloudflare Images — verified deep-dive (video #1)

- **Source:** YouTube — "I've been sleeping on Cloudflare Images" (https://www.youtube.com/watch?v=SOQbMFvOj8Q)
- **Ingested:** 2026-06-15 (watched via /watch — frames + captions)
- **Confidence:** `high` for everything demonstrated on screen; `medium` where the
  presenter asserted but did not show; pricing **not shown → `verify`**.
- **Catalog slug:** `images` · **Category:** Media

> Note: the auto-captions repeatedly say "Cloudinary" — that is an
> auto-transcription/verbal slip. Every on-screen artifact (the dashboard at
> `imagedelivery.net`, the Delivery tab, the URL params) is **Cloudflare Images**.

## One-liner

Upload an image once; get every variant as a URL. Cloudflare stores, optimizes,
transforms, and delivers it from the edge — no buckets, resize pipeline, or
format-negotiation middleware to operate.

## Replaces (the "stop building this" hook)

The entire roll-your-own image pipeline the video diagrams as "the old way":
- multipart upload parsing + size/type validation on your server,
- a raw-file bucket (R2/S3),
- a resize/transform pipeline (`sharp` / ImageMagick) + a background queue,
- per-variant storage (thumbnail / square / hero),
- a CDN in front + custom cache logic,
- WebP/AVIF content-negotiation middleware (parse `Accept`, branch per browser).

→ collapses to **two things: an upload and a URL.** Also a direct competitor to
**Cloudinary / imgix / Imgproxy**.

## Capabilities (verified on screen unless noted)

- **Upload → image ID.** Demo app "Super Images" uploads an iPhone **HEIC** file;
  Cloudflare ingests and converts it (HEIC has no browser preview, CF handles it).
- **Named variants.** Pre-defined transforms delivered by URL suffix. Demo had:
  `thumbnail` (200×200), `classic` (800×800), `hero` (wide banner, ~1366×900),
  `public` (~1366×768). Each variant = width / height / fit / optional blur / optional
  watermark. Dashboard → **Delivery** tab manages them. Switch variant = change the URL.
- **A 200×200 thumbnail came back at ~2.3 KB.**
- **Flexible variants.** Toggle in dashboard → arbitrary transforms via URL query
  params (width, height, fit, quality, format) without pre-defining a variant.
  Warning shown on enable: *"anyone can obtain untransformed full-resolution images
  and their metadata"* — flexible variants expose the original; weigh before enabling.
- **Background removal** via `segment=foreground` URL param. Verified: sunglasses
  rendered with the background stripped to transparent. JPEG is rejected for this
  (no alpha channel); use WebP or PNG. Demo used WebP @ quality 85.
- **Face-aware crop** via `gravity=face` (+ a `zoom` amount, e.g. `0.2`). Verified:
  a full-body street photo smart-cropped and centered on the face for the hero variant.
- **Format conversion / auto content-negotiation.** `format=webp` (and AVIF) on
  demand; the "serve the right format per browser" step is automatic — "gone, it's
  just auto."
- **Pre-signed delivery** handled out of the box (token expiry, signed requests) —
  no manual signing.

## API surface (as shown / inferred — verify exact syntax against docs)

- Stored reference is an **image ID** (kept in your DB).
- Delivery is a URL: `https://imagedelivery.net/<account-hash>/<image-id>/<variant>`
  for named variants; flexible variants take query params (e.g.
  `.../<image-id>/w=800,h=800,segment=foreground,format=webp,gravity=face,zoom=0.2`).
  *(Exact param grammar — confirm via cloudflare-docs MCP before quoting.)*
- Upload + variant management via the Images dashboard and the Cloudflare API;
  Workers integration via the Images binding. *(Binding/SDK specifics: verify.)*

## detectionSignals (what makes the lens fire)

- `multer` / `busboy` + `sharp` / `gm` / `imagemagick` in deps
- a `/uploads` or `/variants` bucket + code generating multiple sizes
- manual `Accept` header parsing / `image/webp` branching for format negotiation
- `cloudinary` / `imgix` / `@imgproxy` SDKs or URLs
- storing several derived sizes per image in S3/R2
- HEIC/HEIF handling code; client-side canvas resizing before upload

## ideaPrompts (proactive)

- Any user-generated-content surface (avatars, listings, marketplace photos): drop
  the resize pipeline entirely, store the image ID, render variants by URL.
- `segment=foreground` for instant "remove background" on product shots — replaces a
  paid background-removal API.
- `gravity=face` for avatar/hero auto-cropping without a face-detection service.

## pairsWith

R2 (raw originals / overflow), Workers (auth + signing + the upload endpoint),
Pages (the front-end), Stream (the video equivalent of this story).

## Limits / caveats (verify all)

- Flexible variants expose full-resolution originals + metadata — security tradeoff.
- `segment=foreground` requires an alpha-capable format (WebP/PNG, not JPEG).
- Pricing/quota **not shown in the video** — do not quote numbers without checking docs.
- Lock-in: delivery URLs and the transform grammar are Cloudflare-specific.

## docs

- Product index: https://developers.cloudflare.com/images/llms.txt
  *(fetch before quoting specifics — this entry is from a demo video, not the docs.)*
