# Media

_4 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Cloudflare Images
`cloudflare-images` · Media / Image Optimization · confidence: `high` · lock-in: `sticky`

**Is:** Edge image pipeline that resizes, recompresses, and re-encodes images on the fly (and optionally stores them), so you stop generating and shipping multiple image variants yourself.

**Replaces:** A self-hosted sharp/ImageMagick resize pipeline writing variants to S3 + a CDN, or a SaaS like Cloudinary / imgix / Mux (for images / thumbnailing).

**Use it via:** Three surfaces. (1) Worker binding: add `"images": { "binding": "IMAGES" }` to wrangler.jsonc, then `env.IMAGES.input(stream).transform({width:800}).output({format:'image/webp'}).response()`. (2) URL transform: `/cdn-cgi/image/<options>/<source-image-url>` e.g. `/cdn-cgi/image/width=800,quality=75,format=auto/https://.../photo.jpg`. (3) In-Worker fetch: `fetch(url, { cf: { image: { width:800, height:600, fit:'scale-down', format:'avif' } } })`. Storage/admin via REST: `/client/v4/accounts/{account_id}/images/v1` (upload, list, direct_upload).

**Capabilities:**
- Two modes: Transformations ('bring your own storage' — optimize remote images from any origin including R2/S3) and hosted Storage (upload images to Cloudflare's managed bucket).
- On-the-fly resize, crop, fit, quality, blur, sharpen, rotate, and gravity controls applied at the edge and cached automatically.
- Automatic format conversion to modern codecs (WebP, AVIF) including Accept-header content negotiation to pick the optimal format per browser.
- Predefined / named variants for hosted images so a single upload serves many device/breakpoint sizes.
- Three integration surfaces: URL-based /cdn-cgi/image/ transforms, the cf.image options object on a Worker fetch() subrequest, and the IMAGES Worker binding (input -> transform -> draw -> output -> response).
- Direct Creator Upload (signed one-time upload URLs) so end users upload straight to Images without your server proxying the bytes.
- Image compositing/watermarking via the binding's .draw() overlay method.
- Animated image handling (animated WebP/GIF), SVG sanitization, and HEIC input support.

**Detection signals — the lens fires on these:**
- npm deps: `sharp`, `jimp`, `imagemin`, `gm`/`graphicsmagick`, `@squoosh/lib`, `image-size`, `multer` (for image upload handling).
- Python: `Pillow`/`PIL`, `pillow-heif`, `wand` (ImageMagick), a Celery/cron task that pre-generates thumbnails.
- SaaS SDKs / hostnames you'd be paying for: `cloudinary`, `res.cloudinary.com`, `imgix`, `*.imgix.net`, `@imgix/js-core`, `imagekit`, `ik.imagekit.io`, `thumbor`.
- Architecture shape: a resize service / lambda that writes `*_thumb.jpg`, `*_small.webp`, `*_medium`, `*_large` variants to a bucket; `srcset`/`<picture>` markup hand-built from those variants.
- Env vars / config: `AWS_S3_BUCKET` + an images/uploads prefix, `CLOUDINARY_URL`, `IMGIX_TOKEN`, a `Dockerfile` that `apt-get install`s libvips/imagemagick.
- Manual WebP/AVIF conversion code, `Accept`-header sniffing to choose image format, or a `next/image` loader pointed at a custom optimizer.
- Egress/bandwidth line items from serving full-size originals out of S3/GCS.

**Ideas:**
- Point a Worker (or just /cdn-cgi/image/ URLs) at images already in R2 or S3 and delete the entire sharp/Pillow thumbnail-generation pipeline — resize and format-convert on demand, cached at the edge.
- Replace hand-built srcset variants with `format=auto` URL transforms so every browser gets AVIF/WebP automatically without you maintaining per-breakpoint files.
- Use Direct Creator Upload to let users upload avatars/photos straight to Images with a signed URL, removing the upload-proxy + virus-of-storage logic from your API server.
- Use the binding's .draw() to watermark or composite user-generated images in a Worker instead of running a server-side ImageMagick job.

**Pairs with:** R2 (origin storage for the 'bring your own storage' transformations path, no egress fees), Workers (binding + cf.image fetch transforms, custom auth/rewrite logic), Cloudflare CDN/cache (transformed outputs cached automatically at the edge), Cloudflare Stream (sibling product for video, when GIFs should become MP4/WebM)

**Pricing:** Free plan: up to 5,000 unique transformations/month (over-limit transforms error rather than bill). Paid: Transformations $0.50 / 1,000 unique transformations/month (first 5,000 included); Images Stored $5 / 100,000 images stored/month; Images Delivered $1 / 100,000 images delivered/month. Storage + delivery charges apply only to images hosted in Cloudflare's bucket; transformations of external (e.g. R2/S3) images are billed only on the transformations line. No per-GB egress charge for delivery. (verify — drifts)

**Limits:**
- Hosted upload: max 10 MB/image; remote (transformed) images: max 100 MB.
- Max dimension 12,000 px/side for PNG/JPEG/GIF/WebP; AVIF capped at 1,200 px/side.
- Max area 100 MP (e.g. 10,000x10,000) for static images.
- Animations measured by total MP across frames; >50 MP animations delivered WITHOUT transformations, 100 MP delivery ceiling.
- Input formats: PNG, JPEG, GIF, WebP, SVG, HEIC; AVIF input is Enterprise-only. Output: PNG, JPEG, GIF, WebP, AVIF, SVG.
- SVGs are sanitized and ignore optimization params; progressive JPEG falls back to baseline outside 50x50–3000x3000.
- Hosted-image metadata capped at 1,024 bytes.
- 'Unique transformation' is the billing unit — distinct option-set + source combos; re-serving a cached transform is free.

**Notes:** Honest caveats: (1) Two products under one name — 'Transformations' (works on ANY origin, billed per unique transformation) vs hosted 'Images storage/delivery' (billed for stored + delivered). Don't conflate the pricing lines. (2) Transformations must be explicitly ENABLED per zone in the dashboard (Images > Transformations) before /cdn-cgi/image/ URLs work; the source zone generally needs to be on Cloudflare. (3) Lock-in is moderate for hosted storage (your canonical asset store + URLs live in Cloudflare); the transformations-on-R2/S3 path is lower lock-in since originals stay in your bucket and you can drop back to raw URLs. (4) Not a DAM — no tagging/search/asset-management UI like Cloudinary; it's an optimization+delivery layer, not a media library. (5) AVIF input is Enterprise-only and AVIF output is dimension-limited (1,200 px), so it's not a drop-in for very large AVIF source workflows. (6) For video/GIF-heavy use, Cloudflare steers you to Stream + MP4/WebM rather than animated transforms. (7) The cf.image fetch path requires loop-guarding in the Worker so resize paths don't recursively fetch themselves. Pricing figures fetched 2026-06-15 and are known to drift — re-verify before quoting.

**Docs:** https://developers.cloudflare.com/images/llms.txt, https://developers.cloudflare.com/images/index.md, https://developers.cloudflare.com/images/pricing/index.md, https://developers.cloudflare.com/images/optimization/transformations/overview/index.md, https://developers.cloudflare.com/images/optimization/binding/index.md, https://developers.cloudflare.com/images/optimization/transformations/transform-via-workers/index.md, https://developers.cloudflare.com/images/get-started/limits/index.md

---

## Cloudflare Realtime (RealtimeKit + SFU + TURN)
`cloudflare-realtime` · Realtime media / WebRTC · confidence: `high` · lock-in: `deep`

**Is:** A WebRTC suite that runs the live video/audio plane for you: RealtimeKit (drop-in SDKs + UI for meetings/calls), Realtime SFU (a global media-routing server you drive from your backend), and a managed TURN/STUN relay.

**Replaces:** A self-run WebRTC stack: a SaaS like Agora / Twilio Video (sunset) / Daily / LiveKit Cloud / 100ms, OR self-hosting mediasoup/Janus/Pion SFUs plus your own coturn TURN boxes on autoscaling VMs.

**Use it via:** RealtimeKit backend REST: https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/realtime/kit/{APP_ID}/meetings (create meeting, add_participant to mint a join token, PATCH status INACTIVE). Client SDKs: RealtimeKit UI Kit (recommended) + Core SDK (built on SFU). SFU low-level REST base: https://rtc.live.cloudflare.com/v1/apps/{appId}/... (sessions/new, tracks/new, renegotiate; SDP offer/answer JSON, Bearer App Token, App ID + App Secret from the Realtime dashboard). TURN creds: POST https://rtc.live.cloudflare.com/v1/turn/keys/{TURN_KEY_ID}/credentials/generate-ice-servers, header 'Authorization: Bearer {TURN_KEY_API_TOKEN}', body {"ttl":86400} -> 201 with iceServers[] (stun:stun.cloudflare.com:3478 + turn urls/username/credential). Dashboard: dash.cloudflare.com/?to=/:account/calls.

**Capabilities:**
- RealtimeKit: prebuilt UI Kit + Core SDK for web/mobile that abstracts WebRTC (join/leave, mute, video toggle) for meetings, classrooms, social video
- Backend REST API to manage meetings, participants, presets, recordings, livestreams, sessions, and webhooks for server-side events
- Realtime SFU: low-level WebRTC selective forwarding unit + WebRTC-CDN fanout for broadcast; full control over tracks/sessions, no region/scaling management
- Managed TURN/STUN relay (turn.cloudflare.com) to punch through NAT/firewalls; short-lived credentials via API
- Recording/export to R2 (raw RTP), real-time transcription via Workers AI
- Runs on Cloudflare's global anycast network (hundreds of cities) so media routes to the nearest edge

**Detection signals — the lens fires on these:**
- npm: agora-rtc-sdk-ng, twilio-video, @daily-co/daily-js, livekit-client / livekit-server-sdk, @100mslive/* , mediasoup, mediasoup-client, janode, simple-peer, peerjs
- Go/Pion: github.com/pion/webrtc, pion/turn; Janus or Jitsi (jitsi-meet, lib-jitsi-meet) deployments
- Self-hosted TURN: coturn in a Dockerfile/docker-compose, turnserver.conf, env TURN_SECRET / TURN_SERVER / STUN_URL, hardcoded stun:stun.l.google.com:19302
- Raw RTCPeerConnection + manual ICE/SDP signaling over a websocket server you maintain (Socket.IO 'offer'/'answer'/'ice-candidate' events)
- Env: AGORA_APP_ID/AGORA_APP_CERTIFICATE, TWILIO_API_KEY for video, LIVEKIT_API_KEY/LIVEKIT_API_SECRET, DAILY_API_KEY
- Autoscaling EC2/GKE node groups labeled 'sfu'/'media', regional media-server clusters, custom 'fanout'/'broadcast' relay code
- Recording pipelines that ffmpeg-mux WebRTC tracks and push to S3; a separate transcription worker calling Whisper/Deepgram

**Ideas:**
- Replace a coturn fleet (or hardcoded Google STUN) with Cloudflare's managed TURN — generate short-lived ICE servers from a Worker so credentials never ship to the client statically.
- Swap an Agora/Twilio/Daily integration for RealtimeKit UI Kit to add video calling with prebuilt components, and mint per-participant join tokens from your backend.
- For a custom broadcast/low-latency app, drive Realtime SFU directly (sessions/tracks API) to fan out one publisher to many viewers as a WebRTC-CDN instead of standing up mediasoup.

**Pairs with:** Workers (mint TURN/participant tokens, run signaling at the edge), R2 (store recordings / raw RTP export, no egress fees), Workers AI (real-time transcription), Durable Objects (room/session coordination + presence state alongside the SFU), Stream (for VOD playback of recorded sessions)

**Pricing:** RealtimeKit: free during Beta; at GA $0.002/min per A/V participant, $0.0005/min audio-only; recording/export $0.010/min (A/V), $0.003/min (audio), raw RTP to R2 $0.0005/min; transcription billed as Workers AI. SFU: $0.05 per real-time GB egress with first 1,000 GB/month free. TURN: free when used with Realtime SFU, otherwise $0.05 per real-time GB outbound to the TURN client. Workers AI transcription billed separately. (verify — drifts; product in Beta)

**Limits:**
- RealtimeKit is in Beta (free during beta); GA pricing published but billing model may shift
- TURN alternate ports 53/udp and 80/443 fallbacks: port 53 blocked by many ISPs and browsers — not safe to rely on exclusively
- SFU/TURN are low-level WebRTC; you own SDP/track orchestration unless you use RealtimeKit on top
- Browsers reject the port-53 TURN URL (times out) — must use standard ports for browser clients

**Notes:** Lock-in is moderate: SFU/TURN speak standard WebRTC (SDP/ICE), so the media layer is portable, but RealtimeKit's UI Kit/Core SDK + meeting/participant REST model is proprietary and migrating off it is a rewrite. TURN being free *only* when paired with Realtime SFU is the real hook — standalone TURN still costs $0.05/GB. NOT the right tool for SIP/PSTN telephony (use Twilio/Telnyx) or for simple one-way live streaming where Cloudflare Stream Live (HLS/DASH) is cheaper and simpler than a WebRTC SFU. Verified this run: TURN credential endpoint + ports + pricing (verbatim from generate-credentials and turn pages), SFU $0.05/GB + 1000GB free and rtc.live.cloudflare.com base, RealtimeKit GA per-minute pricing, and the api.cloudflare.com/.../realtime/kit/{APP_ID}/meetings REST shape (from FAQ). NOT fully verified this run: exact SFU sessions/new + tracks/new + renegotiate paths — the get-started page did not surface request/response bodies, so those specific sub-paths are asserted from the documented rtc.live.cloudflare.com/v1/apps/{appId} base and should be confirmed against the SFU API reference before code-gen.

**Docs:** https://developers.cloudflare.com/realtime/llms.txt, https://developers.cloudflare.com/realtime/index.md, https://developers.cloudflare.com/realtime/realtimekit/pricing/index.md, https://developers.cloudflare.com/realtime/sfu/, https://developers.cloudflare.com/realtime/turn/, https://developers.cloudflare.com/realtime/turn/generate-credentials/, https://developers.cloudflare.com/realtime/realtimekit/

---

## Cloudflare Stream
`cloudflare-stream` · Media / Video · confidence: `high` · lock-in: `sticky`

**Is:** A serverless platform to upload, store, encode, and globally deliver on-demand and live video (adaptive-bitrate HLS/DASH) plus a hosted player, signed URLs, thumbnails, and programmatic video transforms — without running any video infrastructure.

**Replaces:** Mux or Cloudinary video (or a DIY pipeline of S3 + ffmpeg transcode workers + an HLS packager + a CDN with egress bills + a third-party player); for live, replaces a self-managed RTMP-to-HLS stack (nginx-rtmp / OvenMediaEngine / AWS MediaLive + MediaPackage).

**Use it via:** Worker binding: wrangler key `[stream]` with `binding = "STREAM"`, accessed as `env.STREAM` — e.g. `env.STREAM.upload(url, {creator, meta, allowedOrigins, watermarkId})`, `env.STREAM.createDirectUpload({maxDurationSeconds})` → `{uploadURL, id}`, and `env.STREAM.video(id).details()/.update()/.delete()/.generateToken()`. Media Transformations is a separate binding `MEDIA`: `env.MEDIA.input(bytes).transform({width,height,fit}).output({...}).response()`. Also a full REST API under `/client/v4/accounts/{account_id}/stream` (live inputs under `/stream/live_inputs`) and tus resumable upload endpoints. Player embed via `<stream>`/iframe + Stream Player API.

**Capabilities:**
- Upload via file, resumable tus, URL pull, or browser Direct Creator Uploads (no API token exposed to client)
- Automatic H.264 encoding to adaptive-bitrate renditions (360p–1080p) for HLS/DASH playback
- Hosted Stream Player (embed) plus playback in any HLS/DASH player on web, iOS, Android, Apple TV
- Live streaming: create a live input, ingest over RTMPS or SRT, multi-resolution encode, auto-reconnect, recordings ready within ~60s of stream end
- Signed URLs / generateToken() for access-controlled video and per-creator analytics
- Media Transformations: resize/crop video (width/height/fit), extract JPEG/PNG thumbnails and spritesheets at a timestamp, transcode to optimized MP4, extract AAC/M4A audio — runnable over video in private R2
- Worker binding for server-side upload and video management without shipping API keys to clients
- Ingress and encoding are always free; bandwidth/egress for delivery is included (no separate egress fee)

**Detection signals — the lens fires on these:**
- npm video stack: `mux`, `@mux/mux-node`, `@mux/mux-player`, `cloudinary` (video), `hls.js`, `dash.js`, `video.js`, `shaka-player`, `@api.video/*`
- Self-hosted transcode: `fluent-ffmpeg`, raw `ffmpeg`/`ffprobe` shelling out, `Dockerfile` running ffmpeg, a queue/worker that produces `.m3u8` / `.ts` HLS segments or `.mpd` DASH manifests
- RTMP/live infra: `nginx-rtmp`, `node-media-server`, OvenMediaEngine, `rtmp://` ingest URLs, AWS MediaLive / MediaPackage / IVS, env vars like `RTMP_URL` / `STREAM_KEY`
- Storage+CDN-for-video shape: large `.mp4` objects in S3/R2/GCS served via CloudFront with an egress line item; a `videos` bucket plus a CDN distribution
- Thumbnail/poster generation: ffmpeg `-ss` frame grabs, sprite-sheet generators, on-the-fly poster image code
- Direct user-upload UGC: presigned S3 PUT for video, `tus-js-client` / `@uppy/tus` for resumable video uploads, a `maxDurationSeconds`-style storage reservation
- Vendor keys: `MUX_TOKEN_ID` / `MUX_TOKEN_SECRET`, `CLOUDINARY_URL`, `API_VIDEO_KEY`

**Ideas:**
- Replace a Mux/Cloudinary + hls.js setup: pull existing MP4s in via `env.STREAM.upload(url)` and swap the frontend to the Stream Player or signed HLS, dropping the transcode worker and egress bill.
- Add creator/UGC video uploads safely: mint one-time `createDirectUpload` URLs (tus for >200MB) from a Worker so the browser uploads straight to Stream without ever seeing an API token.
- Generate poster images / preview thumbnails / audio-only versions on demand with the `MEDIA` transforms binding instead of running ffmpeg jobs — including pulling source video from a private R2 bucket.
- Stand up RTMPS/SRT live streaming with auto-recording by creating a live input via the API, retiring a self-hosted nginx-rtmp/MediaLive pipeline.

**Pairs with:** _n/a_

**Pricing:** Storage: $5 per 1,000 minutes of video stored (prepaid, billed by video duration not file size). Delivery: $1 per 1,000 minutes delivered (usage-based). Ingress and encoding are always free; no separate egress/bandwidth fee. Live is billed identically (storage for recordings + delivery when viewed; a broadcast with no viewers incurs no delivery cost). Media Transformations: free 5,000 unique operations/month, then $0.50 per 1,000 monthly unique operations (billing began Nov 1 2025). No standalone free tier for storage/delivery. (verify — drifts)

**Limits:**
- Encoding output is H.264, adaptive bitrate 360p–1080p (docs do not advertise 4K/AV1/HEVC for general delivery)
- Direct Creator Upload basic POST is capped at 200 MB per file; videos over 200 MB must use the tus resumable protocol
- Live recordings are not instant — available within ~60 seconds after the stream ends (video reaches `ready` state)
- You must pre-declare `maxDurationSeconds` on direct uploads to reserve storage capacity
- Media Transformations metered separately by unique operation; heavy thumbnail/transcode workloads add cost beyond the 5,000/month free grant

**Notes:** Billing by minutes of duration (not GB) makes cost predictable for typical libraries but can be unfavorable for very short or rarely-watched clips where a flat object-storage+CDN setup might be cheaper. Bundled, egress-free delivery is the main pull versus S3+CloudFront or Mux. Trade-off is lock-in: video bytes live inside Stream's managed pipeline (no raw originals bucket you control by default) and playback leans on Stream's HLS/DASH manifests and player, so migrating off means re-ingesting elsewhere. Not the right tool if you need the raw source files as the system of record, exotic codecs/4K HDR delivery, or sub-second-latency live (docs describe HLS/DASH live, not WebRTC-grade real-time). Could not verify in pages fetched this run: explicit low-latency-HLS support, simulcast/restream to YouTube/Twitch, WebVTT caption ingest, MP4 download toggle, or watermark setup details (a `watermarkId` param exists on the binding but its configuration flow was not read).

**Docs:** https://developers.cloudflare.com/stream/llms.txt, https://developers.cloudflare.com/stream/index.md, https://developers.cloudflare.com/stream/pricing/index.md, https://developers.cloudflare.com/stream/stream-live/index.md, https://developers.cloudflare.com/stream/manage-video-library/bindings/index.md, https://developers.cloudflare.com/stream/transform-videos/bindings/index.md, https://developers.cloudflare.com/stream/uploading-videos/direct-creator-uploads/index.md

---

## Media over QUIC (MoQ) at Cloudflare
`moq-live-media` · Live media / real-time streaming transport · confidence: `high` · lock-in: `sticky`

**Is:** An Internet-infrastructure-level live-media delivery service implementing the IETF MoQ Transport protocol over QUIC/WebTransport, giving publish/subscribe low-latency media fan-out on Cloudflare's network — 'like HTTP for content delivery, but for live media.'

**Replaces:** A self-run low-latency live stack: an SFU/relay fleet (mediasoup/Janus/LiveKit) or RTMP-ingest + LL-HLS/DASH packaging + a CDN, or a managed vendor like Mux/Agora/Millicast/Ably for real-time media fan-out.

**Use it via:** Protocol-level, not a Worker binding: clients speak MoQ Transport over a WebTransport (HTTP/3) connection to Cloudflare's MoQ relay. Implements draft-ietf-moq-transport (docs reference both draft-07 and draft-14 message sets). No wrangler key or SDK package documented yet.

**Capabilities:**
- Low-latency live media delivery using QUIC multiplexing + connection migration + 0-RTT
- Publish/subscribe model over MoQ Transport (tracks, subgroups; SUBSCRIBE/ANNOUNCE/PUBLISH_NAMESPACE message families)
- Runs over WebTransport so it works from browsers (Chrome solid; Safari early/flagged as of 18.4)
- Positioned as a relay/CDN for live media rather than a packaging or transcoding product
- Native support for adaptive media qualities/bitrates and resilience to congestion

**Detection signals — the lens fires on these:**
- WebRTC SFU stacks: mediasoup, janus, livekit-server, ion-sfu, pion/webrtc in a service that fans out live A/V
- RTMP ingest + HLS/LL-HLS packaging: nginx-rtmp, ffmpeg piping to .m3u8, shaka-packager, video.js / hls.js players chasing sub-second latency
- Managed real-time-media vendors: mux, @mux/*, agora-rtc-sdk, millicast, dolby.io, ably (for live media), pusher used for media signaling
- WebTransport / QUIC experimentation: code using WebTransport() in the browser or quic-go/quiche on the server for custom media transport
- Self-hosted TURN/relay infrastructure (coturn) for live broadcast fan-out

**Ideas:**
- Prototype sub-second live broadcast (one-to-many) without standing up your own SFU or LL-HLS packaging pipeline
- Use MoQ + WebTransport for interactive low-latency experiences (live auctions, sports, watch-parties) where HLS latency is too high and WebRTC fan-out is too operationally heavy
- Experiment with conferencing/real-time media on a standards-track transport instead of a proprietary SDK

**Pairs with:** Workers, WebTransport / HTTP3, Stream (for non-live VOD), Realtime / Calls

**Pricing:** Not stated in the docs — no pricing or GA terms published; treat as experimental/beta. (verify — drifts)

**Limits:**
- Implements only a subset of the MoQ Transport draft; GOAWAY, FETCH/FETCH_OK/FETCH_ERROR, and SUBSCRIBE_UPDATE are not supported
- Known spec deviation: an extra subscribe_id field in Subgroup Headers (leftover from an older draft, to be fixed)
- Depends on WebTransport — Safari support is early/behind feature flags (improving from Safari 18.4, 2025-03-31)
- MoQ Transport is still an evolving IETF draft; protocol churn likely

**Notes:** Very early and protocol-first: there is no documented Worker binding, SDK, hostname, codec list, or auth model yet — you wire up a MoQ/WebTransport client against the relay. This is bleeding-edge standards work; for production live streaming today, Cloudflare Stream (or a Mux-style vendor) is the safer call. Flag MoQ as a 'watch this / prototype' item, not a drop-in replacement. Browser reach is gated on WebTransport (Safari is the weak link).

**Docs:** https://developers.cloudflare.com/moq/llms.txt, https://developers.cloudflare.com/moq/index.md, https://developers.cloudflare.com/moq/about/index.md, https://developers.cloudflare.com/moq/feature-matrix/index.md

---
