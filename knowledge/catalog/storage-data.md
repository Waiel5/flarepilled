# Storage, Databases & Data

_7 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Cloudflare Artifacts
`artifacts` · Versioned storage / Git-compatible object store · confidence: `high` · lock-in: `sticky`

**Is:** Durable, versioned file-tree storage that 'speaks Git' — create repos programmatically, push/pull from any standard Git client, and read commits/trees from a Workers binding or REST API, with synchronous multi-region replication handled for you.

**Replaces:** Standing up and babysitting your own Git server (Gitea/GitLab on a VM with replication + backups), or bolting versioning onto a raw blob store (R2/S3) by hand — especially for agent/automation workflows that need branches, diffs, and forks.

**Use it via:** Worker binding `ARTIFACTS` configured in wrangler.jsonc as an `artifacts` array ({ binding: 'ARTIFACTS', namespace: 'default' }), typed as `Artifacts`. Namespace methods: create/get/list/import/delete. Repo-handle methods: createToken/listTokens/revokeToken, fork, log, readCommit, readTree. Plus a REST API and a Git smart-HTTP protocol endpoint for normal git clients.

**Capabilities:**
- Stores versioned file trees behind a Git-compatible interface (full git history + refs per repo)
- Same repo reachable three ways: Workers binding, REST API, and standard Git clients (clone/fetch/pull/push)
- Programmatic repo lifecycle: create, import existing repos, fork from a baseline, then diff/merge
- Read git objects from a Worker: log(), readCommit(hash), readTree(hash)
- Repo-scoped token auth with read (clone/fetch/pull) vs write (push/mutations) scopes, minted by your Worker/API
- Durable by default: synchronous replication across multiple data centers + async copy to object storage and snapshots; Cloudflare runs the whole Git server lifecycle

**Detection signals — the lens fires on these:**
- Self-hosted Git: gitea, gogs, gitlab-runner, a bare repo served over SSH, or a Dockerfile running a git server
- isomorphic-git / nodegit / simple-git used to programmatically create/clone/commit repos in app code or agents
- Build/automation pipelines that snapshot working trees into S3/R2 tarballs and reinvent versioning
- Agent frameworks that need isolated per-task workspaces with branch/fork/diff semantics (e.g. coding agents)
- AWS_ACCESS_KEY_ID / S3 buckets used as a poor-man's versioned file store with manual revision keys
- wrangler.jsonc already present (Workers shop) + a need to hand work to 'Git-aware tools, agents, and automation'

**Ideas:**
- Give each coding-agent task its own forkable repo so parallel runs are isolated and results can be diffed/merged
- Replace a self-hosted Gitea/GitLab box used purely as programmatic storage with managed, multi-region-replicated repos
- Store versioned config/state file-trees (instead of raw blobs) and hand a Git URL to existing CI/CD and review tooling

**Pairs with:** Workers, R2, Durable Objects, Sandbox SDK / coding agents, CI/CD git tooling

**Pricing:** No free tier (requires Workers Paid). Operations: first 10,000/mo free-of-charge within plan, then $0.15 per additional 1,000 operations. Storage: first 1 GB-mo included, then $0.50 per additional GB-mo (averaged over 30-day cycle; replicated copies not charged extra). (verify — drifts)

**Limits:**
- Currently in closed beta (access by request form)
- Max storage per repository: 10 GB
- Max storage per account: 1 TB (raisable on request)
- Control-plane rate: 2,000 requests / 10s per namespace; Git request rate: 2,000 requests / 10s per artifact
- Naming: namespace/repo names must start with a letter or digit; remaining chars letters/digits/./_/-
- No free tier — requires a Workers Paid plan

**Notes:** Despite the name, this is NOT a build-artifact/container-image/package registry — docs are explicit it manages versioned file trees and Git workflows, not raw CI blobs or OCI images (use R2 for raw blobs, a registry for images). The killer use case is agent/automation workspaces (fork/diff/merge). Closed-beta + Workers-Paid-only today, so gate any recommendation on beta access. Lock-in: repos live in Cloudflare, but the Git-compatible interface makes egress (git clone elsewhere) straightforward.

**Docs:** https://developers.cloudflare.com/artifacts/llms.txt, https://developers.cloudflare.com/artifacts/index.md, https://developers.cloudflare.com/artifacts/concepts/how-artifacts-works/index.md, https://developers.cloudflare.com/artifacts/api/workers-binding/index.md, https://developers.cloudflare.com/artifacts/platform/pricing/index.md, https://developers.cloudflare.com/artifacts/platform/limits/index.md

---

## Cloudflare D1
`d1` · Database · confidence: `high` · lock-in: `sticky`

**Is:** Cloudflare's managed, serverless SQLite-semantics database queried directly from Workers and Pages via a binding or HTTP API, with point-in-time recovery and global read replication.

**Replaces:** A managed Postgres/MySQL instance (RDS, Neon, PlanetScale, Supabase) plus its connection-pooling layer — or a self-hosted SQLite/libSQL box — for a Workers-resident app backend.

