# Community patterns & gotchas

_51 patterns swept from Reddit / Hacker News / dev blogs (21 corroborated as `high`). **These are anecdotes, not documentation** — confidence is tagged on each: `high` = also in official docs or widely corroborated · `medium` = multiple sources · `community` = a single report. The lens may surface `do`/`idea` items as **speculative** and must verify any `gotcha` against live docs before stating it as fact._

## Unconventional architectures (6)

### ✅ do · One SQLite database per user/tenant via Durable Objects
`high` · Durable Objects, D1, Workers

**Takeaway:** On Cloudflare you scale by giving each user/tenant their own DO+SQLite instance instead of sharding one central DB; run migrations in the DO constructor.

Multiple devs and CF's own docs push using a Durable Object (with its embedded SQLite, now GA at 10GB/DO) as a dedicated database per user, per tenant, or per entity, instantiated near that user. Treated as the idiomatic way to 'shard' on CF rather than running one big database. Boris Tane's widely-shared writeups pair it with Drizzle ORM for type-safe per-user DBs. Gotcha surfaced repeatedly: DO SQLite migrations must run in the constructor (runs on cold start when an instance is first hit), and the DO API itself is 'quite verbose,' which is why people build abstractions on top.

Sources: https://boristane.com/blog/durable-objects-database-per-user/ · https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/ · https://developers.cloudflare.com/changelog/2025-04-07-sqlite-in-durable-objects-ga · https://news.ycombinator.com/item?id=34649677

### ✅ do · Durable-Object-per-tenant as the entire backend (DB + compute fused)
`high` · Durable Objects, SQLite in DO, Workers, Drizzle ORM, Hono

**Takeaway:** One Durable Object (with its own SQLite) per tenant/user makes isolation a property of the infrastructure, not a WHERE clause you can forget.

Instead of one shared multi-tenant database with WHERE tenant_id filters, give each user/tenant/graph/document its own Durable Object, each carrying its own embedded SQLite (up to 10GB, GA April 2025). idFromName(tenantId) deterministically routes every request for that tenant to the same globally-unique single-threaded instance, so isolation is infrastructural rather than a policy you can forget to apply (no missing-WHERE data leaks). Boris Tane runs this in production (Basebrain) with Drizzle ORM + Hono; Lambros Petrou (ex-WhatsApp/Erlang actors) calls DOs 'the most underrated' Cloudflare primitive and recommends the pattern whenever 'all your queries have WHERE resourceID='. Heuristic from the community: if every query is scoped to one ID, a DO can probably be that ID. Scales to millions of objects with no capacity planning and scale-to-zero (~$0.20/GB-month storage).

Sources: https://boristane.com/blog/durable-objects-database-per-user/ · https://www.lambrospetrou.com/articles/durable-objects-cloudflare/ · https://blog.cloudflare.com/sqlite-in-durable-objects/ · https://news.ycombinator.com/item?id=25084470

### ✅ do · D1 global read replication via the Sessions API + bookmarks (multi-region consistency trick)
`high` · D1, Durable Objects, SQLite (WAL mode), Workers

**Takeaway:** Pass D1 write 'bookmarks' through your requests and replicas self-delay until caught up - sequential consistency at the edge without pinning clients or routing replicas by hand.

