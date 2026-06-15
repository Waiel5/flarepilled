# Compute & Workers

_8 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Cloudflare Containers
`containers` · Compute · confidence: `high` · lock-in: `portable`

**Is:** Serverless Docker containers that spin up on-demand, controlled from Worker code and backed by Durable Objects, for workloads too heavy or too Linux-y for a plain Worker.

**Replaces:** A box you keep warm to run code Workers can't: an ECS/Fargate task, a Fly.io app, a Kubernetes deployment, or a $5-40/mo VPS running `docker run` behind a load balancer — plus the autoscaling and image registry around it.

**Use it via:** wrangler.jsonc `containers` array: { class_name, image: "./Dockerfile" | registry ref, instance_type, max_instances } + a matching `durable_objects.bindings` entry + `migrations` with `new_sqlite_classes`. In code: `import { Container, getContainer } from "@cloudflare/containers"`; `class MyContainer extends Container { defaultPort=8080; sleepAfter="5m" }`; route with `getContainer(env.MY_CONTAINER, sessionId).fetch(request)`. Deploy: `npx wrangler deploy` (builds via local Docker, pushes changed layers). CI: `wrangler containers build/push`.

**Capabilities:**
- Run an arbitrary Docker image (any language/runtime, full Linux filesystem, native binaries like ffmpeg/headless-chromium/Python ML) next to your Worker
- Scale-to-zero: instances sleep after an idle timeout (sleepAfter, default 10m) and spin back up on the next request; cold start typically 1-3s
- Per-instance routing & session affinity via getContainer(env.BINDING, name) — each named instance is its own container, ideal for per-user sandboxes / stateful sessions
- Lifecycle hooks (onStart, onStop, onError, onActivityExpired) and explicit start/stop/destroy control because each container is a Durable Object
- Managed image registry backed by R2 (registry.cloudflare.com) with layer-diff pushes; also pulls from Docker Hub and Amazon ECR
- Access Worker bindings (KV, R2, D1, Durable Objects, Queues) from the controlling Worker; per-instance SQLite via this.ctx.storage
- Predefined instance types (lite -> standard-4, up to 4 vCPU / 12 GiB RAM / 20 GB disk) or custom sizes

**Detection signals — the lens fires on these:**
- A `Dockerfile` or `docker-compose.yml` in the repo for an app deployed elsewhere (especially a single web service / job runner)
- Fly.io config: `fly.toml`, flyctl, `fly deploy`
- AWS ECS/Fargate: `ecs-task-definition.json`, `aws ecs`, Fargate, Copilot (`copilot/`), App Runner
- Kubernetes for a small service: `deployment.yaml`, `k8s/`, Helm charts, kustomize wrapping one or two Deployments
- Render / Railway / Heroku / DigitalOcean App Platform manifests (`render.yaml`, `railway.json`, `Procfile`, `app.yaml`) for a container service
- A long-running Node/Python/Go process behind nginx on a VPS (systemd unit, pm2, `docker run` in a deploy script)
- Native-binary workloads that can't run in a Worker: `sharp`/`ffmpeg`/`imagemagick`/`puppeteer`/`playwright`/headless Chromium, `pdf` rendering, Pandoc, ML inference with PyTorch/Tensorflow, a code-execution sandbox
- Existing Cloudflare Worker that proxies out to a separate container host (smell: Worker + external compute it could absorb)
- Per-user/per-session isolated compute hand-rolled with a pool of VMs or a queue of jobs

**Ideas:**
- Move an ffmpeg/sharp/headless-Chromium job off a Fargate task or VPS into a Container invoked from a Worker, so it scales to zero between jobs instead of running 24/7
- Run an AI agent's code-execution sandbox or a per-user dev environment as a named Container (getContainer(env.X, userId)) for isolation without managing a VM pool
- Wrap an existing Dockerized API or legacy service in a Container so a Worker can front it with KV caching, WAF, and bindings — without standing up Kubernetes