**Use it via:** Worker binding env.DB (type D1Database) configured via wrangler `d1_databases` array (binding / database_name / database_id) in wrangler.jsonc or [[d1_databases]] in wrangler.toml. Methods: db.prepare(sql).bind(...).run()/.all()/.first()/.raw(), db.batch([...]), db.exec(), db.withSession(). CLI: `wrangler d1 create`, `wrangler d1 execute --local|--remote --file= / --command=`. REST: POST /accounts/{account_id}/d1/database (and /query subresource).

**Capabilities:**
- Serverless relational SQL database with SQLite SQL semantics, no connection strings or pooling to manage
- Direct Worker/Pages binding (env.DB) plus prepared statements with parameter binding
- Batch transactions (db.batch([...])) and raw SQL exec for migrations/bulk DDL
- Time Travel: point-in-time restore to any minute within the last 30 days (built-in disaster recovery)
- Global read replication via the Sessions API (db.withSession()) to cut read latency across regions
- Create thousands of isolated databases per account at no extra cost (per-tenant / per-customer DB-per-user patterns)
- Import/export of SQL and bulk data; query from dashboard, Wrangler CLI, or REST
- Billed only on queries (rows read/written) and storage — idle databases cost only storage

**Detection signals — the lens fires on these:**
- Deps: better-sqlite3, sqlite3, sql.js, @libsql/client, libsql, drizzle-orm + drizzle-orm/d1, kysely (d1 dialect), prisma + @prisma/adapter-d1
- A bundled SQLite file in the repo: *.sqlite, *.sqlite3, *.db, data.db, app.db
- Postgres/MySQL client deps paired with a Workers/Pages app: pg, postgres, mysql2, @neondatabase/serverless, @planetscale/database, @supabase/supabase-js
- Env vars for an external DB: DATABASE_URL, POSTGRES_URL, PG_CONNECTION_STRING, MYSQL_HOST, PLANETSCALE_*, SUPABASE_URL
- Connection-pooling shims (pgbouncer config, serverless-pg pool wrappers) added to work around edge/serverless connection limits
- wrangler.toml/wrangler.jsonc already present (Workers/Pages project) but persistence handled by an outside SQL host
- Hand-rolled per-tenant database provisioning logic (one SQLite/Postgres DB per customer)
- A separate cron/job doing SQL dumps for backup that Time Travel would replace

**Ideas:**
- Move a Workers app's relational data off an external Postgres/Neon instance into D1 to kill the connection string, pooling layer, and cross-region read latency.
- Use database-per-tenant (thousands of free isolated D1 DBs) for a multi-tenant SaaS or a vibe-coding/app-builder platform instead of row-level tenant isolation in one big DB.
- Replace a nightly SQL-dump backup cron with built-in Time Travel 30-day point-in-time restore, and add read replicas via the Sessions API for read-heavy endpoints.