D1 is itself built on SQLite-backed Durable Objects (3 layers: binding -> stateless router Worker -> primary/replica DOs). To get read-your-own-writes across regions without a global lock, D1 uses the Sessions API: every write returns a monotonically increasing 'bookmark' (a Lamport timestamp derived from SQLite's WAL). You thread that bookmark through requests (e.g. an x-d1-bookmark header); a nearby read replica blocks until its WAL has caught up to at least that bookmark before answering, and writes transparently proxy to the single primary. Net effect: sub-ms reads from the nearest replica with sequential consistency, no stale-read foot-guns, no manual replica routing. This is the non-obvious 'how do you get consistency on an edge network where you can't pin a client to a replica' answer.

Sources: https://blog.cloudflare.com/d1-read-replication-beta/

### ✅ do · R2 + R2 Data Catalog (managed Iceberg) + R2 SQL as a zero-egress serverless data lake
`high` · R2, R2 Data Catalog (Apache Iceberg), R2 SQL, Workers, Apache DataFusion

**Takeaway:** R2 + managed Iceberg + R2 SQL is a no-cluster, zero-egress data lake; Iceberg stats prune files up front and ORDER-BY-aligned manifests let LIMIT queries finish early.

R2's zero egress fees make it attractive as the storage layer for an analytics lakehouse. R2 Data Catalog adds a managed Apache Iceberg catalog built into each bucket; R2 SQL is a serverless distributed query engine over it. Architecture: a query planner reads Iceberg manifest/partition/column stats to prune Parquet files before any I/O, a coordinator distributes Parquet row-groups as work units to worker nodes across Cloudflare's network (routed via Argo Smart Routing), each running Apache DataFusion in parallel, streaming results. A neat optimization: manifests are ordered to match the query's ORDER BY so LIMIT...ORDER BY can 'finish early' after scanning a fraction of data. No clusters to provision; others can query your Iceberg tables for free. Limitations (early): ORDER BY only on partition-key columns, filter-queries first with aggregations added later (Jan 2026), less tunable than full Iceberg.

Sources: https://blog.cloudflare.com/r2-sql-deep-dive/ · https://blog.cloudflare.com/r2-data-catalog-public-beta/ · https://www.infoq.com/news/2026/01/cloudflare-r2-sql-aggregations/

### 💡 idea · Transactional DB on object storage via DO coordination + conditional writes (R2/S3) — cross-object txns are the wall
`community` · Durable Objects, R2, Workers

**Takeaway:** DO-as-single-writer over R2 objects can give cheap transactional storage, but single-object only — cross-object/table transactions are the unsolved hard part.

The 'Transactional Object Storage' thread explored building serializable databases directly on object storage, with Durable Objects as the single-writer/coordination layer over data partitioned across R2/S3 objects. Patterns: conditional/precondition writes + transaction logs (GlassDB), MVCC with a light coordinator (Delta Lake), single-writer batched flush to cut S3 costs (SlateDB), KV-then-SQL layering (CockroachDB pattern). Recurring hard limit: transactions ACROSS objects/tables remain unsolved in most designs; strict-serializable readers must re-validate against storage (latency tax); S3 only recently gained conditional writes (GCS/R2 better here). An interesting-but-sharp-edged architecture.

Sources: https://news.ycombinator.com/item?id=42164058

### 💡 idea · On-demand graph databases as 'one DO per graph' with SQLite + BFS in the actor
`community` · Durable Objects, SQLite in DO, Workers, Hono

**Takeaway:** You can fake an on-demand graph DB with one DO per graph (SQLite nodes/edges + in-actor BFS) - elegant for small isolated graphs, but no cross-graph queries and 10GB/DO ceiling.

An experimental-but-functional pattern from Boris Tane: spin up an isolated graph database on demand by addressing a new Durable Object per graphId (idFromName) - 'creating a new database is as simple as an HTTP request with a new identifier.' Each DO's embedded SQLite holds a nodes table (JSON blobs) and an edges table (composite unique key on source,target,relationship with directional indexes); graph traversal (shortest path / reachability) is done with breadth-first search in the single-threaded DO using a visited set. Zero provisioning, automatic per-graph isolation, scale-to-zero. Explicitly scoped by the author: good for thousands-to-tens-of-thousands of nodes (10GB/DO cap), no cross-graph queries or distributed transactions, cold-start on first hit, and no built-in backup (you must write export logic). Framed as ideal for agent memory / multi-tenant graphs, not as a Neo4j replacement.

Sources: https://boristane.com/blog/durable-objects-graph-databases/


## Clever product combos (6)

### ✅ do · Durable Objects = SQLite-per-object actor: strong consistency + data locality (the canonical pattern)
`high` · Durable Objects, Workers

**Takeaway:** Reach for a DO-per-key actor when you need serialized, strongly-consistent per-entity state (rate limits, rooms, sessions, state machines) — not for general SQL workloads.

DO threads repeatedly frame Durable Objects as single-threaded virtual actors (compared to Microsoft Orleans, EJB Entity Beans, Erlang actors) that co-locate compute with strongly-consistent state, now with embedded SQLite per object. The endorsed sweet spot: coordination primitives — rate limiting / API usage caps via one DO per key, chat rooms, multiplayer/collab session state, per-entity state machines — where you want serialized access and strong consistency without a separate DB. Skeptics note it's 'nothing new under the sun' conceptually, but that's framed as healthy context, not a warning against use.

Sources: https://news.ycombinator.com/item?id=44143669 · https://news.ycombinator.com/item?id=32996261

### ✅ do · WebSocket + state co-located in one DO per room/entity (PartyKit pattern)
`high` · Durable Objects, WebSockets, SQLite in DO, PartyKit/PartyServer, Workers

**Takeaway:** Put the socket and the authoritative state in the same per-room DO; the single thread is your built-in conflict resolver, but deploys drop connections so handle reconnect.

The canonical realtime pattern: one Durable Object per room/list/game/match handles BOTH the WebSocket fan-out AND the authoritative state (now via embedded SQLite), because a DO is the only way to reliably reach the specific instance holding a given client's socket. PartyKit/PartyServer (now Cloudflare) productize exactly this: a 'Party' = a DO, routed by ID. Used for chat, collaborative lists (Show HN 'Online List Maker': each list = a DO doing socket + SQLite), and multiplayer game servers where clients propose actions over WS and the DO validates+broadcasts authoritative state. Single-threaded execution gives a free serialization point for conflict resolution. Caveat raised in HN 'Durable Objects in Production': because DOs are long-lived, every deploy disconnects clients, so you must build client-side reconnection.

Sources: https://docs.partykit.io/how-partykit-works/ · https://news.ycombinator.com/item?id=46675386 · https://www.astahmer.dev/posts/multiplayer-state-machine-with-durable-objects/ · https://news.ycombinator.com/item?id=25084470

### 💡 idea · Workers AI free tier as a zero-infra LLM/Whisper/embeddings backend
`medium` · Workers AI, Workers, KV

**Takeaway:** Workers AI's free 10k-neuron/day tier is a viable zero-infra LLM/Whisper/embeddings backend for prototypes, but mind neuron-limit errors and context/retry/KV cost inflation at scale.

People use Workers AI as a free, no-credit-card edge AI backend for side projects: 10,000 neurons/day (~roughly 100-300 text generations, varies by model) covers prototyping, plus Whisper for speech-to-text, LLaVA for image understanding, and embeddings — all behind one binding with no GPU to manage, and it's wired up as a custom LLM for tools like ElevenLabs. Surprises to watch: users hit '4006 daily free neuron limit exceeded' (sometimes while the dashboard shows 0 usage) and report billing/charge confusion; analyses warn the real cost inflators on paid are context-window overages, retries, and KV ops around RAG, not the headline token price.

Sources: https://developers.cloudflare.com/workers-ai/platform/pricing/ · https://elevenlabs.io/docs/agents-platform/customization/llm/custom-llm/cloudflare · https://community.cloudflare.com/t/workers-ai-returns-4006-daily-free-neuron-limit-exceeded-while-dashboard-shows-0/909187 · https://dev.to/0012303/cloudflare-workers-ai-has-a-free-api-run-ai-models-at-the-edge-with-zero-infrastructure-2ibo

### ✅ do · Single-writer Durable Object as the consistency guard for an async AI/RAG indexing pipeline (AutoRAG)
`medium` · Workers AI, Vectorize, R2, Durable Objects, AI Gateway, AutoRAG

**Takeaway:** A globally-unique DO doubles as a distributed lock/leader-elector - AutoRAG uses one to guarantee a single concurrent indexer per RAG so the vector store can't be raced.

Cloudflare's AutoRAG (managed RAG: R2 source -> convert to markdown -> chunk -> embed via Workers AI -> store vectors in Vectorize, original in R2, AI Gateway for caching/analytics) uses Durable Objects under the hood for coordination, not storage: a 'JobManager' DO runs a full sync (queue files, embed, keep Vectorize current) and a 'RagManager' enforces that only ONE JobManager exists per RAG at a time. The non-obvious lesson: DOs' globally-unique single-instance guarantee is being used as a distributed mutex/leader-election to prevent concurrent indexers from racing and corrupting the vector index. This generalizes - any 'exactly one worker may touch this resource right now' problem maps cleanly onto a DO. Practitioner gotcha with AutoRAG itself: indexing silently fails on oversized files and unsupported formats.

Sources: https://community.cloudflare.com/t/ai-search-vectorize-create-fully-managed-rag-pipelines-for-your-ai-applications-with-autorag/819614 · https://annjose.com/post/cloudflare-autorag-step-by-step/ · https://developers.cloudflare.com/workers-ai/guides/tutorials/build-a-retrieval-augmented-generation-ai/

### 💡 idea · R2 + rclone/restic as a self-hosted Dropbox/backup target
`community` · R2

**Takeaway:** R2's zero-egress + S3 API makes it a cheap rclone/restic backup and self-hosted file-sync target where restores are free — use restic/rclone-crypt for snapshotting/encryption semantics instead of assuming S3 versioning/Object Lock.

In selfhosted circles R2 is a popular cloud backup/sync target precisely because of zero egress: mount a bucket locally with `rclone mount` or push encrypted backups via rclone crypt / restic against R2's S3 API, getting global CDN delivery and free restores (no egress charge to pull your data back). Used as a cheap Dropbox-for-photos / media-library tier and offsite backup. The catch versus B2/S3 is the R2 feature gaps above: Cloudflare-native Bucket Locks exist, but S3 bucket versioning APIs and S3 Object Lock APIs/headers do not; auth/placement semantics differ from AWS. People layer restic's snapshotting or rclone crypt on top for backup history, integrity, and encryption.

Sources: https://rclone.org/ · https://dev.to/viiik/how-to-make-easy-encrypted-backups-with-rclone-for-free-1i18 · https://dev.to/medrix/rclone-cloudflare-r2-and-nginx-reverse-proxy-509b

### ✅ do · Workers' 6-concurrent-outbound-connection limit; Cloudflare engineer's workaround is 'farm it across Durable Objects'
`community` · Workers, Durable Objects

**Takeaway:** Hitting the ~6 outbound-connection cap in a Worker? Fan the requests out across multiple Durable Objects to multiply your connection budget.

In the agents/AI-platform thread, developers flagged the Workers limit of ~6 simultaneous outbound connections as a real constraint for fan-out/agent workloads. A Cloudflare engineer's confirmed-but-undocumented workaround: distribute the outbound work across multiple Durable Objects (each gets its own connection budget) to raise effective concurrency. Useful, non-obvious scaling trick — with the caveat that it's officially undocumented.

Sources: https://news.ycombinator.com/item?id=47792538


## Cost & migration stories (7)

### ✅ do · R2 zero-egress as an S3-compatible replacement (huge bandwidth savings)
`high` · R2, Workers

**Takeaway:** For egress-heavy media/asset/registry serving, R2's zero egress + S3-compatible API can cut bandwidth cost by 50-97%, but validate S3 feature gaps before calling it drop-in.

The most repeated 'I replaced X with Cloudflare Y' story: move bandwidth-heavy object workloads from S3 to R2 to kill egress fees. Reported outcomes range from an indie dev whose bill 'became $0,' to a team taking ~$30k/yr off bandwidth by fronting CloudFront with Cloudflare, to ~60x cited savings; OpenTofu runs its provider/module registry on R2. R2 is S3-API-compatible so rclone/restic and most S3 tooling work with an endpoint swap, but it is not S3-identical: validate unsupported S3 APIs, auth semantics, object-lock/versioning expectations, and cache behavior before promising a drop-in migration. Migration friction noted: leaving AWS now incurs its own egress toll (e.g. ~$24 for 250GB), and Glacier Deep Archive can still beat R2 for cold archival.

Sources: https://news.ycombinator.com/item?id=42256771 · https://news.ycombinator.com/item?id=40612437 · https://developers.cloudflare.com/r2/pricing/ · https://blog.cloudflare.com/using-cloudflare-r2-as-an-apt-yum-repository

### ✅ do · R2's zero egress flips media/download economics vs S3 (1M×1GB: ~$0.13 vs ~$59k)
`high` · R2

**Takeaway:** For egress-heavy workloads (media, public downloads, AI datasets), R2's zero egress is a step-change vs S3; use Sippy for gradual cutover.

Across multiple HN threads on S3→R2 migration, the recurring driver is egress. One widely-cited comparison: 1 million 1GB downloads costs ~13¢ in R2 egress vs ~$59,247 on AWS S3. Users report saving $2–3k/month moving off S3/DigitalOcean Spaces for media hosting, backups, and data-pipeline/AI-dataset serving. Cloudflare's Sippy tool enables incremental migration so you only pay source egress for objects actually read. Community treats this as the genuine, real value prop — but specifically for egress-heavy, frequently-accessed data.

Sources: https://news.ycombinator.com/item?id=38118577 · https://news.ycombinator.com/item?id=37888135 · https://news.ycombinator.com/item?id=38118991

### ⚠️ avoid · Durable Objects bill WALL-CLOCK duration — an idle WebSocket meters money
`high` · Durable Objects

**Takeaway:** DO charges wall-clock time while active; a plain accept()'d WebSocket bills 24/7 even when idle — use the WebSocket Hibernation API or pay for dead air.

Unlike Workers (CPU-time billing), Durable Objects bill compute duration in wall-clock time whenever the object is active and not eligible for hibernation. The sharp edge: calling WebSocket.accept() in a DO keeps it 'active' and billing for the entire time the connection is open, even when totally idle — so a few thousand long-lived idle sockets can quietly rack up GB-s charges. The mitigation that surprises people is mandatory for cost control: use the WebSocket Hibernation API so the object can evict from memory between messages and stop the duration clock while keeping the connection alive.

Sources: https://developers.cloudflare.com/durable-objects/platform/pricing · https://github.com/cloudflare/cloudflare-docs/blob/production/src/content/partials/durable-objects/durable-objects-pricing.mdx · https://blog.ashleypeacock.co.uk/p/the-ultimate-guide-to-cloudflares

### ✅ do · Durable Objects replacing Redis for rate limiting / counters
`medium` · Durable Objects, Workers

**Takeaway:** A Durable Object is a strongly-consistent edge counter that can replace a Redis rate-limiter with lower latency and cost, at the price of Cloudflare lock-in.

Recurring 'I ditched Redis for Durable Objects' pattern (DEV/DZone writeups, corroborated by CF building its own Queues on DOs rather than Kafka/Pulsar). A ThrottlerDO holds counter state at the edge; one team reported rate-limit checks dropping from 80-150ms (Redis, network round-trip + geographic distance) to under 5ms, running at ~30% of prior Redis cost while serving 10x more requests, and removing Redis as a single point of failure. Caveat the authors themselves note: DO has no cross-platform portability beyond Cloudflare and no complex query ability — it's a coordination primitive, not a Redis feature-superset.

Sources: https://dev.to/horushe/why-i-ditched-redis-for-cloudflare-durable-objects-in-my-rate-limiter-jof · https://dzone.com/articles/why-ditch-redis-for-cloudflare-durable-objects · https://news.ycombinator.com/item?id=34649677

### 💡 idea · R2 via the Worker binding double-bills: Worker invocation + R2 Class A/B ops
`medium` · R2, Workers

**Takeaway:** R2 kills egress fees but the Worker binding bills invocation + Class A/B ops on top — watch list operations (Class A) on big buckets, not just storage.

R2's headline draw is zero egress fees, but accessing it through the in-Worker binding charges you twice — Worker invocation/CPU time AND the R2 Class A (writes/lists/deletes, ~$4.50/M) or Class B (reads) operation. An AMA commenter noted this can make Class B ops nearly 2x more expensive than S3 on a per-op basis (Cloudflare counters that Workers+R2 still beats Lambda+S3 overall, and you save the egress). The practical surprises: list operations are Class A and add up fast on large buckets (listObjectsV2 over many keys), and per-request Worker overhead stacks on top. Budget for operation counts and minimize listing, not just storage GB.

Sources: https://news.ycombinator.com/item?id=31340296 · https://markaicode.com/pricing/cloudflare-workers-pricing-breakdown/ · https://developers.cloudflare.com/r2/reference/durability/

### ⚠️ avoid · KV write costs (10x reads) are the line item that ambushes the bill
`medium` · Workers KV

**Takeaway:** KV writes cost ~10x reads (~$5 vs ~$0.50/M) — writing to KV on every request is a cost anti-pattern; KV is for write-rarely/read-often data.

The most common Cloudflare billing surprise practitioners report is KV write pricing: ~$5 per million writes vs ~$0.50 per million reads — roughly 10-16x. Teams reach for KV as a general-purpose session store or cache and write on every request (touch-on-read sessions, per-request counters, analytics), then get a 'hundreds of dollars in KV writes' bill before realizing the read/write asymmetry. The lens-worthy rule: KV is priced for read-heavy, write-rarely data. If you write on most requests, that's a smell — batch writes, move hot mutable state to a Durable Object, or rethink whether KV is the right store at all.

Sources: https://markaicode.com/pricing/cloudflare-workers-pricing-breakdown/ · https://developers.cloudflare.com/workers/platform/pricing/ · https://makerkit.dev/pricing-calculator/cloudflare

### ⚠️ avoid · Workers AI's $0.30/M-token rate hides an egress/traffic trap
`community` · Workers AI

**Takeaway:** Workers AI's cheap token rate is undercut by egress charges and paying full price for truncated over-context prompts — model traffic + prompt size, not just $/token.

Workers AI advertises low per-token pricing (around $0.30 per 1M tokens for some models), but practitioners warn the real cost isn't the token rate — it's data egress and traffic leaving Cloudflare's edge, where a single egress spike was reported adding ~$450 to a monthly bill. A second silent inflator: if prompt+completion exceeds a model's context window it can be truncated, yet you still pay for the full prompt tokens every request — reportedly inflating token spend up to ~60% on verbose RAG pipelines. Treat the token price as a starting point, model your egress and RAG prompt sizes, and watch context-overflow truncation.

Sources: https://markaicode.com/pricing/cloudflare-workers-pricing-breakdown/ · https://www.truefoundry.com/blog/cloudflare-ai-gateway-pricing-a-complete-breakdown


## Tips (5)

### ✅ do · KV as the edge feature-flag / runtime-config store (write-rarely, read-everywhere)
`medium` · Workers KV, Workers

**Takeaway:** KV is the right home for feature flags/edge config (write-rarely/read-everywhere) - but it's eventually consistent, so never treat it as a read-your-writes database.

KV's eventually-consistent, read-optimized model (hot reads <5ms at edge) is a textbook fit for feature flags, A/B variants, and redirect/config rules: written rarely, read on nearly every request, and you flip behavior globally without a redeploy. Multiple OSS projects build on exactly this (TwoFlags, CloudFlags as minimalist Workers+KV flag services; the LaunchDarkly Node SDK can swap its in-memory store for KV; Spotify's Confidence ships a Cloudflare/KV edge resolver). Critical caveat surfaced by practitioners: KV is eventually consistent (writes can take time to propagate to all edges) and is a Redis-like KV store, NOT a NoSQL database replacement - don't use it where you need read-your-writes or relational queries (reach for D1/DO there).