**Pairs with:** Workers (the controller / HTTP front door), Durable Objects (each container instance is one; per-instance SQLite via this.ctx.storage), R2 (backs the image registry; also the go-to for persisting state off ephemeral disk), Queues (fan jobs into containers), Workers AI / Vectorize (offload heavy inference to a container when a Worker can't host the model)

**Pricing:** Requires Workers Paid ($5/mo); no separate free tier for container usage. Billed on provisioned memory + disk and active vCPU, plus egress. Included monthly allotments: 25 GiB-hours memory, 375 vCPU-minutes, 200 GB-hours disk. Overages: $0.0000025/GiB-s memory, $0.000020/vCPU-s, $0.00000007/GB-s disk. Egress $0.025/GB NA+EU (1 TB incl.), $0.04-0.05/GB elsewhere. (verify — drifts)

**Limits:**
- Instance types: lite (1/16 vCPU, 256 MiB, 2 GB) -> standard-4 (4 vCPU, 12 GiB, 20 GB); custom max 4 vCPU / 12 GiB RAM / 20 GB disk
- Custom ratios: min 3 GiB memory per vCPU; max 2 GB disk per 1 GiB memory
- Account caps: 6 TiB concurrent memory, 1,500 concurrent vCPU, 30 TB concurrent disk, 50 GB total image storage
- Image size capped at the instance's disk space
- Disk is ephemeral — wiped on restart unless externalized (e.g. R2/FUSE); persistence is not automatic
- Cold start ~1-3s depending on image size; a container may be placed in a different region than its Durable Object (optimized for startup, not co-location)
- Local build/deploy needs a running Docker (or Docker-compatible) CLI

**Notes:** Newer product, evolving fast — instance types, included allotments, and per-unit prices drift; re-verify against the live pricing/limits pages. NOT a fit for: always-on ultra-low-latency services where 1-3s cold starts hurt (keep warm via sleepAfter, which costs idle provisioned memory/disk); >4 vCPU / >12 GiB jobs (exceeds max instance); or anything needing durable local disk (it's ephemeral). Lock-in is moderate: the Dockerfile/image is portable, but the @cloudflare/containers Container class, getContainer routing, and Durable-Object binding model are Cloudflare-specific glue you'd rewrite to move to ECS/Fly/K8s. Egress is metered (with generous NA/EU allowance) but cheaper and more predictable than AWS egress. Docker Hub/ECR pulls are not cached and Docker Hub may rate-limit — prefer the Cloudflare registry.

**Docs:** https://developers.cloudflare.com/containers/index.md, https://developers.cloudflare.com/containers/pricing/index.md, https://developers.cloudflare.com/containers/platform-details/limits/index.md, https://developers.cloudflare.com/containers/container-class/index.md, https://developers.cloudflare.com/containers/get-started/index.md, https://developers.cloudflare.com/containers/platform-details/image-management/index.md, https://developers.cloudflare.com/containers/platform-details/architecture/index.md

---

## Cloudflare Durable Objects
`durable-objects` · Stateful compute / coordination · confidence: `high` · lock-in: `deep`

**Is:** Single-threaded, globally-addressable stateful actors that pair Worker compute with built-in transactional SQLite storage, so one named instance can coordinate many clients (chat rooms, multiplayer, booking, presence) without an external DB or pub/sub box.

**Replaces:** A Redis box (or upstash) for sessions/locks/coordination + Pusher/Ably/Socket.io for realtime fan-out — collapsed into one per-entity object you address by name.

**Use it via:** Worker binding. wrangler.jsonc: durable_objects.bindings: [{ name: "MY_DO", class_name: "MyDurableObject" }] plus a migrations entry with new_sqlite_classes: ["MyDurableObject"]. Class extends DurableObject from 'cloudflare:workers'; constructor(ctx: DurableObjectState, env). Invoke from a Worker: env.MY_DO.getByName(name) (or idFromName(name) then .get(id)) returns a stub, then call RPC methods on it. Storage via this.ctx.storage.sql.exec(...) / .get/.put. REST admin API at /api/resources/durable_objects/subresources/namespaces (list namespaces).

**Capabilities:**
- Per-instance single-threaded actor: each object is globally unique and addressed by name (getByName / idFromName), so all requests for one entity (room, document, user, game) hit the same instance — natural serialization, no race conditions, no distributed lock service
- Built-in strongly-consistent transactional storage: SQLite per object (this.ctx.storage.sql.exec(...)) plus a key-value API; data is private to that one instance and co-located with the compute
- In-memory state caching between requests (resets on hibernation), avoiding storage round-trips for hot state
- WebSocket Hibernation API: one object coordinates many WebSocket connections (acceptWebSocket / getWebSockets / broadcast); the object is evicted from memory while connections stay open, and Duration (GB-s) is NOT billed during hibernation. serializeAttachment/deserializeAttachment persist per-connection state (max 16,384 bytes)
- Alarms API: schedule future wake-ups (this.ctx.storage.setAlarm) for periodic/time-based work — replaces an external cron/job-scheduler for per-entity timers; alarm handlers get up to 15 min wall clock
- Native RPC: call DO methods directly as JS (await stub.sayHello()) instead of hand-rolling fetch + serialization between Worker and object

**Detection signals — the lens fires on these:**
- Realtime infra: socket.io / ws server + a separate sticky-session/Redis adapter (socket.io-redis, @socket.io/redis-adapter); pusher / pusher-js; ably; partykit / partyserver; liveblocks; a long-running WebSocket server process that must pin clients to one node
- Coordination via Redis: ioredis / redis / @upstash/redis used for locks, counters, rate-limit buckets, presence sets, or 'who is in this room' — REDIS_URL, UPSTASH_REDIS_REST_URL env vars; SETNX/Redlock distributed-lock patterns
- Per-entity state forced into a shared DB purely for serialization/concurrency control (SELECT ... FOR UPDATE, advisory locks, optimistic-version columns) when the real need is 'one writer per room/doc/user'
- An external job scheduler / cron worker (BullMQ, Agenda, a cron service, Cloudflare Queues + cron) used only to fire a per-entity timer (e.g. 'expire this booking in 10 min', 'end this auction')
- A stateful singleton server (game-server, collab/CRDT server, presence service) the team runs on a VM/container and has to shard and keep warm
- Already on Cloudflare Workers (wrangler.jsonc/.toml, @cloudflare/workers-types, export default { fetch }) but reaching off-platform for any of the above — strongest signal, since DO is the in-platform answer

**Ideas:**
- Replace a Pusher/Ably/socket.io+Redis realtime layer with one Durable Object per room/channel using the WebSocket Hibernation API — connections stay open while idle and you stop paying GB-s during hibernation
- Model each booking/auction/seat-map/rate-limit-bucket as its own named Durable Object so concurrent writes serialize on the single-threaded instance instead of needing Redlock or SELECT FOR UPDATE
- Use the Alarms API for per-entity timers (expire a hold, end an auction, send a reminder, debounce a webhook) instead of standing up BullMQ/Agenda/an external cron
- Give each AI agent / chat session a Durable Object to hold conversation state + SQLite history co-located with compute (this is the foundation of the Cloudflare Agents SDK)

**Pairs with:** Cloudflare Workers (DOs are defined and bound from a Worker), Cloudflare Agents SDK (built on Durable Objects for per-agent state), Workers KV / R2 / D1 for shared/global data that should NOT be siloed per-instance, Hibernatable WebSockets for realtime; Queues for async fan-out between objects

**Pricing:** Available on BOTH free and paid Workers plans (free plan supports SQLite-backed storage only; KV-backed storage is paid-only). Compute billed on requests + Duration (GB-s): Free = 100k requests/day + 13,000 GB-s/day; Paid = 1M requests/month then $0.15/M, and 400,000 GB-s/month then $12.50/M GB-s. Billable metrics include HTTP requests, RPC sessions, WebSocket messages (incoming messages billed at a 20:1 ratio) and alarm invocations; no Duration billed during WebSocket hibernation. SQLite storage billing starts ~Jan 7 2026: Free = 5M rows read/day, 100k rows written/day, 5 GB total; Paid = first 25B rows read/mo then $0.001/M, first 50M rows written/mo then $1.00/M, 5 GB-month then $0.20/GB-month. (verify — drifts)

**Limits:**
- Storage per object (SQLite-backed): 10 GB; per-account storage Free = 5 GB, Paid = unlimited
- Classes per account: 500 (Workers Paid) / 100 (Free); objects per namespace: unlimited
- Throughput: soft limit ~1,000 requests/second per single object (the single-threaded model is the bottleneck for very hot keys — shard if you exceed it)
- CPU time: 30s default, configurable up to 5 minutes of active CPU; wall-clock unlimited while an HTTP/RPC/WebSocket connection is open; alarm handlers up to 15 min
- SQLite row size 2 MB, SQL statement length 100 KB, 100 columns/table, 100 bound params/query; KV value 128 KiB, KV key 2 KiB; WebSocket received message up to 32 MiB

**Notes:** Lock-in: this is a Cloudflare-runtime-native primitive (cloudflare:workers, DurableObjectState, wrangler migrations) with no drop-in equivalent elsewhere — porting off means re-architecting the actor model. NOT a general-purpose database: each object's storage is private to that single instance, so it's wrong for cross-entity queries, analytics, or shared global state (use D1/KV/R2 for that). NOT for ultra-hot single keys beyond ~1k req/s — the single-threaded guarantee that makes coordination easy also caps per-object throughput, so design your keyspace to shard load. Watch the new SQLite storage billing turning on in Jan 2026 and the 20:1 incoming-WebSocket-message billing ratio. Pricing/limits quoted from docs fetched 2026-06-15 and explicitly drift (1 GB→10 GB SQLite expansion was in flight).

**Docs:** https://developers.cloudflare.com/durable-objects/llms.txt, https://developers.cloudflare.com/durable-objects/concepts/what-are-durable-objects/index.md, https://developers.cloudflare.com/durable-objects/platform/pricing/index.md, https://developers.cloudflare.com/durable-objects/platform/limits/index.md, https://developers.cloudflare.com/durable-objects/get-started/index.md, https://developers.cloudflare.com/durable-objects/best-practices/websockets/index.md

---

## Cloudflare Sandbox SDK
`sandbox-sdk` · Compute / Code Execution · confidence: `high` · lock-in: `portable`

**Is:** An SDK to spin up secure, isolated Linux containers from a Worker and run untrusted code, shell commands, or whole dev servers inside them, each addressable by a stable sandbox ID.

**Replaces:** A self-hosted code-execution sandbox built on Firecracker/gVisor microVMs or Docker-on-a-VM (plus the EC2/Fargate fleet, autoscaler, and per-tenant teardown to run it), or a hosted code-interpreter vendor like E2B / Daytona / Modal sandboxes.

**Use it via:** npm package @cloudflare/sandbox; scaffold with `npm create cloudflare@latest -- my-sandbox --template=cloudflare/sandbox-sdk/examples/minimal`. In the Worker: `import { getSandbox, proxyToSandbox, type Sandbox } from '@cloudflare/sandbox'` then `const sandbox = getSandbox(env.Sandbox, 'user-123')`. wrangler.jsonc needs a `containers` entry (class_name:'Sandbox', image:'./Dockerfile', instance_type:'lite'), a `durable_objects.bindings` entry binding class Sandbox to name Sandbox, and a `migrations` entry with Sandbox in new_sqlite_classes. Binding typed as `Sandbox: DurableObjectNamespace<Sandbox>`. Also exposes a Sandbox Bridge HTTP API for non-Workers callers.

**Capabilities:**
- Run arbitrary shell commands in an isolated Ubuntu container via sandbox.exec() returning {stdout, stderr, exitCode, success}
- Code Interpreter: execute Python, JavaScript, and TypeScript with persistent contexts that keep variables/imports/functions across runs (createCodeContext / runCode / listCodeContexts / deleteCodeContext)
- Rich outputs from interpreted code: text, html, png, jpeg, svg, latex, markdown, json, chart, data (Jupyter-style data-viz without saying Jupyter)
- Streaming output via onStdout / onStderr / onResult / onError callbacks; top-level await in JS/TS contexts
- Filesystem API (read/write/manage files, file watching), git workflows, background processes, docker-in-docker
- Preview URLs: exposePort(port) returns a public HTTPS URL (https://{port}-{sandbox-id}-{token}.yourdomain.com) routing straight to a service running inside the sandbox; getExposedPorts() lists them
- Mount S3-compatible object storage (R2) into the sandbox filesystem; proxy/outbound traffic controls; terminal over WebSocket
- Persistent identity: same sandbox ID always routes to the same Durable-Object-backed instance

**Detection signals — the lens fires on these:**
- npm deps: e2b / @e2b/code-interpreter / @e2b/sdk, @daytonaio/sdk, modal, or in-house 'sandbox'/'code-runner' packages
- Docker-as-a-service shapes: spawning `docker run`/`docker exec` per user request, dockerode, a Dockerfile whose image is handed untrusted code, docker-in-docker (dind) sidecars
- microVM/jailing libs: firecracker, firecracker-containerd, gvisor/runsc, nsjail, bubblewrap (bwrap), seccomp profiles, isolated-vm, vm2, Pyodide/pyodide used to sandbox user Python
- AI-agent code execution: an agent/tool-calling loop that needs to run model-generated Python/JS (LangChain PythonREPL, OpenAI/Anthropic 'code interpreter' shims, exec() of LLM output)
- Per-tenant compute fleets on AWS/GCP: ECS/Fargate task-per-job, EC2 autoscaling groups that boot a VM to run one user's code then tear it down, Kubernetes Jobs spun up per execution
- Ephemeral preview/dev-server hosting: code that allocates a port + reverse-proxies (nginx/Caddy/ngrok/localtunnel) to expose a user's running app at a unique subdomain
- Notebook/data-analysis backends: Jupyter kernel pools, nbconvert, papermill, a 'kernel gateway' running user notebooks
- CI-in-the-app: a feature that clones a repo and runs tests/builds on demand (git clone + npm test orchestration outside real CI)

**Ideas:**
- Back an AI coding agent's tool-use loop: let the model write Python/JS, runCode() it in a per-user persistent context, stream stdout/charts back, and keep state between turns instead of re-bootstrapping an interpreter each call.
- Offer 'run your snippet' / live data-notebook features (CSV upload -> pandas -> rendered chart) by leaning on the Code Interpreter's png/svg/chart rich outputs rather than standing up a Jupyter kernel farm.
- Build instant per-PR or per-user preview environments: clone the repo into a sandbox, start the dev server, and hand back the exposePort() HTTPS URL — replacing a homegrown ngrok/Caddy + container-orchestration preview stack.

**Pairs with:** Cloudflare Containers (the underlying execution + billing layer), Durable Objects (per-sandbox identity, routing, state), Workers AI / Agents SDK (LLM that generates the code to execute), R2 (mount as object storage for inputs/outputs and data persistence), Workers (the entry point that calls getSandbox)

**Pricing:** No standalone free tier published; pricing is inherited from the underlying Containers platform (you pay Containers' vCPU + memory + disk rates) plus Workers, Durable Objects, and Workers Logs usage. Containers requires a Workers Paid plan. Exact per-unit rates live on the Containers pricing page, not the Sandbox page. (verify — drifts)

**Limits:**
- Each sandbox runs in its own VM (isolated Ubuntu Linux with Python, Node.js, Git preinstalled); one container per sandbox ID, lifecycle owned by a Durable Object
- instance_type in wrangler (e.g. 'lite') selects the container size; actual vCPU/memory/disk caps and available instance types come from Containers platform limits, not the Sandbox docs
- Workers subrequest cap applies to HTTP transport: 50 subrequests/request on Workers Free, 1,000 on Workers Paid — use the WebSocket transport to multiplex and dodge this
- Languages for the Code Interpreter are Python, JavaScript, TypeScript only
- Preview URLs are public-by-default and gated only by a random 16-char token — not real auth; sensitive endpoints need their own auth layer
- A '2026 deprecation migration' guide exists, so some current APIs/config are slated to change — pin versions and check that page

**Notes:** Strongest fit when you need to run untrusted or model-generated code with hard isolation, or to host short-lived per-user/per-PR environments, from inside a Cloudflare Worker. Lock-in is real: it's built on Cloudflare Containers + Durable Objects, so the binding model, wrangler config, and pricing are Cloudflare-specific — not a drop-in for an existing AWS/k8s execution fleet. NOT the right tool for long-running always-on services (that's plain Containers/Workers), for trusted first-party batch jobs where isolation is overkill, or for heavy GPU workloads. Could not verify on this run: exact vCPU/memory/disk numbers per instance_type, concrete $ rates, idle-sleep/cold-start timing, and max concurrent sandboxes — all deferred to the Containers limits/pricing pages, which I did not fetch. The docs say 'each sandbox runs in its own VM' but do not name the isolation tech (microVM vs gVisor), so treat the precise isolation boundary as unconfirmed. The '2026 deprecation' guide signals API churn.

**Docs:** https://developers.cloudflare.com/sandbox/llms.txt, https://developers.cloudflare.com/sandbox/index.md, https://developers.cloudflare.com/sandbox/get-started/index.md, https://developers.cloudflare.com/sandbox/platform/pricing/index.md, https://developers.cloudflare.com/sandbox/platform/limits/index.md, https://developers.cloudflare.com/sandbox/api/interpreter/index.md, https://developers.cloudflare.com/sandbox/concepts/architecture/index.md, https://developers.cloudflare.com/sandbox/concepts/preview-urls/index.md

---

## Cloudflare Workers
`cloudflare-workers` · Compute / Serverless · confidence: `high` · lock-in: `portable`

**Is:** A serverless platform that runs your JS/TS/Python/Rust/WASM code on V8 isolates across Cloudflare's global edge network, deployed with a single command and no infrastructure to manage.

**Replaces:** AWS Lambda + API Gateway (or an always-on Express/Fastify box on EC2/a VPS behind a load balancer) — plus the container/cold-start and egress bills that come with them.

**Use it via:** Worker binding via the env object (e.g. env.MY_BUCKET.put(...), env.DB.prepare(...)); env importable as `import { env } from "cloudflare:workers"`. Configured in wrangler.jsonc/wrangler.toml (binding arrays like r2_buckets, kv_namespaces, d1_databases, durable_objects, queues, vectorize, ai, services). Deployed/dev'd with the Wrangler CLI (`wrangler deploy`, `wrangler dev`); templates also deployable from the dashboard.

**Capabilities:**
- Runs code on V8 isolates instead of containers: an isolate starts ~100x faster than a Node process on a VM and uses an order of magnitude less startup memory, effectively eliminating cold starts
- Standard fetch(request, env, ctx) handler model; also supports Cron Triggers, Queue consumers, and Durable Object alarms as entry points
- Runs on Cloudflare's global network (thousands of machines across hundreds of locations) — code executes in whichever data center receives the request, no region to pick
- Languages: JavaScript, TypeScript, Python, Rust, and WebAssembly
- 24+ binding types wire the Worker to the rest of the platform (KV, R2, D1, Durable Objects, Queues, Workers AI, Vectorize, Hyperdrive, Service bindings, Workflows, Browser Rendering, Images) with the credential embedded in the binding — the secret is never exposed to code
- No charge or limit for wall-clock duration and zero egress/bandwidth fees; ctx.waitUntil() extends work up to 30s after the response
- Static asset serving is free and unlimited; subrequests don't count against request totals

**Detection signals — the lens fires on these:**
- AWS Lambda artifacts: serverless.yml, AWS SAM template.yaml, `aws-lambda` / `@aws-sdk` deps, handler.js exporting `exports.handler`, API Gateway config
- Always-on Node servers meant to scale horizontally: express / fastify / koa + a Dockerfile + a PaaS config (Procfile, render.yaml, fly.toml, Heroku, ECS task defs) where the app is mostly stateless request/response
- Cold-start workarounds: Lambda provisioned concurrency, warmup cron pings, keep-alive lambdas
- Egress-cost pain: heavy outbound bandwidth on EC2/Lambda/Cloud Run noted in infra cost reviews
- Edge-curious stacks already partway there: next on @cloudflare/next-on-pages, Hono, itty-router, nitro with a cloudflare preset, `@cloudflare/workers-types`
- Geographic latency hacks: multi-region Lambda deploys, CloudFront-in-front-of-Lambda, manual edge replication
- Presence of wrangler.toml/wrangler.jsonc or `wrangler` in devDependencies (already a Worker — flag for using more bindings instead of external services)

**Ideas:**
- Port a small stateless Express/Lambda API (auth proxy, webhook receiver, BFF, image/redirect edge logic) to a Worker to kill cold starts and egress fees and get global low latency for free
- Replace a cron box / scheduled Lambda with a Worker Cron Trigger, and a SQS+worker queue pattern with Cloudflare Queues + a Queue consumer Worker
- Use a Worker as the front door that composes platform bindings (D1 for SQL, KV for config/cache, R2 for objects, Workers AI for inference) instead of standing up Postgres + Redis + S3 + a model host separately

**Pairs with:** Workers KV, D1, R2, Durable Objects, Queues, Workers AI, Vectorize, Hyperdrive, Workflows, Cloudflare Pages / Static Assets

**Pricing:** Free tier: 100,000 requests/day, 10 ms CPU time per invocation, no duration charge. Paid (Standard usage model): $5/mo base, 10M requests included then +$0.30/additional million; 30M CPU-milliseconds included then +$0.02/additional million CPU-ms. You pay for requests + CPU time (not wall-clock duration), and egress/bandwidth is free. CPU cap 30s default, up to 5 min/invocation (15 min for Cron/Queue consumers). (verify — drifts)

**Limits:**
- CPU time: 10 ms/request (Free) vs default 30s, max 5 min/request (Paid); 15 min for Cron Triggers / Queue consumers / Durable Object alarms
- Memory: 128 MB per isolate (JS heap + WASM combined) on both plans
- Worker size: 3 MB compressed (Free) / 10 MB compressed (Paid); up to 64 MB uncompressed
- Subrequests: 50/request (Free) vs 10,000/request (Paid, expandable up to 10M)
- Workers per account: 100 (Free) / 500 (Paid)
- Env vars: 64/Worker (Free) / 128/Worker (Paid), 5 KB size limit each
- Daily requests capped at 100,000 on Free (resets midnight UTC); no daily cap on Paid
- ctx.waitUntil() post-response work limited to ~30s

**Notes:** Workers is the compute substrate, so this is less 'replace a SaaS' and more 'replace your serverless/VPS host' — the strongest pitch when code is stateless request/response and would benefit from no cold starts, free egress, and global execution. Trade-offs to be honest about: the 128 MB-per-isolate and CPU-ms model is wrong for long CPU-bound batch jobs or heavy in-memory workloads (reach for Cloudflare Containers/Workflows or a real VM instead); not a drop-in for full Node — it's a web-standard runtime with partial Node compat (nodejs_compat flag), so native addons / arbitrary npm with C bindings may not work; and adopting the binding ecosystem (D1/KV/R2/DO) creates real Cloudflare lock-in (the Worker code itself is fairly portable web-standard JS, the bindings are not). Pricing and limits verified against the live pricing/limits pages this run but Cloudflare changes these often — re-verify before quoting.

**Docs:** https://developers.cloudflare.com/workers/index.md, https://developers.cloudflare.com/workers/reference/how-workers-works/index.md, https://developers.cloudflare.com/workers/platform/pricing/index.md, https://developers.cloudflare.com/workers/platform/limits/index.md, https://developers.cloudflare.com/workers/runtime-apis/bindings/index.md

---

## Cloudflare Workflows
`workflows` · Compute / Durable Execution · confidence: `high` · lock-in: `deep`

**Is:** A durable execution engine on Workers that runs multi-step processes which survive failures, timeouts, and restarts by automatically persisting state and retrying steps, and can pause for seconds to weeks (sleeping, or waiting on external events) without consuming compute.

**Replaces:** A hand-rolled durable-job stack: a queue + a worker pool + a state table that records 'which step did we reach' + cron-driven retry/backoff + idempotency keys to avoid re-running side effects. In SaaS terms it replaces paying for Temporal Cloud / Inngest / AWS Step Functions, or wiring BullMQ/Sidekiq/Celery on top of a Redis box.

**Use it via:** Worker binding declared in wrangler.jsonc/.toml as [[workflows]] with name, binding (e.g. MY_WORKFLOW), class_name, and optional script_name for cross-script calls. Logic lives in a class extending WorkflowEntrypoint<Env, Params> with async run(event, step) using step.do(name, cb), step.sleep(name, duration), step.sleepUntil(name, ts), step.waitForEvent(name, {type, timeout}). Drive instances from a Worker via env.MY_WORKFLOW.create({id, params}), env.MY_WORKFLOW.get(id) then .status()/.pause()/.resume()/.restart()/.terminate()/.sendEvent(). Also exposed via REST API under /accounts/{account_id}/workflows/... (instances create/list endpoints) and the wrangler workflows CLI. Python SDK available.

**Capabilities:**
- Durable step execution: each step.do() result is persisted, so a crash or redeploy resumes from the last completed step instead of restarting
- Automatic per-step retries with configurable backoff (up to 10,000 retries per step)
- step.sleep() / step.sleepUntil() pause for up to 365 days with zero CPU billed while idle
- step.waitForEvent() blocks a running instance until an external event (webhook, approval, callback) arrives — default 24h timeout, enables human-in-the-loop
- Instance lifecycle control: create, get/status, pause, resume, restart, terminate, sendEvent
- Triggerable from a Worker fetch handler, a Cron Trigger (scheduled handler), a Queue consumer, the REST API, wrangler CLI, a Durable Object, or another Workflow (child workflows)
- Waiting instances (sleeping/retrying/awaiting events) do not consume concurrency slots — millions can wait at once
- Python Workflows SDK in addition to TypeScript, including a DAG style
- Built-in observability for instance state, and status values: queued/running/paused/errored/terminated/complete/waiting/unknown

**Detection signals — the lens fires on these:**
- npm deps: bullmq, bee-queue, agenda, kue, graphile-worker, pg-boss, node-resque
- Python deps: celery, rq, dramatiq, apscheduler, prefect, dagster, airflow/apache-airflow, temporalio
- Ruby: sidekiq, resque, good_job, delayed_job; JS: bull, agenda
- SaaS SDKs: @temporalio/client, inngest, @trigger.dev/sdk, @restate/* — or AWS @aws-sdk/client-sfn (Step Functions), StateMachineArn / states:StartExecution in IaC
- A DB table named jobs/tasks/workflow_state/saga_state/job_runs with columns like status, current_step, attempts/retry_count, next_run_at, idempotency_key, last_error
- Redis used as a job broker: REDIS_URL alongside worker/consumer processes, *.process()/.add() job queue calls
- Cron jobs (node-cron, a Kubernetes CronJob, or a Cloudflare scheduled handler) that scan for 'stuck' or 'pending' rows and retry them — a hand-rolled retry loop
- Hand-written exponential-backoff/retry helpers wrapping external API calls (retry(fn, {attempts, backoff}), p-retry)
- Long-running orchestration that must outlive a single request: multi-step onboarding, trial-expiry/dunning emails, ETL/data pipelines, AI agent pipelines with approval gates, order/payment sagas
- Idempotency-key plumbing added specifically to make re-runnable side effects safe
- Already on Cloudflare (existing wrangler.jsonc, Workers, Queues, R2, D1, Durable Objects) but orchestrating jobs off-platform

**Ideas:**
- Replace a BullMQ/Redis or Celery job pipeline (e.g. multi-step user onboarding, trial-expiration and dunning emails, scheduled report generation) with a single WorkflowEntrypoint where each stage is a step.do() — getting durable state, retries, and step.sleep() delays for free instead of a queue + state table + cron retry scanner.
- Build a human-in-the-loop AI/agent pipeline: run generation steps, then step.waitForEvent() to block on a reviewer's approval webhook before publishing — no separate 'paused job' table or polling loop.
- Move ETL / fan-out data pipelines that currently chain Queue messages with manual checkpointing onto Workflows so a mid-pipeline failure resumes from the last completed step rather than reprocessing, and orchestrate sub-jobs via child workflows.

**Pairs with:** Cloudflare Queues (trigger a Workflow per message; offload fan-out), Durable Objects (Workflows build on the same durable primitives; trigger from within a DO), R2 / D1 / KV (read/write durable data inside steps; the canonical example fetches from R2), Workers AI / AI Gateway (multi-step AI/agent pipelines with retries and approval gates), Cron Triggers (kick off scheduled Workflow runs from a scheduled handler), Email Routing / Email Sending (lifecycle email sequences as workflow steps)

**Pricing:** No separate plan: Workflows are billed as Workers and share the same CPU-time and request SKUs. Free plan: included with Workers Free — 100,000 requests/day (shared with Workers), 10 ms CPU per invocation, 1 GB storage. Workers Paid: 10M requests/mo then $0.30/additional million; 30M CPU-ms/mo then $0.02/additional million; 1 GB storage/mo then $0.20/GB-month (storage billing began Sep 15, 2025). Steps are NOT billed separately, and idle time (step.sleep, waiting on events/APIs) incurs no CPU charge. (verify — drifts)

**Limits:**
- Steps per instance: 1,024 (Free) / 10,000 default, configurable up to 25,000 (Paid)
- Concurrent (actively running) instances: 100 (Free) / 50,000 (Paid) — waiting/sleeping/retrying instances do NOT count
- Max step result (return) size: 1 MiB on both plans; larger output via ReadableStream<Uint8Array>
- Max persisted state per instance: 100 MB (Free) / 1 GB (Paid)
- CPU time per step: 10 ms (Free) / 30 s default, configurable to 5 min (Paid)
- Max sleep duration: 365 days (both plans)
- Max retries per step: 10,000
- Subrequests per request: 50 (Free) / 10,000 default, up to 10M (Paid)
- Instance retention: 3 days (Free) / 30 days (Paid)
- Daily executions: 100,000/day (Free) / unlimited (Paid)
- Workflow scripts per account: 100 (Free) / 500 (Paid)
- Creation rate: 100/s (Free) / 300/s per account + 100/s per workflow (Paid)
- Queued instances cap: 100,000 (Free) / 2,000,000 (Paid)

**Notes:** Platform lock-in: the WorkflowEntrypoint/step.* programming model is Cloudflare-specific (closest analog is Temporal/Step Functions), so porting off later means a rewrite, not a config change. The 10 ms CPU-per-step cap on the Free plan is tiny — real workloads need Workers Paid. Steps must be deterministic-ish and idempotent: a step can re-run on retry, and only structured-cloneable results ≤1 MiB persist between steps, so it is NOT a drop-in for in-memory job logic that passes huge blobs around (stream those instead). Not the right tool for sub-second synchronous request/response work (just use a Worker) or for high-throughput stream processing (use Queues/Pipelines). Heavy compute per step still bills as Workers CPU. I did not fetch the exact REST endpoint paths or wrangler CLI subcommand strings (the trigger page deferred to other docs), so those surface details are described by shape rather than verbatim; everything else is grounded in the pages fetched this run.

**Docs:** https://developers.cloudflare.com/workflows/llms.txt, https://developers.cloudflare.com/workflows/index.md, https://developers.cloudflare.com/workflows/reference/pricing/index.md, https://developers.cloudflare.com/workflows/reference/limits/index.md, https://developers.cloudflare.com/workflows/build/workers-api/index.md, https://developers.cloudflare.com/workflows/build/trigger-workflows/index.md

---

## Dynamic Workers (Worker Loader)
`dynamic-workers` · Compute / Code sandboxing · confidence: `high` · lock-in: `portable`

**Is:** A Worker binding that spins up unlimited isolated Workers on demand to execute arbitrary code supplied at runtime — a managed V8-isolate sandbox for untrusted or AI-generated code.

**Replaces:** A self-hosted code-execution sandbox: Firecracker/gVisor microVMs, Docker-per-execution on a container host, or a third-party code-runner SaaS (E2B, Modal, Daytona, Judge0/Piston). Also replaces hand-rolled `vm2`/`isolated-vm`/`node:vm` sandboxes that aren't actually secure.

**Use it via:** Worker binding. wrangler.jsonc: "worker_loaders": [{ "binding": "LOADER" }] (TOML: [[worker_loaders]]). In-Worker: env.LOADER.load({ compatibilityDate, mainModule, modules: { 'index.js': { js: code } }, env: { ...bindings }, globalOutbound, tails }) or env.LOADER.get(id, async () => WorkerCode); invoke via worker.getEntrypoint().fetch(request). Limits set as { cpuMs, subRequests }. For AI agents: import { createCodeTool } from '@cloudflare/codemode/ai' + DynamicWorkerExecutor from '@cloudflare/codemode'. No REST API — binding-only.

**Capabilities:**
- Load arbitrary JS/Python code strings at runtime into a fresh, isolated Worker (no pre-deploy, no wrangler deploy step per script)
- Two modes: load(code) for one-shot execution, get(id, callback) to cache/keep a Dynamic Worker warm across requests by ID
- Capability-based sandbox: the loaded Worker can only access bindings you explicitly pass via the env object; stubs can't be forged
- Network egress control via globalOutbound — set to null to block all fetch()/connect(), or route through a custom WorkerEntrypoint gateway to inspect/modify/block/audit every outbound request
- Per-invocation custom resource limits: cpuMs and subRequests
- Pass live bindings into untrusted code: KV, R2, D1, Durable Object Facets, and custom RPC WorkerEntrypoint classes (with props-based scoping to hide secrets/key-prefixes)
- Powers Code Mode (@cloudflare/codemode): let an LLM write code instead of doing many tool calls, claimed up to ~80% inference token/cost savings
- Observability via Tail Workers (tails config) and console.log capture (returned in ExecuteResult.logs via DynamicWorkerExecutor)

**Detection signals — the lens fires on these:**
- npm: isolated-vm, vm2, node:vm / new Function() / eval() used to run user- or LLM-supplied code
- npm: @e2b/code-interpreter, e2b, @daytonaio/sdk, modal, piston, judge0 clients — paid third-party sandbox runners
- Dockerfile-per-execution, Firecracker/gVisor/Kata, Docker socket spawning a container per code run, Kubernetes Job-per-task patterns
- An AI agent that does many sequential tool calls / JSON function-calling round trips that could be collapsed into one generated code script (Code Mode candidate)
- LLM output being written to a temp .js/.py file and shelled out via child_process.exec / subprocess — classic unsafe code-exec smell
- Code-interpreter / 'run this snippet' / notebook-execution features, vibe-coding playgrounds, preview/sandbox-per-user-app architectures
- Multi-tenant 'run customer plugins/automations' systems hand-rolling isolation
- Existing Cloudflare Workers project (wrangler.jsonc present) already on Workers Paid — strong fit signal

**Ideas:**
- Convert an existing multi-step tool-calling AI agent to Code Mode: have the model emit one code block executed in a Dynamic Worker (globalOutbound:null, bindings injected) to cut tool-call round trips and tokens
- Replace an E2B/Docker code-interpreter backend with env.LOADER.load() so generated data-analysis / file-transform code runs in a per-request V8 isolate with cpuMs + subRequests caps
- Run untrusted customer-supplied plugins/automations safely: block the internet by default, then expose only scoped KV/R2/D1 and a vetted HTTP gateway via a custom WorkerEntrypoint outbound

**Pairs with:** Workers AI / AI Gateway (the LLM that generates the code), @cloudflare/codemode + AI SDK (createCodeTool, DynamicWorkerExecutor), Agents SDK / Durable Objects (stateful agent loop calling the loader; Durable Object Facets for sandbox storage), KV / R2 / D1 (scoped bindings handed to the sandboxed code), Tail Workers (observability for what the dynamic code did), @cloudflare/worker-bundler (compiles TS + resolves npm deps before loading)

**Pricing:** Workers Paid only, no free tier. 1,000 unique Dynamic Workers created/month included, then $0.002 per Worker per day. Requests and CPU bill on the standard Workers model: 10M requests + 30M CPU-ms included, then $0.30/M requests and $0.02/M CPU-ms (CPU includes startup time). (verify — drifts)

**Limits:**
- Workers Paid plan only — no free tier
- Per-invocation limits documented: cpuMs and subRequests (memory/duration maxima not stated in docs read this run — verify)
- CPU billing includes startup time (isolate init + code parsing), unlike standard Workers which bill execution only — cold/short scripts cost relatively more
- A Dynamic Worker is keyed by Worker ID + code; any change to either counts as a new Worker for the daily-created billing metric
- get(id) keep-warm is best-effort: 'no guarantee of reuse' on subsequent calls
- TypeScript must be pre-compiled (use @cloudflare/worker-bundler); JS and Python supported directly

**Notes:** Do NOT confuse with Workers for Platforms: that product uploads/deploys tenant Workers ahead of time and dispatches via dispatch_namespaces + env.DISPATCH.get(name). Dynamic Workers loads ephemeral code at runtime via the Worker Loader binding (worker_loaders / env.LOADER) — different config, different shape. The Worker Loader runtime API page lives under /workers/runtime-apis/bindings/worker-loader/. Lock-in: the binding API, globalOutbound gateway pattern, and codemode package are Cloudflare-specific; portable code is the user's JS/Python, but the sandbox harness is not. Not the right tool for long-running/stateful background jobs (use Workflows/Containers/Durable Objects) or for code needing full Linux/native binaries or a real filesystem (use Cloudflare Containers or the Sandbox SDK instead — Dynamic Workers is a V8-isolate, not a microVM). Per-invocation memory/duration maxima and exact default limit numbers were not quoted on the limits page fetched this run.

**Docs:** https://developers.cloudflare.com/dynamic-workers/llms.txt, https://developers.cloudflare.com/dynamic-workers/index.md, https://developers.cloudflare.com/dynamic-workers/pricing/index.md, https://developers.cloudflare.com/dynamic-workers/getting-started/index.md, https://developers.cloudflare.com/dynamic-workers/api-reference/index.md, https://developers.cloudflare.com/dynamic-workers/usage/bindings/index.md, https://developers.cloudflare.com/dynamic-workers/usage/egress-control/index.md, https://developers.cloudflare.com/dynamic-workers/usage/limits/index.md, https://developers.cloudflare.com/workers/runtime-apis/bindings/worker-loader/

---

## Workers Builds
`workers-builds` · Compute / CI-CD · confidence: `high` · lock-in: `portable`

**Is:** Git-connected CI/CD that builds and deploys your Worker on every push, run on Cloudflare's own build infrastructure.

**Replaces:** A GitHub Actions / GitLab CI / CircleCI pipeline whose entire job is to checkout, install, build, and run `wrangler deploy` against Cloudflare.

**Use it via:** Dashboard: Workers & Pages > (Worker) > Settings > Builds to connect repo and set build/deploy commands. Wrangler config file (wrangler.toml / wrangler.jsonc) is required and its `name` must match the dashboard Worker name. Deploy command is typically `wrangler deploy` (deploy) or `wrangler versions upload` (preview only). Builds API reference + Deploy Hook URLs for external triggering. GitHub/GitLab integration via OAuth app install.

**Capabilities:**
- Connect a GitHub or GitLab repo to a Worker; a push to the connected branch triggers a build + deploy (configured via Settings > Builds in the dashboard).
- Runs a configurable build command and deploy command; with `wrangler deploy` as the deploy command, a successful build is uploaded as a version and promoted to the Active Deployment.
- Preview-only mode: set deploy command to `npx wrangler versions upload` to build + upload a version (with a generated preview URL) without promoting it to production.
- Build branches / automatic pull request builds: non-production branches and PRs can trigger builds for preview before merge.
- Build watch paths to skip builds when irrelevant paths change (monorepo support).
- Build caching to speed up dependency install / build steps across runs.
- Deploy Hooks: unique URLs to trigger a build from an external system (rate-limited 10/min per Worker, 100/min per account).
- Build-time environment variables (up to 64, 5 KB each) and a Builds API reference for programmatic management.

**Detection signals — the lens fires on these:**
- A `.github/workflows/*.yml` (or `.gitlab-ci.yml` / `.circleci/config.yml`) whose only real step is `npm ci && npx wrangler deploy` (or uses `cloudflare/wrangler-action`).
- `CLOUDFLARE_API_TOKEN` / `CF_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` stored as CI secrets purely to authenticate wrangler deploys.
- A wrangler.toml/wrangler.jsonc in the repo paired with a hand-written deploy pipeline.
- Custom shell scripts (deploy.sh) that wrap `wrangler deploy` with branch logic.
- Multiple near-identical workflow files for prod vs preview/staging branch deploys.

**Ideas:**
- This GitHub Actions workflow only does `npm ci && wrangler deploy` with a CF API token secret — replace it with Workers Builds connected to the repo so pushes auto-deploy without managing CI minutes or tokens.
- You deploy preview branches via a second CI workflow — use Workers Builds branch/PR builds with `wrangler versions upload` to get preview URLs per PR instead.
- Your monorepo rebuilds the Worker on every commit — configure Workers Builds watch paths + build caching so only relevant changes trigger a deploy.

**Pairs with:** Workers, Wrangler, Workers Observability, Workers Logs, Workers (Versions & Gradual Deployments)

**Pricing:** Build minutes: 3,000/month on Free, 6,000/month on Workers Paid then +$0.005 per build minute. Concurrency: 1 (Free) / 6 (Paid). Build timeout 20 min. Build runner: 2 vCPU/8 GB (Free), 4 vCPU/8 GB (Paid), 20 GB disk. (verify — drifts.)

**Limits:**
- 20-minute hard build timeout per build.
- 1 concurrent build on Free, 6 on Paid (queued beyond that).
- GitHub/GitLab only for native git integration (no Bitbucket native connect; use Deploy Hooks for other systems).
- 64 build env vars, 5 KB each; Deploy Hooks rate-limited 10/min per Worker, 100/min per account.
- Worker `name` in wrangler config must exactly match the dashboard Worker.

**Notes:** Tighter integration than external CI but Cloudflare-specific: your build/deploy pipeline now lives in the CF dashboard, not in-repo YAML, which reduces portability if you later leave Workers. Cloudflare still documents External CI/CD (GitHub Actions / GitLab CI with wrangler-action) as a supported alternative — prefer that when you need a shared org-wide pipeline, custom runners, complex multi-service orchestration, or build steps unrelated to the Worker. Native git connect is GitHub/GitLab only.

**Docs:** https://developers.cloudflare.com/workers/ci-cd/builds/, https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/, https://developers.cloudflare.com/workers/ci-cd/builds/git-integration/, https://developers.cloudflare.com/workers/ci-cd/index.md

---

## Workers for Platforms
`workers-for-platforms` · Multi-tenant compute / Edge functions-as-a-service · confidence: `high` · lock-in: `portable`

**Is:** Lets your own customers write and deploy their own Workers code into your platform, with each tenant's script isolated and dynamically dispatched at request time.

**Replaces:** A hand-rolled multi-tenant code-execution layer: spinning up per-customer containers/VMs/Lambdas, a homegrown plugin/sandbox runtime (vm2, isolated-vm, QuickJS), or a queue of node child_process workers to run untrusted customer-supplied functions.

**Use it via:** wrangler.jsonc: "dispatch_namespaces": [{ "binding": "DISPATCHER", "namespace": "my-dispatch-namespace" }]. In the dispatch Worker: const userWorker = env.DISPATCHER.get(userWorkerName); return await userWorker.fetch(request). Upload a tenant script via REST multipart PUT to /accounts/{account_id}/workers/dispatch/namespaces/{namespace}/scripts/{script_name}; list namespaces under /accounts/{account_id}/workers_for_platforms/dispatch/namespaces.

**Capabilities:**
- Dispatch namespace = a container holding all your customers' Workers, with no per-account script limit (1000 scripts included, $0.02 each beyond)
- Dynamic dispatch Worker is your entry point: runs auth/rate-limiting/routing, then calls the right tenant Worker via env.DISPATCHER.get(name)
- User/customer Workers run in 'untrusted mode' — no cache sharing, no access to request.cf — isolated per tenant
- Outbound Workers intercept fetch() egress from user Workers to log, block, or rewrite external calls
- Per-tenant custom limits on CPU time and subrequests; tags for bulk script management
- User Workers can still bind to KV, R2, etc. (env.USER_KV.get/put) scoped per customer

**Detection signals — the lens fires on these:**
- Sandboxing libs for untrusted user code: isolated-vm, vm2, vm (node builtin), quickjs-emscripten, deno subprocess
- Per-customer container/function orchestration: spawning Lambda/Fargate/Cloud Run/Fly Machines per tenant, child_process.fork in a worker pool
- A 'plugins', 'functions', 'extensions', 'custom code', or 'user scripts' table/feature where tenants submit JS to run
- eval() / new Function() gated behind tenant auth, or a homegrown DSL interpreter for customer logic
- Low-code / app-builder / 'serverless for our users' / Shopify-Functions-style product shape
- A dispatcher/router service that maps tenant -> their handler before executing

**Ideas:**
- Offer end-customers a 'write your own webhook handler / transform function' feature without standing up sandbox infra
- Build a Shopify-Functions-style extensibility layer where merchants deploy custom checkout/pricing logic
- Run untrusted customer middleware (auth hooks, request rewriting) with per-tenant CPU/subrequest caps and an outbound Worker for egress control

**Pairs with:** Workers KV / R2 / D1 (bound per-tenant inside user Workers), Service bindings (the static-relationship alternative when tenant Workers are known at build time), Outbound Workers for egress governance

**Pricing:** Workers for Platforms Paid plan: $25/mo. Includes 20M requests/mo ($0.30/additional million), 60M CPU-ms/mo ($0.02/additional million CPU-ms), 1000 scripts ($0.02/additional script). No duration charge. The whole dispatch->user->outbound chain bills as 1 request; subrequests not billed. No free tier — requires the paid plan. (verify — drifts)

**Limits:**
- Max 30s CPU time per invocation; max 15 min CPU per Cron Trigger / Queue Consumer invocation
- User Workers run untrusted: no cache sharing, no request.cf access
- Per-tenant CPU-time and subrequest limits enforced by plan; configurable via custom limits

**Notes:** Two products live under 'Cloudflare for Platforms' — this is the COMPUTE one. NOT the right tool when the set of Workers is known statically at deploy time (use plain Service bindings instead — cheaper, simpler). Strong lock-in: tenant code is written against the Workers runtime + Cloudflare bindings, not portable to Lambda/containers. The bindings doc page itself only surfaced REST multipart-upload metadata; the wrangler dispatch_namespaces snippet and env.DISPATCHER.get() API were confirmed from the dynamic-dispatch config page. The exact namespaces REST path is inferred from the API index URL in the llms.txt index, not from a fetched body.

**Docs:** https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/how-workers-for-platforms-works/index.md, https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/configuration/dynamic-dispatch/index.md, https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/configuration/bindings/index.md, https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/reference/pricing/index.md

---