**Pairs with:** Cloudflare Workers / Pages (the compute that binds D1), Workers KV (hot key-value cache in front of D1 reads), R2 (large blobs/files that exceed the 2 MB row limit — store in R2, keep keys in D1), Durable Objects (strongly-consistent per-entity coordination alongside D1's relational store), Hyperdrive (the alternative when you must keep an existing external Postgres/MySQL rather than migrate to D1), Drizzle ORM / Kysely / Prisma (D1 adapters)

**Pricing:** Free plan: 5M rows read/day, 100k rows written/day, 5 GB total storage. Workers Paid: first 25B rows read/mo, 50M rows written/mo, 5 GB storage included; overage $0.001/M rows read, $1.00/M rows written, $0.75/GB-month storage. Billed on queries (rows read/written) + storage only — not compute/duration. (verify — drifts)

**Limits:**
- Max database size: 500 MB (Free) / 10 GB (Paid, non-increasable)
- Databases per account: 10 (Free) / 50,000 (Paid, can request more)
- Storage per account: 5 GB (Free) / 1 TB (Paid, can request more)
- Max 100 columns per table; max 100 bound parameters per query
- Max SQL statement length 100 KB; max string/BLOB/row size 2 MB
- Max query duration 30s; queries per Worker invocation 50 (Free) / 1,000 (Paid); max 6 simultaneous DB connections per Worker invocation
- Max `wrangler d1 execute` import file size 5 GB

**Notes:** SQLite semantics, not Postgres — no native pgvector, limited concurrent-write throughput, single-primary writes (replicas are read-only and eventually consistent). The 10 GB hard per-database cap is non-increasable, so very large single datasets must shard across databases or live elsewhere. 2 MB max row/BLOB size means large files belong in R2. Lock-in: data lives in Cloudflare and is reached via the Worker binding / D1 REST API; portability is eased by standard SQLite SQL + export, but app code couples to the binding. If you need to keep an existing external SQL database, Hyperdrive (not D1) is the right tool. Read-replication and per-row billing model verified from pricing/limits pages fetched this run.

**Docs:** https://developers.cloudflare.com/d1/llms.txt, https://developers.cloudflare.com/d1/index.md, https://developers.cloudflare.com/d1/platform/pricing/index.md, https://developers.cloudflare.com/d1/platform/limits/index.md, https://developers.cloudflare.com/d1/worker-api/index.md, https://developers.cloudflare.com/d1/get-started/index.md

---

## Cloudflare Hyperdrive
`hyperdrive` · Database / Data access · confidence: `high` · lock-in: `sticky`

**Is:** A Worker binding that makes your existing regional Postgres or MySQL database feel fast from the edge by pooling connections near the origin and caching read queries.

**Replaces:** A self-hosted connection pooler (PgBouncer/RDS Proxy) plus a hand-rolled read-through cache (a Redis box in front of the DB) that you stand up to survive serverless connection storms and round-trip latency.

**Use it via:** Worker binding env.HYPERDRIVE exposing .connectionString (and .host/.user/.password/.database/.port for mysql2). Config created with `npx wrangler hyperdrive create <NAME> --connection-string="postgres://..."`, then bound in wrangler.jsonc under "hyperdrive": [{ "binding": "HYPERDRIVE", "id": "<DB_ID>" }]. Caching toggled with `--caching-disabled true`.

**Capabilities:**
- Edge-side connection setup so the TLS/auth handshake happens near the Worker instead of across the ocean to your DB
- Connection pooling in transaction mode, with the pool placed in region(s) closest to your origin DB (reuses warm connections, avoids exhausting Postgres max_connections from many isolates)
- Default-on query caching of non-mutating read queries (default max_age 60s, stale_while_revalidate 15s, max_age cap 1 hour)
- Automatic read/write detection: only SELECTs are cached; INSERT/UPDATE/DELETE/DDL and volatile/stable functions (NOW(), RANDOM(), CURRENT_TIMESTAMP) bypass cache
- Drop-in with existing drivers and ORMs (node-postgres, postgres.js, mysql2, Drizzle) — no query rewrites
- Works with any Postgres/MySQL host: AWS/GCP/Azure managed DBs, Neon, PlanetScale, plus Postgres-compatible CockroachDB and Timescale
- No data-transfer/egress charges for queries through Hyperdrive

**Detection signals — the lens fires on these:**
- A Worker/Pages project (wrangler.jsonc / wrangler.toml present) that imports `pg`, `postgres`, `mysql2`, or `drizzle-orm` and connects straight to a remote DATABASE_URL
- Env vars like DATABASE_URL, PG_CONNECTION_STRING, POSTGRES_URL, NEON_DATABASE_URL, PLANETSCALE/Supabase connection strings used inside edge/serverless handlers
- Self-managed pooler infrastructure: pgbouncer.ini, a PgBouncer/Supavisor container, or AWS RDS Proxy / `rds-proxy` in IaC
- A Redis/Upstash cache sitting in front of Postgres purely to memoize hot read queries (REDIS_URL + a cache-read-then-DB-read pattern around SELECTs)
- Comments or code about 'connection exhaustion', 'too many connections', max_connections tuning, or per-request `new Client()` in a serverless function
- Cron/queue workers re-opening DB connections on every invocation against a regional Postgres/MySQL from Workers

**Ideas:**
- Front an existing Neon/Supabase/RDS Postgres with Hyperdrive so the Worker stops opening a fresh connection per request and read-heavy endpoints get cached for free
- Replace a Redis read-cache that only memoizes SELECTs with Hyperdrive's built-in query cache (tune max_age per binding, or use a second binding with --caching-disabled for fresh reads)
- Drop a PgBouncer/RDS Proxy box you run solely to absorb serverless connection storms and point the driver at env.HYPERDRIVE.connectionString instead

**Pairs with:** Cloudflare Workers, D1 (when you want a CF-native SQLite DB instead of an external one), Smart Placement (run the Worker near the origin DB to cut uncached round-trips)

**Pricing:** Included free on both Free and Paid Workers plans; no per-query or egress charge for the cache/pooling. You pay in query volume: Free = 100,000 DB queries/day (resets 00:00 UTC), Paid = unlimited. A 'query' counts SELECT, INSERT/UPDATE/DELETE, and DDL equally. (verify — drifts)

**Limits:**
- Configs: 10 per account (Free) / 25 per account (Paid)
- Origin DB connections per config: ~20 (Free) / ~100 (Paid)
- Max query duration 60s; idle connection timeout 10 min; connection start timeout 15s
- Max cached response size 50 MB; query cache max_age default 60s, capped at 1 hour, stale_while_revalidate 15s
- Username and database name each capped at 63 bytes

**Notes:** It accelerates EXISTING external Postgres/MySQL — it is not a database itself (use D1 for that) and won't help if your data already lives in a CF-native store. Caching is opt-out and only helps read-heavy workloads with tolerance for up-to-60s staleness; write-heavy or strongly-consistent paths see pooling benefit but no cache benefit. Pooler is transaction-mode, so session-level features (LISTEN/NOTIFY, session advisory locks, some named prepared-statement patterns) may not behave as on a direct connection — I could not verify the exact unsupported-feature list from the limits/caching pages fetched this run. You still pay your DB provider's own hosting + egress; Hyperdrive only waives CF-side data-transfer charges.

**Docs:** https://developers.cloudflare.com/hyperdrive/llms.txt, https://developers.cloudflare.com/hyperdrive/index.md, https://developers.cloudflare.com/hyperdrive/concepts/how-hyperdrive-works/index.md, https://developers.cloudflare.com/hyperdrive/concepts/query-caching/index.md, https://developers.cloudflare.com/hyperdrive/platform/pricing/index.md, https://developers.cloudflare.com/hyperdrive/platform/limits/index.md, https://developers.cloudflare.com/hyperdrive/get-started/index.md

---

## Cloudflare Pipelines
`pipelines` · Data / Streaming ETL · confidence: `high` · lock-in: `sticky`

**Is:** A serverless streaming-data platform that ingests events over HTTP or a Worker binding, transforms them with SQL, and lands them in R2 as JSON, Parquet, or Apache Iceberg tables.

**Replaces:** A self-hosted Kafka + Flink/Spark Streaming + S3 sink stack (or a Kinesis Firehose / Confluent + a custom Parquet-writer Lambda) for getting clickstream/log/event data into a queryable lake.

**Use it via:** Worker binding: `pipelines` array in wrangler.jsonc with `{ "binding": "STREAM", "stream": "<STREAM_ID>" }`, then `await env.STREAM.send([{...}])`. HTTP: POST JSON array to `https://{stream-id}.ingest.cloudflare.com` with `Content-Type: application/json` and optional `Authorization: Bearer <token>`. SQL transform: `INSERT INTO <sink> SELECT ... FROM <stream>`. CLI: `wrangler pipelines ...` (streams / sinks / pipelines subcommands). Also REST API + Terraform Cloudflare provider.

**Capabilities:**
- Streams: durable, buffered ingestion queues that accept events via HTTP endpoint or Workers binding; optional schema (structured streams enforce field types, unstructured accept any JSON)
- Pipelines: SQL transformation layer (INSERT INTO sink SELECT ... FROM stream WHERE ...) to filter, reshape, cast, unnest, and enrich events at ingest time
- Sinks: write to R2 as JSON or Parquet files, or to R2 Data Catalog as managed Apache Iceberg tables
- Worker binding exposes env.<BINDING>.send(records) returning a Promise that resolves when records are confirmed ingested
- HTTP ingestion endpoint with optional Bearer-token auth (Workers Pipeline Send permission)
- Rich scalar SQL function library (string, math, regex, JSON, struct, array, hashing, time/date) per the SQL reference
- Logpush can be wired in as a stream source to land Cloudflare product logs in R2
- Metrics for data ingested/processed/delivered via dashboard or GraphQL analytics API
- Managed via Wrangler CLI, REST API, and the Cloudflare Terraform provider

**Detection signals — the lens fires on these:**
- kafkajs / node-rdkafka / @confluentinc/kafka-javascript in package.json, or a docker-compose with kafka/zookeeper/redpanda
- AWS Kinesis Firehose / @aws-sdk/client-firehose, or kinesis-related env vars, feeding an S3 bucket
- A Lambda/worker that buffers events and writes Parquet (parquetjs, pyarrow, fastparquet, parquet-wasm) batches to object storage on a timer
- Self-managed Flink / Spark Structured Streaming jobs whose only job is filter+reshape+land-to-S3
- Apache Iceberg writer code (pyiceberg, iceberg-rust, Glue/Nessie catalog config) maintaining tables by hand
- Clickstream/analytics ingestion endpoints batching events to S3/GCS for later Athena/BigQuery querying (AWS_ACCESS_KEY_ID, S3_BUCKET, ATHENA_*, BIGQUERY_*)
- Cron jobs that roll up app/access logs into dated Parquet/NDJSON files for a data lake
- Segment/RudderStack/Snowplow collectors used purely to fan events into a warehouse/lake
- A Worker already POSTing event JSON to an external collector that could instead call env.<binding>.send()

**Ideas:**
- Replace a Kinesis Firehose -> S3 -> Parquet clickstream pipeline: POST events to a Pipelines stream and write Iceberg tables in R2 Data Catalog, then query with R2 SQL / DuckDB / Spark with no egress fees.
- From an existing Worker, call env.STREAM.send([...]) on each request to capture analytics/audit events, and use a SQL transform to drop bots and PII before they ever hit storage.
- Point Cloudflare Logpush at a Pipelines stream to land HTTP/WAF/Workers logs as Iceberg tables in R2 for cheap long-term log analytics instead of paying a SIEM/Datadog for retention.

**Pairs with:** R2 (object storage destination; no egress fees), R2 Data Catalog (managed Apache Iceberg catalog for the Iceberg sink), R2 SQL (serverless query engine over the Iceberg tables Pipelines writes; $2.50/TB scanned), Workers (producer side via the pipelines binding), Logpush (as a stream source for Cloudflare product logs), External Iceberg readers: DuckDB, Spark, Snowflake, PyIceberg

**Pricing:** Open beta; pricing published May 2026 but billing NOT yet enabled (30 days notice promised before charging). Ingress (streams) is free regardless of volume. SQL transforms: $0.04/GB (stateless: filter, reshape, unnest, cast, compute). Sinks: $0.03/GB JSON, $0.06/GB Parquet or Iceberg output. Free included allowance: Workers Free = 1 GB/month per dimension; Workers Paid = 50 GB/month per dimension. Standard R2 storage/operations and R2 Data Catalog charges apply separately. Requires a Workers Paid plan to use during beta. (verify - drifts)

**Limits:**
- Open beta: max 20 streams, 20 sinks, and 20 pipelines per account
- Max payload size per ingestion request: 5 MB
- Max ingest rate per stream: 5 MB/s
- Higher limits via Limit Increase Request Form
- Beta requires a Workers Paid plan to start

**Notes:** Honest caveats: (1) Lock-in tilts toward the Cloudflare data plane - sinks write only to R2 / R2 Data Catalog, not arbitrary S3/GCS/Snowflake; the open-table escape hatch is that Iceberg/Parquet in R2 is readable by external engines, which softens it. (2) SQL transforms are described as stateless (filter/reshape/cast/compute) - this is NOT a stream-processing engine for windowed aggregations, joins across streams, or stateful enrichment; for that you still want Flink/Spark/Materialize or a warehouse. (3) Still open beta with low default ceilings (20 of each resource, 5 MB/s per stream) - not yet proven for very high-throughput firehoses without a limit increase. (4) Product was significantly redesigned in Sept 2025 (streams/sinks/pipelines model; a Legacy pipelines migration guide exists) so older tutorials and the older single-'pipeline' CLI shape are stale. (5) Pricing numbers are published but billing is not live yet - treat rates as provisional. (6) Could not load /pipelines/platform/pricing/ directly (404 at the guessed path); pricing figures are grounded in the official May 2026 changelog announcement, not the canonical pricing page - verify the exact page before quoting to a customer.

**Docs:** https://developers.cloudflare.com/pipelines/llms.txt, https://developers.cloudflare.com/pipelines/, https://developers.cloudflare.com/pipelines/streams/writing-to-streams/, https://developers.cloudflare.com/pipelines/platform/limits/, https://developers.cloudflare.com/pipelines/pipelines/manage-pipelines/, https://developers.cloudflare.com/changelog/post/2026-05-11-pipelines-pricing-announced/

---

## Cloudflare R2
`r2` · Object Storage · confidence: `high` · lock-in: `sticky`

**Is:** S3-compatible object storage with zero egress fees for storing unstructured data (files, images, video, backups, ML datasets, logs).

**Replaces:** AWS S3 + its egress/data-transfer bills (the single biggest hook); also the wider 'S3 bucket + CloudFront CDN + NAT/egress' stack, or paid S3-compatible vendors (Wasabi, Backblaze B2, DigitalOcean Spaces, MinIO you self-host).

**Use it via:** Worker binding via wrangler.jsonc `r2_buckets: [{ binding: "MY_BUCKET", bucket_name: "..." }]`, then env.MY_BUCKET.get/put/delete/list/head + createMultipartUpload. OR S3 API at https://<ACCOUNT_ID>.r2.cloudflarestorage.com (SigV4; jurisdiction endpoints https://<ACCOUNT_ID>.<JURISDICTION>.r2.cloudflarestorage.com). OR Cloudflare REST API + `wrangler r2 bucket/object` CLI. R2 Data Catalog enabled via `wrangler r2 bucket catalog enable <bucket>`; query via `wrangler r2 sql query`.

**Capabilities:**
- S3-compatible API — reuse aws-sdk / boto3 / s3fs by repointing the endpoint to https://<ACCOUNT_ID>.r2.cloudflarestorage.com (SigV4, access key id + secret)
- Native Workers binding (env.MY_BUCKET.get/put/delete/list/head + multipart) — no keys in code, no SDK round-trip from the edge
- Zero egress fees on data read directly from R2 (Workers API, S3 API, and r2.dev public domain)
- Public buckets + custom domains for serving assets straight to the internet; presigned URLs for scoped temporary access
- Event notifications -> Queues, so writes/deletes can trigger Workers (thumbnailing, indexing, ETL)
- Standard + Infrequent Access storage classes ($0.01/GB-mo + $0.01/GB retrieval) and lifecycle rules
- Jurisdictional Restrictions (EU, FedRAMP) and Location Hints for data residency / placement
- Bucket locks (object-lock / WORM-style retention) for compliance and ransomware protection
- Migration tooling: Super Slurper (bulk one-time copy from S3/GCS/MinIO/Wasabi/B2/DO Spaces) and Sippy (incremental, copy-on-read migration)
- R2 Data Catalog: managed Apache Iceberg REST catalog built into the bucket; query with R2 SQL, Spark, Snowflake, DuckDB, Trino, PyIceberg

**Detection signals — the lens fires on these:**
- @aws-sdk/client-s3, aws-sdk, @aws-sdk/s3-request-presigner, boto3 / botocore, s3fs, minio, @aws-sdk/lib-storage in package.json / requirements.txt
- Env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET, S3_ENDPOINT, AWS_S3_BUCKET
- Code referencing s3.amazonaws.com, .s3.<region>.amazonaws.com, CloudFront distribution IDs, or an S3 origin behind a CDN
- Self-hosted object storage: minio/minio in docker-compose.yml or Dockerfile, MINIO_ROOT_USER/MINIO_ROOT_PASSWORD, a mounted volume used as a blob store
- Other S3-compatible vendors in config: wasabisys.com, backblazeb2.com / b2, digitaloceanspaces.com endpoints
- App-level file storage that should be object storage: user uploads written to local disk / a Postgres bytea / a mounted PVC; multer disk storage; storing large blobs in the database
- AWS bills / IaC where the line item is data transfer / egress (NAT Gateway, CloudFront egress) on a read-heavy bucket
- Analytics: Parquet/Iceberg files in S3 + an external Glue/Hive catalog, or a Spark/DuckDB/Trino job pointed at s3:// for log/event data

**Ideas:**
- Serve a read-heavy asset/media bucket (images, video, downloads, game assets) from R2 + a custom domain to kill CloudFront egress bills, and resize on the fly with Cloudflare Images.
- Back user uploads or generated artifacts with the R2 Workers binding so a Worker streams uploads straight to storage with no AWS keys, then fan out post-processing via R2 event notifications -> Queues.
- Land logs/events/clickstream as Iceberg tables in R2 Data Catalog and run serverless analytics with R2 SQL (or Spark/DuckDB/Snowflake) instead of standing up a warehouse — and migrate an existing S3 bucket in with Super Slurper / Sippy.

**Pairs with:** Workers (compute / presigning / streaming uploads at the edge), Cloudflare Images & Stream (resize/transform/serve media stored in R2), Queues (consume R2 event notifications for async processing), R2 Data Catalog + R2 SQL / Pipelines (Iceberg analytics over data in R2), Cache / CDN + custom domains (public asset delivery)

**Pricing:** Free tier: 10 GB-month storage, 1M Class A (writes/list) ops, 10M Class B (reads) ops per month; egress always free. Standard: $0.015/GB-month, $4.50/M Class A, $0.36/M Class B. Infrequent Access: $0.01/GB-month + $0.01/GB retrieval, $9.00/M Class A, $0.90/M Class B, 30-day min duration. Usage rounds up to the next billing unit. (verify — drifts)

**Limits:**
- Max object size ~4.995 TiB (documented as 5 TiB); single-part PUT max ~4.995 GiB (5 GiB) — larger needs multipart
- Multipart: up to 10,000 parts per upload
- Up to 1,000,000 buckets per account; unlimited objects and storage per bucket
- Object key length 1,024 bytes; custom metadata up to 8,192 bytes
- Concurrent writes to the SAME key: ~1/second; bucket-management ops ~50/second
- REST API ~1,200 requests per 5 minutes across all R2 operations; free r2.dev subdomain is rate-limited (429s past a few hundred req/s) and meant for dev, not production traffic

**Notes:** Egress is free directly from R2, but other Cloudflare services layered on top can still meter (e.g. Images transformations). Vendor lock-in is modest at the API layer (S3-compatible, so SDKs port back out), but jurisdiction is immutable once a bucket is created and the deeper features (Workers binding, Data Catalog, event notifications) are Cloudflare-specific. Not a database or a filesystem: no in-place partial writes/appends, no POSIX semantics, ~1 write/sec per key, eventual-ish for high-churn keys — wrong tool for hot mutable state (use D1/KV/Durable Objects). Several adjacent pieces (R2 Data Catalog, R2 SQL) are recent/beta-era; confirm GA status and current pricing before relying on them. Object-size and single-part numbers are documented as 5 TiB / 5 GiB but are precisely ~4.995 — verify against current limits page.

**Docs:** https://developers.cloudflare.com/r2/llms.txt, https://developers.cloudflare.com/r2/index.md, https://developers.cloudflare.com/r2/pricing/index.md, https://developers.cloudflare.com/r2/platform/limits/index.md, https://developers.cloudflare.com/r2/api/workers/workers-api-usage/index.md, https://developers.cloudflare.com/r2/api/s3/api/index.md, https://developers.cloudflare.com/r2/reference/data-location/index.md

---

## R2 SQL
`r2-sql` · Data & Analytics · confidence: `high` · lock-in: `sticky`

**Is:** A serverless, distributed SQL query engine that runs read-only analytics queries directly over Apache Iceberg tables stored in R2 Data Catalog, billed by bytes scanned.

**Replaces:** A self-managed analytics stack: an S3 data lake + AWS Athena/Presto/Trino (or DuckDB/Spark on a box) + Glue catalog, plus the egress and cluster ops to run it. The 'stop building this yourself' hook is the hand-rolled 'dump JSON/Parquet to object storage, then stand up a query engine + catalog to read it' pipeline.

**Use it via:** Wrangler CLI: `npx wrangler r2 sql query <WAREHOUSE> "SELECT ... FROM namespace.table LIMIT 10"` (auth via env var WRANGLER_R2_SQL_AUTH_TOKEN). REST: `POST https://api.sql.cloudflarestorage.com/api/v1/accounts/{ACCOUNT_ID}/r2-sql/query/{BUCKET_NAME}` with header `Authorization: Bearer <token>`, `Content-Type: application/json`, body `{"query":"..."}`. API token needs permission groups: 'Workers R2 SQL Read', 'Workers R2 Data Catalog Write', 'Workers R2 Storage Write'. Prereqs: R2 bucket with Data Catalog enabled (`wrangler r2 bucket catalog enable <bucket>`). NOTE: no Worker binding and no client SDK documented as of this run — CLI + REST only.

**Capabilities:**
- Distributed, serverless SQL over Apache Iceberg tables in R2 — no cluster to provision or tune
- Automatic file pruning and query optimization (partition + predicate pushdown); reads compressed bytes, prices on data scanned
- Read-only analytical SQL: SELECT / FROM / WHERE / GROUP BY / HAVING / ORDER BY / LIMIT, CTEs (WITH), and UNION/UNION ALL/INTERSECT/EXCEPT
- All standard JOIN types across multiple Iceberg tables: INNER, LEFT, RIGHT, FULL OUTER, CROSS, and implicit joins (per sql-reference; overview/get-started don't showcase them)
- 173 scalar functions and 33 aggregate functions; expressions CASE/CAST/LIKE/BETWEEN/IN, subqueries, struct/array/map complex types
- Queries data landed by Cloudflare Pipelines (HTTP/stream ingest -> Iceberg sink in R2 Data Catalog), giving a near-real-time ingest-to-query lakehouse loop
- Works on both partitioned and unpartitioned Iceberg tables

**Detection signals — the lens fires on these:**
- An R2 (or S3) bucket holding Apache Iceberg or Parquet files used as an analytics/event lake
- wrangler.jsonc / wrangler.toml with `r2_buckets` bindings plus a separate analytics query path
- AWS Athena, Presto, Trino, or DuckDB/Spark used to query Parquet/Iceberg in object storage (look for @aws-sdk/client-athena, athena, trino-client, prestodb, duckdb, pyiceberg, deltalake, glue catalog config)
- AWS_ACCESS_KEY_ID / AWS_S3_BUCKET env vars feeding an Athena or Glue workflow over a data lake
- Cloudflare Pipelines already in use (`wrangler pipelines setup`, INSERT INTO ... SELECT FROM stream) writing to an Iceberg sink — the natural query layer on top
- A Worker/cron that batches events to Parquet and a separate service/notebook that runs ad-hoc SQL over them
- pyiceberg / apache-iceberg / iceberg-rust dependencies pointed at an R2 or S3 catalog
- 'dump to object storage then query later' analytics that today round-trip through BigQuery/Snowflake external tables or a self-hosted OLAP box

**Ideas:**
- Run ad-hoc analytics (fraud flags, funnel/event aggregations, revenue rollups) directly over event data your Pipelines already land in R2 Iceberg tables — skip exporting to a warehouse.
- Replace an Athena/Trino-over-S3 setup: keep data in R2 (no per-query egress to a separate engine), point R2 SQL at the same Iceberg tables, and pay only for bytes scanned.
- Back a lightweight internal dashboard or scheduled report by hitting the R2 SQL REST endpoint from a Worker cron, instead of operating a query cluster.

**Pairs with:** R2 (object storage holding the data), R2 Data Catalog (the managed Apache Iceberg catalog R2 SQL queries), Cloudflare Pipelines (streaming/HTTP ingest that writes Iceberg tables for R2 SQL to read), Workers (cron or API Worker that calls the R2 SQL REST endpoint)

**Pricing:** Free tier: 1 GB scanned / month. Beyond that, $0.0025 / GB scanned ($2.50 / TB), measured as compressed bytes read from R2. Minimum 10 MB billed per query (sub-10 MB queries still cost 10 MB). Currently open beta and free for R2 subscribers, with billing to begin after 30 days' notice. Storage and any R2 operations billed separately under R2 / R2 Data Catalog. (verify — drifts)

**Limits:**
- Read-only: no INSERT/UPDATE/DELETE/CREATE/DROP/ALTER — it queries data, it does not mutate tables (writes come via Pipelines or Iceberg writers)
- Parquet data files only; CSV/JSON not supported as the underlying table format
- Only Apache Iceberg tables managed by R2 Data Catalog (bucket must have Data Catalog enabled) — not a general-purpose SQL DB and not OLTP
- No window functions and no OFFSET clause; UNNEST, PIVOT/UNPIVOT, and nested joins unsupported
- DISTINCT inside aggregates (e.g. COUNT(DISTINCT)) unsupported — use approx_distinct; ARRAY_AGG/STRING_AGG unsupported for memory safety; PERCENTILE_CONT/DISC and MEDIAN need approximate alternatives
- Multi-table joins are supported but performance depends on intermediate result size; avoid joining 3+ large tables without filters
- now()/current_time() quantized to 10ms boundaries and forced to UTC
- No documented Worker binding or client SDK yet — integration is CLI + REST only, which complicates calling it inline from Worker code (must POST to the REST endpoint)

**Notes:** Honest caveats: (1) Scope — this is an OLAP/lakehouse query engine, not a transactional database; for app state/CRUD use D1, KV, or Durable Objects, not R2 SQL. (2) Maturity — open beta; pricing is announced but not yet charged, and the integration surface is thin (CLI + REST, no binding/SDK observed this run), so it's better for batch/scheduled analytics than tight in-request paths today. (3) Lock-in is moderate, not severe: data sits in open Apache Iceberg + Parquet in R2, so the *tables* are portable to other Iceberg engines (Spark/Trino/DuckDB); what's Cloudflare-specific is the query API and R2 Data Catalog, and you avoid S3 egress only as long as you stay in R2. (4) Feature gaps matter: no window functions/OFFSET and approximate-only DISTINCT/percentiles mean some warehouse workloads won't port cleanly. (5) Version note: the overview and get-started pages still describe a narrower SELECT-only feature set, while the sql-reference page documents full JOINs/CTEs/set ops — treat JOIN/CTE support as current but re-verify, as docs are mid-update.

**Docs:** https://developers.cloudflare.com/r2-sql/llms.txt, https://developers.cloudflare.com/r2-sql/index.md, https://developers.cloudflare.com/r2-sql/query-data/index.md, https://developers.cloudflare.com/r2-sql/platform/pricing/index.md, https://developers.cloudflare.com/r2-sql/reference/limitations-best-practices/index.md, https://developers.cloudflare.com/r2-sql/get-started/index.md, https://developers.cloudflare.com/r2-sql/sql-reference/index.md

---

## Workers KV
`workers-kv` · Storage / Edge cache · confidence: `high` · lock-in: `sticky`

**Is:** A global, low-latency, eventually-consistent key-value store that reads from Cloudflare's edge cache and is bound directly into a Worker.

**Replaces:** A Redis/Memcached box (or Upstash/ElastiCache) fronting config, feature flags, sessions, or allow/deny-lists — plus the CDN-edge caching layer you'd hand-roll on top of it.

**Use it via:** Worker binding: env.NAMESPACE.get(key, 'text'|'json'|'arrayBuffer'|'stream'), .getWithMetadata(key), .put(key, value, {expiration|expirationTtl, metadata}), .delete(key), .list({prefix, cursor, limit}); get returns null on miss. Config: kv_namespaces:[{binding,id}] in wrangler.jsonc (or [[kv_namespaces]] in wrangler.toml). REST/bulk: /accounts/{id}/storage/kv/namespaces/{ns}/values/{key} and /bulk. CLI: wrangler kv.

**Capabilities:**
- Key-value get/put/delete/list bound into a Worker with sub-millisecond hot reads from the local edge cache
- Reads served from a tiered cache (local edge -> regional -> central), so popular keys are fast everywhere with zero replication code
- Per-key TTL expiration: absolute (expiration, UNIX epoch) or relative (expirationTtl, min 60s); expiration takes precedence over cacheTtl
- Up to 1024 bytes of arbitrary metadata per key, returned via getWithMetadata without a second fetch
- Values up to 25 MiB as string, JSON, ArrayBuffer, or ReadableStream; keys up to 512 bytes
- Bulk write up to 10,000 pairs per request via Wrangler/REST (binding is single-key only)
- No egress/data-transfer charges — reads are billed per-operation, not per-byte-out

**Detection signals — the lens fires on these:**
- Dependencies: ioredis, redis, @upstash/redis, memcached, node-cache, lru-cache used as a shared/distributed cache
- Env vars: REDIS_URL, REDIS_HOST, UPSTASH_REDIS_REST_URL, MEMCACHED_SERVERS
- A Redis/Memcached service in docker-compose.yml or a managed cache (ElastiCache/Upstash/Memorystore) in IaC, used only for config/flags/sessions/allow-lists rather than queues or pub-sub
- Hand-rolled edge/CDN cache layers: storing JSON config or feature flags in a DB and caching reads in-memory per-instance with manual TTL invalidation
- Loading feature flags, A/B config, or remote config from a DB/S3 on every request
- Session/token stores, rate-limit allow/deny-lists, or IP blocklists kept in Redis
- An already-Cloudflare-Workers project reading config from an external store instead of a binding

**Ideas:**
- Move feature flags / remote config / A/B assignments out of a DB or Redis into KV and read them at the edge with cacheTtl for near-zero-latency lookups
- Serve allow/deny-lists, API-key validation, or IP blocklists from KV so the check happens in the Worker before origin
- Cache rendered fragments, API responses, or geo/personalization config keyed per-route, replacing a per-instance in-memory cache that doesn't share across edge locations

**Pairs with:** Workers, Durable Objects, D1, R2, Pages Functions

**Pricing:** Free: 100k reads, 1k writes, 1k deletes, 1k lists per day + 1 GB storage. Paid: 10M reads/mo then $0.50/M; 1M writes, deletes, lists/mo then $5.00/M each; 1 GB storage then $0.50/GB-mo. All ops billed including misses; no egress charge. (verify — drifts)

**Limits:**
- Value max 25 MiB; key max 512 bytes; metadata max 1024 bytes (serialized)
- Max 1 write per second to the SAME key (429 on violation) — not a write-heavy store
- Eventual consistency: writes can take 60s+ to be globally visible; negative lookups are cached too
- Min expirationTtl 60s; min cacheTtl 30s (default 60s)
- 1000 KV operations per Worker invocation; 1,000 namespaces per account; bulk write capped at 10,000 pairs / 100 MB per request
- arrayBuffer and stream types unavailable for multi-key get

**Notes:** Wrong tool when you need strong consistency, atomic increments/transactions, or frequent writes to one key (e.g. counters, locks, live game state) — Cloudflare points those at Durable Objects. Also not for relational queries or large-blob storage (use D1 and R2 respectively). The 60s+ write-propagation window means it's read-optimized: great for data written rarely and read often, poor for write-hot paths. Lock-in is modest — the get/put/delete/list shape ports, but the edge-cache latency profile and Worker binding are Cloudflare-specific.

**Docs:** https://developers.cloudflare.com/kv/llms.txt, https://developers.cloudflare.com/kv/concepts/how-kv-works/index.md, https://developers.cloudflare.com/kv/platform/pricing/index.md, https://developers.cloudflare.com/kv/platform/limits/index.md, https://developers.cloudflare.com/kv/concepts/kv-bindings/index.md, https://developers.cloudflare.com/kv/api/read-key-value-pairs/index.md, https://developers.cloudflare.com/kv/api/write-key-value-pairs/index.md

---