Sources: https://workers.cloudflare.com/product/kv · https://confidence.spotify.com/docs/sdks/edge/cloudflare · https://github.com/aprets/cloudflags · https://blog.intenics.io/cloudflare-workers-first-impression/

### ✅ do · Full-stack-in-one-Worker (API + frontend + DB), but skip Terraform/Pulumi for the Worker itself
`medium` · Workers, D1, R2, Static Assets, Wrangler, Miniflare, Prisma

**Takeaway:** Serve frontend+API+DB from one Worker and lean on Miniflare for local dev - but configure the Worker with Wrangler, not Terraform/Pulumi, and expect D1+Prisma migration friction.

Firsthand 3-day full-stack build (Angular SPA + Hono REST API + D1 via Prisma + R2 + TOTP auth) all served from a single Worker - static assets don't need a separate Worker, the same backend Worker serves both UI and API. Wins: Miniflare local dev is a 'first-class citizen' that cut reliance on deploys; whole stack shipped in 3 days. Concrete warnings: (1) 'Using Pulumi or Terraform for Cloudflare Workers is a bad idea' - use Wrangler for the Worker and reserve IaC only for supporting infra (R2/D1/domains); (2) D1 is still 'very new', docs are 'a moving target', and Prisma migrations needed workarounds; (3) Cloudflare's coarse permissions vs AWS IAM may block strict-compliance enterprises. Echoes the broader 2026 momentum of Cloudflare positioning Workers as a single-deploy full-stack target (e.g. Payload CMS ported entirely onto Workers+D1+R2 with custom adapters).

