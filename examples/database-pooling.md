# Postgres from serverless (connection exhaustion)

**Task:** "Our Workers/Lambdas open a Postgres connection per invocation. Under load we
exhaust the connection pool, so we bolted on RDS Proxy / PgBouncer — and reads from far
regions are slow."

## The old way (a pooler in front of Postgres)

```ts
import { Pool } from 'pg'
const pool = new Pool({ connectionString: process.env.DATABASE_URL })  // per-isolate pools
// thousands of edge isolates × a few connections each = blow past max_connections,
// so you run RDS Proxy / PgBouncer (another box/$$), and you still pay round-trip
// latency from every edge to a single-region database.
```

## With Hyperdrive (pooling + caching at the edge)

```bash
npx wrangler hyperdrive create my-db \
  --connection-string="postgres://user:pass@host:5432/db"
```
```jsonc
// wrangler.jsonc
{ "hyperdrive": [{ "binding": "HYPERDRIVE", "id": "<id-from-create>" }] }
```
```ts
import { Pool } from 'pg'
// point your normal driver at the binding — Hyperdrive pools globally + caches reads
const pool = new Pool({ connectionString: env.HYPERDRIVE.connectionString })
const { rows } = await pool.query('select * from products where id = $1', [id])
```

**Why it's the swap:** Hyperdrive maintains the connection pool for you (no more
exhaustion, no RDS Proxy box) and **caches read queries at the edge**, cutting latency to
your single-region Postgres — using the same `pg`/`postgres` driver you already have.

### The honest catch
- **Lock-in: sticky** — but light: it's a connection string swap, your DB stays yours.
- **Data gravity check:** your Postgres still lives in one region. Hyperdrive softens the
  hop; it doesn't move the data. Read-heavy workloads win most; write-heavy/strongly-consistent
  paths still pay the round trip. (If the system of record could move, weigh **D1**.)
- **Verify** cached-query semantics + supported drivers against
  `https://developers.cloudflare.com/hyperdrive/llms.txt`.