Sources: https://blog.intenics.io/cloudflare-workers-first-impression/ · https://blog.cloudflare.com/payload-cms-workers/ · https://blog.cloudflare.com/full-stack-development-on-cloudflare-workers/

### ✅ do · KV cold reads are slow; the fast numbers assume a warm, regionally-hot key
`medium` · Workers KV

**Takeaway:** KV is fast for hot keys but cold reads walk to central storage and blow up tail latency — use SWR + single-flight, never serial KV waterfalls (Promise.all), and don't size SLAs off the p50 number.

KV's marketing latency assumes a cached/hot key read near where it's already popular. A cold read (first access in a region, or an unpopular key) must walk from the nearest regional tier down to central storage, so the first hit globally is materially slower and tail latency (p95/p99) diverges from p50. Practitioners on the forums report 'poor' read performance when keys aren't hot. Mitigations the community uses: keep p95 near p50 with stale-while-revalidate, single-flight to avoid thundering-herd refreshes, push refresh/writes into ctx.waitUntil() so they don't block the response, and parallelize independent reads with Promise.all instead of serial waterfalls. (Cloudflare shipped KV perf improvements in 2025, but cold-read asymmetry remains the mental model.)

Sources: https://developers.cloudflare.com/kv/concepts/how-kv-works/ · https://community.cloudflare.com/t/kv-read-performance-poor/566207 · https://developers.cloudflare.com/changelog/2025-08-22-kv-performance-improvements/

### ✅ do · Practical D1 query tricks: Smart Placement, KV read-cache, batch inserts, CTEs over JOIN-loops, avoid OFFSET
`community` · D1, Workers KV, Workers

**Takeaway:** To make D1 usable: turn on Smart Placement, front reads with KV, batch writes, collapse round-trips into CTEs, and use cursor (not OFFSET) pagination.

In the same D1 optimization thread, practitioners shared concrete mitigations that helped: enable Smart Placement so the Worker runs near the DB's primary region (cut latency for several users); aggressively cache read-heavy data in Workers KV; batch INSERTs instead of row-by-row; replace multiple round-trip queries with a single CTE rather than N queries + JOINs; and avoid OFFSET-based pagination (use keyset/cursor). Treated as the working playbook to make D1 viable.

Sources: https://news.ycombinator.com/item?id=43572511

### 💡 idea · Workers AI free tier is real and abusable: image-gen demos hit KV read limits, sustainability unclear
`community` · Workers AI, Workers KV

**Takeaway:** Workers AI free tier is great for shipping AI demos cheaply, but watch KV read limits and add your own content filtering — don't count on free-tier economics lasting.

The 'Free image generation on Workers AI' Show HN had the builder running a public image generator entirely on the Workers AI free tier, openly unsure 'how long it will last.' Practical gotchas surfaced: the app bumped into Workers KV read limits (needed a quota bump), and prompt-safety/sentiment filtering needed fixing (NSFW/edge outputs slipped through). Pattern: Workers AI is a cheap/free way to ship AI demos fast, but KV read limits and content-filtering are the early walls, and free-tier economics aren't guaranteed.

Sources: https://news.ycombinator.com/item?id=38459481


## Gotchas (verify before you rely on these) (19)

### ✅ do · WebSocket Hibernation: keep sockets open without paying for idle time
`high` · Durable Objects, Workers

**Takeaway:** Always use the WebSocket Hibernation API for DO realtime apps; plain DO WebSockets bill for the whole connection duration even while idle.

The non-obvious win that makes DO viable for chat/multiplayer/collab: with the Hibernation API the client stays connected to Cloudflare's edge while the DO is evicted from memory, so you only pay wall-clock compute when a message actually arrives (e.g. a chat tab open 30 min with no traffic costs nothing). Before hibernation (pre-Sept 2023), basic WebSockets billed duration for the entire connection, which several devs said pushed them to polling instead. Use serializeAttachment/deserializeAttachment to survive eviction.

Sources: https://developers.cloudflare.com/durable-objects/best-practices/websockets · https://thomasgauvin.com/writing/how-cloudflare-durable-objects-websocket-hibernation-works/ · https://news.ycombinator.com/item?id=39942364 · https://news.ycombinator.com/item?id=38893425

### ⚠️ avoid · Workers KV is more stale than 'eventually consistent' implies
`high` · KV, Durable Objects

**Takeaway:** Never rely on Workers KV for read-after-write or write-hot data; its cache can serve stale values for 10-60s even to the same client — use a Durable Object for consistency.

Devs warn KV's staleness bites harder than the docs suggest: stale reads 'often by 10 seconds at least,' and crucially the stale value persists even for the same client that just wrote, unless they add their own caching — because reads hit a per-PoP cache with ~60s TTL, negative (key-miss) lookups are cached too, and write ordering isn't guaranteed. Workarounds people resort to: explicit caching plus hand-rolled reconciliation/cache-invalidation, or moving the consistency-sensitive piece to a Durable Object. Consensus: KV is great for read-heavy, rarely-changing config/assets, but a bad fit for read-after-write or write-heavy (same key many times/sec) workloads.

Sources: https://news.ycombinator.com/item?id=30875542 · https://developers.cloudflare.com/kv/concepts/how-kv-works/ · https://community.cloudflare.com/t/kv-store-eventual-consistency/85664

### ⚠️ avoid · WebSocket apps on Durable Objects WILL surprise-bill you unless you use Hibernation
`high` · Durable Objects, WebSocket Hibernation API, Workers

**Takeaway:** On DO WebSockets, the connection itself is billable wall-clock time; always use the Hibernation API or idle rooms quietly drain your budget.

DOs bill on request count AND wall-clock duration (unlike Workers' CPU-only pricing). Calling accept() on a WebSocket keeps the DO 'in memory' and billable for the ENTIRE time the socket is connected, even with zero messages. Community math: a mostly-idle chat-room DO can cost ~$5/month each just to hold the connection open, so 100 rooms ≈ $500/mo; a realtime collab app with persistent sockets easily runs $20-50/mo in DO duration charges. The fix is the WebSocket Hibernation API, which evicts the DO from memory between messages while keeping the socket alive, so you stop paying for idle duration and only wake on actual events. This concern dates back to the 2020 'Durable Objects in Production' HN thread, where even Cloudflare staff admitted naive duration billing 'wouldn't work very well' for sockets.

Sources: https://github.com/trpc/trpc/discussions/4400 · https://community.cloudflare.com/t/is-my-understanding-of-the-websockets-pricing-model-correct/384366 · https://news.ycombinator.com/item?id=25084470 · https://blog.cloudflare.com/sqlite-in-durable-objects/

### ⚠️ avoid · KV is eventually consistent: writes take up to ~60s to propagate globally
`high` · Workers KV

**Takeaway:** KV is read-optimized and eventually consistent (~60s) — never use it where you must read your own write immediately; use DO or D1 for that.

Workers KV does not give read-after-write consistency. A write made in one location can take up to ~60 seconds before edge caches everywhere reflect it, and a write read back immediately from a different colo (or even the same one) may return the old value. The community repeatedly warns against using KV for anything that requires a value to be correct immediately after writing (counters, session invalidation, locks, 'just-wrote-it' reads). Use Durable Objects or D1 when you need strong/read-after-write consistency; reserve KV for read-heavy data that tolerates staleness (config, feature flags, cached API responses).

Sources: https://developers.cloudflare.com/kv/concepts/how-kv-works/ · https://community.cloudflare.com/t/about-workers-kv-concurrency-limit-for-writing-the-same-key/315119

### ⚠️ avoid · A single Durable Object is single-threaded (~soft 1k req/s) — shard hot objects
`high` · Durable Objects

**Takeaway:** One DO = one thread (~1k req/s soft cap); CPU-bound work and long serialized sections hurt everyone on that object — shard hot keys instead of making one mega-object.

Each Durable Object is single-threaded and cooperatively scheduled (like browser JS), so all requests to one object share one execution context. The practical soft ceiling is on the order of hundreds to ~1,000 requests/second for simple ops, and far less if each request does real CPU work or holds serialized state too long. The classic trap is funneling a hot workload (a global counter, a popular chat room, a leaderboard) through ONE object and hitting a wall. Async I/O can yield, but CPU-bound work and long critical sections still stall progress for that object. The fix the community and Cloudflare both endorse is horizontal sharding — spread load across many objects (e.g. Cloudflare's own Queues team sharded DOs for a 10x throughput gain).

Sources: https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/ · https://blog.cloudflare.com/how-we-built-cloudflare-queues/ · https://developers.cloudflare.com/durable-objects/reference/faq

### ⚠️ avoid · D1's 10GB-per-database cap is hard AND there's no split/migrate path
`high` · D1

**Takeaway:** D1 caps at 10GB/database with no later split or migrate — design per-tenant/per-entity sharding upfront or you'll hit a wall you can't refactor out of.

Each D1 database is capped at 10GB and once you hit it, writes fail. Production teams stress that the 10GB number itself isn't the real problem — it's that D1 gives you no mechanism to split, grow, or transparently stitch a database after creation. You cannot shard an existing DB later, so the cap forces an upfront 'database-per-tenant/user/entity' architecture or a painful manual re-shard. Teams that adopted D1 early (one ran 421+ databases since alpha) describe outgrowing it and building custom sharding (one scaled to 500GB across ~50 DBs manually). Plan the sharding key from day one; D1 is built for many small DBs, not one big one.

Sources: https://sushidata.com/blog/2026/05/19/outgrew-cloudflare-d1-everything-tried-building-solution/ · https://medium.com/@tristantrommer/scaling-cloudflare-d1-from-10-gb-to-500-gb-with-manual-database-sharding-4e95d6deb742 · https://developers.cloudflare.com/d1/platform/limits

### ⚠️ avoid · D1 read replicas are async — without the Sessions API you get stale reads
`high` · D1

**Takeaway:** Turning on D1 read replicas without using the Sessions API (bookmarks) gives you read-your-writes bugs — thread the session token through every related query.

D1 read replication asynchronously copies from the primary to replicas, so any replica can be 'arbitrarily out of date' and routing to replicas is non-deterministic. The canonical bug: user places an order (write to primary) then loads their orders page (read served by a lagging replica) and the new order is missing. The fix is the Sessions API, which attaches a bookmark to each query so a session reads a sequentially-consistent version even across different replicas — but you must actually thread the session/bookmark through, and mixing replicas within one logical session breaks the guarantee. Treat replicas as a read-latency optimization that requires the Sessions API to stay correct.

Sources: https://developers.cloudflare.com/d1/best-practices/read-replication/ · https://blog.cloudflare.com/d1-read-replication-beta/ · https://community.cloudflare.com/t/d1-workers-d1-read-replication-public-beta/819595

### ⚠️ avoid · Workers measure CPU time, not wall time — but 128MB RAM is the real killer
`high` · Workers

**Takeaway:** Workers count CPU (not I/O wait) time, and the 128MB RAM cap OOMs on surprisingly small files — stream with TransformStream instead of buffering, and look for sync blocking on CPU errors.

Two intertwined limits trip people up. (1) Workers bill/limit CPU time (default 30s, up to 5min on paid, 10ms on free); time spent awaiting fetch/KV/D1 does NOT count, so 'CPU exceeded' (Error 1102/1107) almost always means synchronous code blocking the event loop, not slow I/O. (2) The hard 128MB memory ceiling is what actually crashes file-processing Workers: a 20MB upload can OOM because toArrayBuffer makes a 20MB copy and base64 adds another ~27MB, and when a request pushes past 128MB the runtime may cancel requests. The universal fix is the Streams API (TransformStream) to process multi-GB payloads incrementally instead of buffering. Don't buffer whole files; stream them.

Sources: https://medium.com/@morphinewan_37034/when-a-20mb-file-crashed-my-cloudflare-worker-an-indie-developers-memory-management-nightmare-1fc6d52ce46b · https://developers.cloudflare.com/workers/platform/limits/ · https://developers.cloudflare.com/workers/runtime-apis/streams

### ⚠️ avoid · Cloudflare Queues are at-least-once — duplicates WILL happen, build idempotent consumers
`high` · Queues

**Takeaway:** Queues redeliver on crash/timeout even after successful processing — make every consumer idempotent with a unique message ID / dedup key from day one.

Queues guarantee at-least-once delivery, meaning a message can be delivered more than once: a consumer crash, network failure, or ack timeout triggers redelivery even when your processing already succeeded (you just didn't ack in time). The trap is assuming exactly-once and doing non-idempotent side effects (charge a card, send an email, INSERT a row) directly in the consumer. The community's day-one rule: generate a unique message ID at produce time and use it as a DB primary key or idempotency/dedup key so reprocessing the same message is a no-op. 'Exactly-once' on Queues is something you engineer on top via dedup, not a platform guarantee.

Sources: https://developers.cloudflare.com/queues/reference/delivery-guarantees/ · https://github.com/cloudflare/cloudflare-docs/blob/production/src/content/docs/queues/reference/how-queues-works.mdx · https://architectingoncloudflare.com/chapter-08/

### ✅ do · R2 IS strongly consistent — but putting a cache in front silently breaks that
`high` · R2

**Takeaway:** R2 is strongly consistent (incl. list/delete) so you can read your own writes — but caching it (Cache API/CDN) trades that away; consistency then lives in your cache-control headers.

Contrary to the usual object-store assumption, R2 is strongly/read-after-write consistent: read-after-write, metadata, deletes, and even object listing reflect the latest state immediately and globally (only IAM key changes are eventually consistent, up to ~1 min). The non-obvious trap, called out by an R2 engineer in an AMA, is that the moment you layer Cache API / CDN caching in front of an R2 bucket for performance, you give up that strong consistency — freshness now depends entirely on your cache-control headers, not R2. So the gotcha is reversed from S3: R2 itself is safe to read-after-write, but your own caching layer is what reintroduces staleness.

Sources: https://developers.cloudflare.com/r2/reference/consistency · https://news.ycombinator.com/item?id=31340296

### ⚠️ avoid · DO WebSocket message billing (20:1) and the million-connection cost cliff
`medium` · Durable Objects, Workers

**Takeaway:** DO realtime is cheap at small/medium scale but high-fanout, high-message-rate workloads (≈1M connections) can be ~20x the cost of one rented box — model it and batch messages.

Even with hibernation, people get bitten by the request side: incoming WS messages bill at 1/20 of a request (100 messages = 5 billed requests), and a 4-byte message costs the same as a large one — so chatty collaborative-editing payloads need artificial batching. An Ask HN cost model for 1M persistent connections at 1 msg/min penciled out to ~$1,015/mo on CF DO ($324 requests + $686 compute duration) versus ~€40/mo for a single 6-core/64GB Hetzner box, prompting a migration. CF engineer kentonv confirms the 1/20 ratio and hibernation as the mitigations; community advice is to load-test on a cheap VPS rather than trust either estimate.

Sources: https://news.ycombinator.com/item?id=40216236 · https://news.ycombinator.com/item?id=39942364 · https://developers.cloudflare.com/durable-objects/platform/pricing

### ⚠️ avoid · R2's sharp edges vs S3: S3 API gaps, Cloudflare auth model, and cache semantics
`medium` · R2

**Takeaway:** R2 is S3-compatible, not S3-identical: Range is supported directly, but versioning/Object Lock APIs, AWS IAM assumptions, placement, replication, and cache behavior still need validation before critical migrations.

Counterweight to the R2 hype, from devs who hit walls. Older community reports mention HTTP Range surprises, but the current R2 S3 compatibility docs list GetObject Range support; if video scrubbing/resumable downloads fail now, first check whether a CDN/custom-domain cache layer is returning stale or un-ranged responses. Official gaps that remain: S3 bucket versioning APIs and S3 Object Lock APIs/headers are not implemented, while Cloudflare-native Bucket Locks are a separate retention feature. R2 access is via Cloudflare API tokens / S3 credentials rather than AWS IAM, and data placement is controlled with Location Hints or Jurisdictional Restrictions rather than arbitrary AWS regions. Enterprise/security-sensitive and data-lake-throughput workloads should validate the exact S3 APIs, auth boundaries, retention, replication, and caching path before migrating.

Sources: https://news.ycombinator.com/item?id=42256771 · https://developers.cloudflare.com/r2/api/s3/api/ · https://developers.cloudflare.com/r2/buckets/bucket-locks/ · https://developers.cloudflare.com/r2/reference/data-location/ · https://developers.cloudflare.com/r2/reference/consistency/

### ⚠️ avoid · D1's 10GB-per-database wall forces a sharding mindset
`medium` · D1, Hyperdrive

**Takeaway:** D1 caps each database at 10GB by design — architect for many sharded per-tenant databases up front, or plan a manual split/export/import or exit to Hyperdrive/Postgres.

Devs evaluating D1 for production repeatedly trip on the 10GB max database size and ask how it's usable at scale. CF's intended answer (and the community's): D1 isn't one big DB — it's meant to be sharded into many small (per-user/per-tenant/per-entity) databases, with thousands of DBs at no extra cost (limit ~50,000 on paid, increases not guaranteed). There is no transparent 'grow this one DB past 10GB' path; teams that do not design for sharding face a manual split/export/import or migration to Hyperdrive+Postgres/external DB once a tenant outgrows one DB. Same architectural shape as the per-user-DO pattern.

Sources: https://www.answeroverflow.com/m/1345869029906059305 · https://developers.cloudflare.com/d1/platform/limits · https://dev.to/araldhafeeri/scaling-your-cloudflare-d1-database-from-the-10-gb-limit-to-tbs-4a16

### ⚠️ avoid · R2 is not S3-identical for enterprise buckets: versioning/Object Lock APIs, IAM model, audit, replication
`medium` · R2

**Takeaway:** Don't treat R2 as exact S3: Cloudflare Bucket Locks and IA storage exist, but S3 versioning/Object Lock APIs, AWS IAM assumptions, audit/replication needs, and unsupported S3 features still decide compliance migrations.

Same R2 threads carry consistent warnings, but the current docs need more precise wording. Cloudflare-native Bucket Locks exist for retention/WORM-style protection and Infrequent Access exists for a cheaper storage class, so 'no object lock/tiering' is stale. What remains true: R2's S3-compatible API does not implement S3 bucket versioning APIs or S3 Object Lock APIs/headers, AWS IAM policy assumptions do not carry over directly, and teams should validate audit, replication, object tagging/ACL/request-payer gaps, custom-domain requirements, and workload-specific latency/throughput. Verdict: great for hot data needing egress savings; for deep archival, same-region AWS compute, or compliance programs built around exact S3 controls, verify before migrating.

Sources: https://news.ycombinator.com/item?id=38118577 · https://news.ycombinator.com/item?id=33453104 · https://developers.cloudflare.com/r2/buckets/bucket-locks/ · https://developers.cloudflare.com/r2/api/s3/api/ · https://developers.cloudflare.com/r2/pricing/

### ⚠️ avoid · D1 single-primary-region latency bites: 200–500ms+ reads from far edges, no edge result cache
`medium` · D1

**Takeaway:** D1 has a single primary/write path; beta read replicas can help reads only when enabled and used through Sessions/bookmarks. Do not assume 'edge DB' means low global latency by default.

The 'Optimize D1 Queries' thread surfaced multiple year-plus production reports of high latency: 400ms+ (spiking >500ms) for simple queries, 200ms+ from North America, and 300–3000ms vs 50–100ms on DigitalOcean Postgres. Root cause is architectural: a D1 DB has a single primary/write path, so writes and non-replicated reads can round-trip to that region, and D1 does not provide a generic edge result cache. D1 now has public-beta read replication through the Sessions API, but that must be enabled and used with bookmarks to avoid stale-read foot-guns. Community consensus: D1 fits small, low-complexity, read-light projects more naturally than latency-sensitive global write-heavy apps.

Sources: https://news.ycombinator.com/item?id=43572511 · https://news.ycombinator.com/item?id=47792538

### ⚠️ avoid · The Cloudflare REST API rate limit (~1200 req / 5 min) throttles D1-via-REST at scale
`medium` · D1, Cloudflare API

**Takeaway:** Driving D1 through the REST API hits a ~1200 req/5min account cap and extra control-plane hops — use native Workers bindings for hot paths, not REST.

Teams driving D1 (or other resources) through the Cloudflare REST API instead of native Workers bindings hit the global account API limit of ~1,200 requests per 5 minutes — one team reported exhausting it in '10 to 20 seconds of normal production load' and needing manual escalation to 9,000+. Compounding it, REST D1 queries historically routed through a centralized control plane (e.g. PDX), adding ~4 extra network hops and hundreds of ms vs. a direct binding. Lesson: prefer native bindings over the REST API for hot-path data access, and if you must use REST, expect to request limit increases early and eat extra latency.

Sources: https://sushidata.com/blog/2026/05/19/outgrew-cloudflare-d1-everything-tried-building-solution/ · https://developers.cloudflare.com/changelog/2025-05-30-d1-rest-api-latency

### ⚠️ avoid · Dzero: 'Supabase for SQLite' on D1 — historical warning about hand-managed replication claims
`community` · D1, R2

**Takeaway:** Scrutinize 'globally distributed SQLite' claims: official D1 read replication is beta and Sessions/bookmark-based; DIY file duplication is not the same consistency model, and D1's 10GB/database cap still applies.

Show HN Dzero layers a dashboard + API over Cloudflare D1, pitching globally distributed SQLite by duplicating the SQLite file across R2/S3 instances. At the time of the thread, the author conceded D1 had no read replicas, so '320 edge locations' meant duplicated files and manually managed consistency. Official D1 has since added public-beta read replication via the Sessions API, so treat the old 'no read replicas' criticism as historical; the useful warning is still to scrutinize consistency guarantees and distinguish official Sessions/bookmarks from DIY storage duplication. The 10GB/DB cap remains an architecture constraint.

Sources: https://news.ycombinator.com/item?id=40563729

### 💡 idea · Workers AI as an agent inference layer: edge network is the edge, but no spend caps and thin LoRA/fine-tune support
`community` · Workers AI, Workers, Agents SDK

**Takeaway:** Workers AI wins on edge networking + unified API, but expect weak fine-tune/LoRA support and no hard spend cap — budget-guard it yourself.

On the 'AI platform for agents' thread, Workers AI is positioned vs OpenRouter as more than an API proxy thanks to Cloudflare's Argo networking + edge distribution, unifying edge-hosted and proxied models under one API/billing. Criticisms: despite the Replicate acquisition there's no scalable deployment of app-specific fine-tunes — 'the only models supporting LoRA are year-old dense models,' pushing one team to keep a personal GPU rack; no spending cap / budget control unlike OpenAI/Google (only daily-spend limits confirmed); and unified billing adds modest fees. Reliability bleed-over from D1 (hanging queries) and poor human support escalation also cited (one $45k/yr customer leaving).

Sources: https://news.ycombinator.com/item?id=47792538 · https://news.ycombinator.com/item?id=43963121

### ⚠️ avoid · Workers-for-Platforms scripts can 'brick' themselves by running out of CPU
`community` · Workers, Workers for Platforms

**Takeaway:** On Workers for Platforms, a tenant script that runs out of CPU can wedge itself — design tenant isolation and recovery, don't assume clean failure.

An edge-case but instructive failure: in Workers for Platforms, a user/tenant Worker that exhausts its CPU time can get into a state where it bricks itself and keeps failing, rather than cleanly recovering — surfaced as a GitHub issue against workers-sdk. The broader lesson for multi-tenant 'run untrusted/customer code' architectures on Workers is that per-script resource exhaustion needs defensive handling (limits, isolation, recovery/redeploy paths) because a single tenant burning CPU shouldn't be able to wedge itself or noisy-neighbor others. Treat CPU limits as a failure mode to design around in platform scenarios, not just a billing knob.

Sources: https://github.com/cloudflare/workers-sdk/issues/11629


## Anti-patterns (don't do this) (8)

### ⚠️ avoid · KV limits you to ~1 write per second to the SAME key (429s above that)
`high` · Workers KV

**Takeaway:** One hot KV key = ~1 write/sec ceiling; don't build counters or rate limiters on a single KV key — shard the key space or use a Durable Object.

KV supports effectively unlimited reads and writes across DIFFERENT keys, but writes to a single key are throttled to roughly one per second; hammering the same key returns rate-limit (429) errors and silently drops the consistency story. This bites people who build counters or rate-limiters in KV: a per-key counter physically cannot increment more than ~once/second, so a 'max 100 req/sec' limiter backed by one KV key can never actually observe more than ~60/min. Mitigation: consolidate multiple writes within one invocation into a single write, spread load across many keys (sharding), or use Durable Objects for hot single-key counters.

Sources: https://developers.cloudflare.com/kv/api/write-key-value-pairs/ · https://community.cloudflare.com/t/regarding-kv-write-up-to-one-write-per-second-per-key/173951 · https://helloacm.com/a-simple-rate-limiter-for-cloudflare-workers-serverless-api-based-on-kv-stores/

### ⚠️ avoid · Don't trust Worker global/module state — isolates get evicted without notice
`high` · Workers

**Takeaway:** Worker global state is a cache you can lose at any moment, not storage — only put cheap-to-rebuild immutables there; real state goes in DO/KV/D1.

A Worker's global scope can persist between requests, but only as a best-effort performance optimization, never a guarantee: isolates are evicted for resource pressure or limits at any time, so a global variable set in one request 'may or may not' exist in the next. The anti-pattern is using module-global maps/variables for an in-memory cache, counter, session store, or lock and assuming durability — it works in dev and low traffic, then silently loses data under load or after deploys. Safe rule: globals are fine for expensive immutable init (parsed config, compiled regex, reused clients) where loss just means cheap recompute; anything stateful that must survive belongs in Durable Objects, KV, or D1.

Sources: https://developers.cloudflare.com/workers/reference/how-workers-works/ · https://developers.cloudflare.com/workers/best-practices/workers-best-practices/ · https://architectingoncloudflare.com/chapter-03/

### ⚠️ avoid · Shipping a Worker with no rate limiting = surprise bill from bots
`medium` · Workers, D1

**Takeaway:** Put rate limiting (WAF rule or DO counter) and billing alerts on any public usage-priced Worker before launch — a bot flood can run up overage costs fast.

Cautionary anecdote that recurs: an unprotected Worker API took 500k requests in 2 hours (bot), overwhelmed the attached D1 and triggered overage charges; author estimated $500+ exposure, fixed by ~10 lines doing 100 req/min/IP returning HTTP 429. Generalizes the well-known Vercel/Netlify 'six-figure static-site bill' fear to CF: usage-priced edge compute + DB makes a public endpoint a financial-DoS target. Community remedies: CF's native rate-limiting / WAF rules, a Durable-Object counter, and setting billing caps/alerts before launch.

Sources: https://dev.to/aserrano/how-rate-limiting-saved-me-500-in-one-day-real-story-ajp · https://www.saashub.com/alternatives/post-news-ycombinator-2024-02-26-netlify-just-sent-me-a-104k-bill-for-a-simple-static-site-2352837

### ⚠️ avoid · D1 in production: no real interactive transactions, queries hang for seconds, hard to shard per-tenant
`medium` · D1

**Takeaway:** Validate transactions, the 10GB cap, and multi-tenant sharding DX before betting a production platform on D1.

Beyond latency, commenters across two threads flag D1 production gaps: missing/limited interactive transaction support (a 'critical gap'), queries occasionally hanging for several seconds up to double digits, the 10GB-per-database ceiling, and inability to download the full SQLite file for larger DBs (data-portability/lock-in concern). Per-user/per-tenant sharding is theoretically attractive but has poor DX — you must explicitly bind each DB into the Worker with no built-in multi-tenancy. Net: usable for small apps, painful to scale into a serious multi-tenant platform without Cloudflare lock-in.

Sources: https://news.ycombinator.com/item?id=47792538 · https://news.ycombinator.com/item?id=40563729

### ⚠️ avoid · Single-threaded DO is a hot-shard risk: don't route a high-traffic resource to one object
`medium` · Durable Objects, Workers KV

**Takeaway:** A single-threaded DO serializes all its requests, so never funnel a hot, high-fan-in resource through one object - pick a key that spreads load, or use KV for low-latency reads.

The flip side of 'one DO per resource': a DO executes single-threaded, and when a request causes side-effects (storage reads/writes) all other requests to that same DO instance block until it completes. So a popular shared object (a global counter, a single 'project' DO that every user hits, one mega-chat-room) becomes a throughput bottleneck and a hot shard - per-instance throughput is finite. The community guidance is to choose the DO key so load naturally fans out (per user, per channel, per match) rather than funneling everyone through one well-known ID, and to use the few-second in-memory residency window for caching. Strong consistency and world-wide-low-latency are described as 'fundamentally opposed' - DOs give you the former; reach for KV when you actually want the latter.

Sources: https://www.lambrospetrou.com/articles/durable-objects-cloudflare/ · https://news.ycombinator.com/item?id=25084470

### ⚠️ avoid · KV list() is slow/expensive and is not a query engine
`medium` · Workers KV

**Takeaway:** Don't use KV.list() to query or enumerate data — it's paginated, slow, and billable; keep an explicit index key or use D1.

KV.list() paginates at 1000 keys per call with cursors, is explicitly called out by practitioners as 'slow and expensive, should be avoided in hot paths,' and prefix listing can even return mismatches across pagination boundaries. People treat KV like a database and list-scan it to 'find' records or check freshness, which both runs up list-operation costs and adds latency. One team traced a 93% cost overrun to a single endpoint that listed an entire namespace to check snapshot freshness. KV is a key-value cache, not something to iterate for queries — store an index/summary key or use D1 for anything you need to filter or enumerate.

Sources: https://developers.cloudflare.com/kv/api/list-keys/ · https://ef-map.com/blog/cloudflare-kv-optimization-93-percent · https://community.cloudflare.com/t/kv-list-with-prefix-includes-mismatches-when-paginating/516969

### ⚠️ avoid · D1 is one single-location SQLite actor — chatty queries pay per round trip
`medium` · D1, Workers

**Takeaway:** D1 lives in one place and charges a round trip per query — batch() your statements and watch DB-to-Worker distance; N+1 query patterns are brutal on D1.

Every D1 database is a single actor in one region with one thread, and all writes route back to that single primary for consistency. Practitioners report simple queries averaging 200ms+ and spiking to 1500ms when the Worker is far from the DB, and note that Smart Placement can paradoxically hurt (moving compute toward the DB sometimes raised latency vs. leaving it off). The killer anti-pattern is N+1 / many small sequential queries, each paying a network round trip; the fix is batch() (multiple statements in one round trip, executed atomically). For two years the batch REST capability was even undocumented, silently forcing people into slow sequential calls. Co-locate, batch aggressively, and don't assume edge = low latency for D1.

Sources: https://rxliuli.com/blog/journey-to-optimize-cloudflare-d1-database-queries/ · https://community.cloudflare.com/t/d1-latency-very-high-for-queries-and-api-wrangler/735047 · https://architectingoncloudflare.com/chapter-12/

### ⚠️ avoid · Durable Objects are a persistence layer, not a workflow engine — DIY Temporal at your peril
`community` · Durable Objects, Workers

**Takeaway:** Don't hand-roll durable workflow orchestration on raw DOs; use alarms+xstate for simple cases, or a real workflow engine (Temporal / CF Workflows) for complex ones.

In the 'DOs for long-running stuff' thread, the consensus caution: a DO is 'just a persistence layer' and lacks workflow-engine features (durable scheduling, state-machine semantics, introspection, analytics, signals, batch transactions). Teams building long-running orchestration on DOs end up reinventing a workflow engine unknowingly. A viable small-team hybrid was shared — DO/Workers alarms for scheduling + xstate for state + custom DB writes for analytics — accepting less sophistication for a lower learning curve than Temporal. For complex/long-running workflows, a dedicated engine (Temporal) or Cloudflare Workflows is the better fit.

Sources: https://news.ycombinator.com/item?id=34691915

