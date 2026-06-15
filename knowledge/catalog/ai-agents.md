# AI & Agents

_8 products. Part of the Flarepilled catalog — see `../INDEX.md`._

## Agent Lee (Cloudflare dashboard AI assistant)
`agent-lee` · AI assistant / dashboard copilot · confidence: `high` · lock-in: `portable`

**Is:** An AI co-pilot built into the Cloudflare dashboard that answers account-specific questions, runs diagnostics (DNS/cert/WHOIS lookups), and performs approved write actions on your zone (DNS records, security settings) via natural language.

**Replaces:** Not a build-it-yourself substitute — it's an operator-productivity tool. Closest analog: hand-navigating the Cloudflare dashboard/API by hand, or writing your own internal 'ops bot' that wraps the Cloudflare API for DNS/security changes.

**Use it via:** No developer API or Worker binding. Accessed in-dashboard via the 'Ask AI' button (upper-right). Interesting mainly as a live example of what the Agents SDK + Durable Objects + Workers AI can build.

**Capabilities:**
- Answers questions using your real account data (zones, DNS, firewall rules, Workers scripts, registrar data) instead of generic docs
- Executes write operations (e.g. add an A record, enable Always Use HTTPS) — each requires explicit user approval
- Runs diagnostics: DNS lookups, certificate inspection, WHOIS lookups
- Generates inline charts from your analytics data
- Built on Cloudflare's own Agents SDK + Durable Objects + Workers AI (a reference implementation of the agent stack)

**Detection signals — the lens fires on these:**
- Internal tooling/scripts that wrap the Cloudflare API (cloudflare npm SDK, CF_API_TOKEN) to manage DNS or WAF settings — the dashboard assistant covers some of this interactively
- Runbooks full of manual 'go to the Cloudflare dashboard and toggle X' steps
- Teams building their own LLM-over-internal-API chatbots — Agent Lee is the canonical Agents-SDK-on-DO pattern to copy

**Ideas:**
- Use it to triage DNS/cert/WHOIS questions about your own zones without leaving the dashboard
- Study it as the reference architecture (Agents SDK + Durable Objects + Workers AI) when building your own approval-gated 'ops agent'

**Pairs with:** Agents SDK, Durable Objects, Workers AI, Cloudflare DNS, WAF

**Pricing:** Free — in beta, only on accounts on the Free plan. (verify — drifts)

**Limits:**
- Beta, and currently only available to accounts on a Free plan
- No code generation
- Cannot access payment methods, API tokens, raw logs, or other accounts' data
- Sessions don't span multiple accounts and don't retain prior conversation context
- All write operations require manual approval; not a replacement for official support on billing/outages

**Notes:** Listed on the AI roster as 'Cloudflare Agent'; product/docs name is 'Agent Lee'. This is a first-party SaaS feature, NOT a product you embed — 'replaces' is weak by design. Its real value to a Flarepilled reader is as a worked example of the Agents-SDK pattern. Free-plan-only availability is unusual and likely to change.

**Docs:** https://developers.cloudflare.com/agent-lee/llms.txt, https://developers.cloudflare.com/agent-lee/index.md

---

## Agent Memory
`agent-memory` · AI / Agents · confidence: `high` · lock-in: `deep`

**Is:** A managed memory layer for AI agents that auto-extracts facts, events, instructions, and tasks from conversations and recalls relevant context across sessions, scoped per user/tenant.

**Replaces:** A hand-rolled long-term-memory stack: an embeddings cron + a vector DB (pgvector/Pinecone/Vectorize) + a Postgres/Redis table for raw messages + your own LLM 'extract-facts-from-this-chat' prompt + a per-user namespacing/RAG retrieval layer. Also overlaps with hosted memory SaaS like Mem0 / Zep / Letta (MemGPT).

**Use it via:** Worker binding: wrangler.jsonc key "agent_memory": [{ "binding": "MEMORY", "namespace": "<NAME>" }]; `npx wrangler types` emits `MEMORY: AgentMemoryNamespace`. Get a profile handle via `env.MEMORY.getProfile("user-123")`, then call `ingest(messages, opts?)`, `remember(memory)`, `recall(query, opts?)`, `list(opts?)`, `get(id)`, `delete(id)`. REST: POST/GET/DELETE under https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/agent-memory/namespaces/<NS>/profiles/<PROFILE>/{ingest|recall|remember|memories[/<ID>]}, auth `Authorization: Bearer <API_TOKEN>`. Profiles auto-create on first write.

**Capabilities:**
- Automatic memory extraction: an LLM reads ingested conversation messages and identifies discrete memorable items, classifying each as Fact, Event, Instruction, or Task
- Dual storage + retrieval: memories written to durable storage with full-text search indexes; non-task memories also embedded as vectors for semantic search
- recall() runs multiple retrieval strategies in parallel (keyword indexes, topic-key lookups, semantic vector indexes, raw messages), ranks, and synthesizes a natural-language answer
- Per-entity isolation via namespace > profile > memory hierarchy; recall() on one profile never returns another profile's memories
- Idempotency built in: content-addressed messages + deterministic session IDs dedupe; Facts and Instructions support supersession (update-in-place)
- Explicit writes via remember() (single memory, auto-classified) in addition to conversation ingest()
- Optional session grouping of memories from the same interaction; sessions scoped per profile so IDs can be reused across profiles

**Detection signals — the lens fires on these:**
- npm packages mem0ai, zep-cloud / zep-js, @letta-ai / letta, llamaindex memory modules, langchain ConversationSummaryMemory / VectorStoreRetrieverMemory
- A bespoke 'summarize / extract facts from this conversation' LLM prompt whose output is stored for later retrieval
- An embeddings pipeline feeding a vector store keyed by user/tenant: OpenAI embeddings + Pinecone/Weaviate/pgvector/Qdrant, or Cloudflare Vectorize + Workers AI bge embeddings, used specifically for 'what does this user prefer / what did we discuss' recall
- A `messages` / `conversation_history` table (Postgres, D1, Redis) plus a separate `memories` or `user_facts` table the app writes summarized facts into
- Per-user RAG namespacing logic (filtering vector queries by user_id / org_id) hand-built to keep one user's memory from leaking into another's
- Cloudflare Agents SDK (agents package) projects storing long-lived user context in Durable Object SQLite and re-implementing extraction/recall by hand
- Cron/queue jobs that periodically re-summarize chat logs into a 'profile' or 'user memory' blob

**Ideas:**
- Give a support or sales agent durable per-customer memory (preferences, past tickets, account rules) so it stops re-asking known facts across separate chats — ingest() each transcript, recall() at the start of the next.
- Replace a custom pgvector + embeddings-cron 'user memory' service behind a chatbot with a single managed namespace/profile, dropping the extraction prompt and the vector-index plumbing.
- Store org-level operating rules and reusable workflows as Instructions in a shared profile, and short-lived session to-dos as Tasks, letting one recall() blend long-term policy with current-session state.

**Pairs with:** Agents (Agents SDK) — gives stateful agents the long-term memory layer to complement Durable Object working state, Workers AI — LLM/embeddings for the agent itself; Agent Memory handles extraction/embedding internally, Vectorize / D1 — the DIY primitives this replaces if you were assembling memory yourself, AI Gateway — observe/cache the agent's own model calls alongside memory recall

**Pricing:** Free during private beta — Cloudflare states it is not currently billing for Agent Memory and will give at least 30 days notice before charging. No billing unit (per-memory / per-op / per-token / storage) defined yet. (verify — drifts)

**Limits:**
- 500 messages per ingest() call
- 32 KB (32,768 bytes UTF-8) max message content size
- 1 KB (1,024 bytes UTF-8) max recall query size
- Session ID <= 64 chars; profile name <= 100 chars; namespace name <= 32 chars
- List page size 1–1,000 (default 20)
- Not documented: max namespaces, max profiles/namespace, max memories/profile, rate limits, retention/storage quotas

**Notes:** Private beta (as of the fetched docs, dated examples reference 2026): API surface and especially pricing/limits can change with little notice — treat as not production-frozen. The docs deliberately do NOT disclose the underlying storage/embedding model (frames memory as Facts/Events/Instructions/Tasks, not the academic episodic/semantic/working split), so you can't tune the retrieval internals. Lock-in: memories live in Cloudflare's managed store with no documented bulk export, and recall() returns a synthesized natural-language answer rather than raw rows, so migrating off or auditing exact stored facts may be harder than a self-hosted vector DB you own. Not the right tool when you need full control over the embedding model, custom ranking, raw-vector access, or on-prem/regional data residency. Overkill if you only need simple keyed session storage (use KV/Durable Objects). Could not verify rate limits, retention, or whether a self-serve (non-private-beta) tier is open yet.

**Docs:** https://developers.cloudflare.com/agent-memory/llms.txt, https://developers.cloudflare.com/agent-memory/index.md, https://developers.cloudflare.com/agent-memory/concepts/how-agent-memory-works/index.md, https://developers.cloudflare.com/agent-memory/api/workers-api/index.md, https://developers.cloudflare.com/agent-memory/api/http-api/index.md, https://developers.cloudflare.com/agent-memory/concepts/namespaces-profiles/index.md, https://developers.cloudflare.com/agent-memory/platform/pricing/index.md, https://developers.cloudflare.com/agent-memory/platform/limits/index.md

---

## Cloudflare AI (umbrella)
`ai-umbrella` · AI / ML platform · confidence: `high` · lock-in: `sticky`

**Is:** An umbrella over Cloudflare's AI building blocks: serverless model inference (Workers AI), an LLM proxy/observability layer (AI Gateway), managed RAG (AI Search), a vector DB (Vectorize), an agent framework (Agents), headless browsers, sandboxes, and AI-crawler control.

**Replaces:** A self-assembled AI stack: GPU boxes or a hosted inference API for models + a separate vector DB (self-hosted pgvector/Pinecone) + a homegrown LLM gateway for caching/rate-limit/keys + a hand-built RAG ingestion cron — collapsed into one platform colocated with your Workers.

**Use it via:** Mostly Worker bindings declared in wrangler.jsonc: `ai` (env.AI.run('@cf/...')), `vectorize` (env.VECTORIZE), Agents SDK on Durable Objects, plus AI Gateway as a proxy URL endpoint (gateway.ai.cloudflare.com/v1/<acct>/<gateway>/...). Each sub-product also exposes its own REST API.

**Capabilities:**
- Workers AI: run ML/LLM models on Cloudflare GPUs via serverless inference (env.AI binding)
- AI Gateway: cache, rate-limit, retry, log and analyze calls to any model provider
- AI Search: fully managed RAG pipelines (ingest -> embed -> retrieve -> generate)
- Vectorize: store/query high-dimensional embeddings as a vector database
- Agents: build stateful AI agents (state persistence, tool/external-service calls)
- Browser Run: headless browser instances for AI data extraction
- Sandbox SDK / Dynamic Workers: spin up isolated on-demand code execution for agents
- AI Crawl Control: analyze and control third-party AI crawlers hitting your site

**Detection signals — the lens fires on these:**
- openai / @anthropic-ai/sdk / langchain / langchain_openai imports calling out to api.openai.com or api.anthropic.com directly (could front with AI Gateway)
- OPENAI_API_KEY / ANTHROPIC_API_KEY env vars with no proxy/caching layer
- pinecone-client / weaviate-client / @pinecone-database/pinecone / pgvector + an embeddings cron (could be Vectorize + AI Search)
- self-hosted RAG: a chunk/embed/upsert ingestion script feeding a vector store
- replicate / huggingface_hub / runpod / modal for GPU inference (could be Workers AI)
- puppeteer / playwright running in a container for scraping (could be Browser Run)
- a hand-rolled 'llm-gateway' / 'ai-proxy' service doing token rate-limits and response caching

**Ideas:**
- Front existing OpenAI/Anthropic calls with AI Gateway to get caching, spend limits, and per-app analytics without changing model providers
- Replace a self-hosted pgvector + embeddings cron with Vectorize + AI Search for a managed RAG pipeline
- Move Puppeteer scraping jobs onto Browser Run so agents can extract page data without running your own headless-Chrome fleet

**Pairs with:** Workers AI, Vectorize, AI Gateway, AI Search, Agents SDK, Durable Objects

**Pricing:** No single umbrella price — each sub-product bills separately (Workers AI per-neuron, Vectorize per query/stored dim, AI Gateway free observability tier, etc.). (verify — drifts)

**Limits:**
- Umbrella docs only enumerate sub-products; per-product limits/pricing live in each sub-product's docs (Workers AI, Vectorize, AI Gateway, AI Search, etc.)

**Notes:** This is a category page, not a single buyable product — when 'Flarepilled' flags it, the actionable hook is almost always one specific sub-product (AI Gateway, Vectorize, Workers AI, AI Search). The roster itself is fast-moving: 'AI Search' is the managed-RAG product (formerly AutoRAG), 'Cloudflare Agent' on the roster is the dashboard assistant (Agent Lee), and 'Dynamic Workers'/'Sandbox SDK' are the on-demand isolated-execution products for agents.

**Docs:** https://developers.cloudflare.com/ai/llms.txt, https://developers.cloudflare.com/ai/related-products/index.md

---

## Cloudflare AI Gateway
`ai-gateway` · AI / LLMOps · confidence: `high` · lock-in: `sticky`

**Is:** A proxy that sits between your app and any LLM provider (OpenAI, Anthropic, Google, Bedrock, Workers AI, etc.) adding caching, rate limiting, retries/fallbacks, cost tracking, logging, and analytics without changing your application logic.

**Replaces:** A hand-rolled LLM proxy/middleware layer: a Redis cache for prompt responses + token/cost accounting code + per-key rate limiting + try/catch retry-and-fallback logic + a logging pipeline for prompts/responses — or a paid LLMOps SaaS like Helicone / Portkey / LangSmith / Langfuse.

**Use it via:** Three surfaces. (1) Unified API (OpenAI-compatible): POST https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat/chat/completions — point any OpenAI SDK's baseURL at .../compat and set model to `{provider}/{model}`. (2) Provider-specific passthrough: https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/{provider} — keeps the original provider's schema, just swap the host. (3) Workers binding: wrangler.jsonc `{ "ai": { "binding": "AI" } }`, then env.AI.run(model, input, { gateway: { id, skipCache, cacheTtl, cacheKey, collectLog, metadata } }); env.AI.gateway(id) exposes getLog()/patchLog()/getUrl(); env.AI.aiGatewayLogId returns the last log id. No extra npm package — binding is built into Workers.

**Capabilities:**
- Drop-in proxy: change only the base URL (or swap api.openai.com for the gateway host) to route existing OpenAI/Anthropic/Google/Bedrock SDK calls through it
- Unified OpenAI-compatible endpoint: one base URL, switch providers/models via `{provider}/{model}` string (e.g. openai/gpt-5-mini, anthropic/claude-sonnet-4-5) without code changes
- Response caching from Cloudflare's global cache (cuts latency/cost on identical requests; TTL configurable up to 1 month, up to 25 MB/request cacheable)
- Rate limiting per gateway to control scaling and protect against abuse
- Dynamic Routing: fallbacks, retries, and A/B testing configured in dashboard with no code changes
- Spend Limits: cost-based dollar budgets tracked cumulatively across requests
- Analytics: requests, tokens, and cost metrics per gateway
- Persistent Logging of prompts/responses with retention, custom metadata, and Logpush export
- Guardrails: real-time content moderation on prompts and responses (billed as Workers AI inference)
- Data Loss Prevention (DLP): scans requests for PII / financial data
- Bring Your Own Keys (BYOK): store provider API keys in Cloudflare's encrypted infrastructure
- Token-based authentication to secure the gateway
- Custom Costs: override default pricing with negotiated rates
- Unified Billing: pay multiple providers through Cloudflare credits (5% fee)

**Detection signals — the lens fires on these:**
- Direct provider base URLs hardcoded: `api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, Bedrock endpoints — prime candidates to re-point at gateway.ai.cloudflare.com
- npm/pip deps: `openai`, `@anthropic-ai/sdk`, `@google/generative-ai`, `ai` (Vercel AI SDK), `langchain`, `cohere-ai`, `@ai-sdk/*`
- A hand-written LLM wrapper/`llmClient.ts`/`callModel()` with manual try/catch retry loops or provider failover (if openai fails, call anthropic)
- Redis/KV used as a prompt-response cache (cache key derived from hashed messages); env vars like REDIS_URL alongside OPENAI_API_KEY
- Custom token-counting / cost-accounting code (tiktoken usage, per-model price tables, usage rows written to a DB)
- Existing LLMOps vendor SDKs/keys: `helicone`, `portkey-ai`, `langsmith`, `langfuse`, HELICONE_API_KEY, LANGCHAIN_TRACING_V2, PORTKEY_API_KEY, LANGFUSE_* — AI Gateway overlaps these
- Per-user/per-key rate limiting middleware in front of LLM calls
- Logging of full prompts/completions to a custom table or log sink for later analysis
- Multiple provider API keys in env (OPENAI_API_KEY + ANTHROPIC_API_KEY + GEMINI_API_KEY) suggesting multi-provider routing that BYOK + Unified API could centralize
- Already on Cloudflare Workers and calling LLMs over fetch() without a gateway id in the URL

**Ideas:**
- Route every existing OpenAI/Anthropic call through AI Gateway by changing only the base URL, then turn on caching + analytics to see real token spend and cache hit rate before optimizing anything.
- Replace bespoke retry/failover code with dashboard-configured Dynamic Routing fallbacks (e.g. primary GPT-5 -> fallback Claude) and add a Spend Limit budget so a runaway loop can't burn the monthly budget.
- Add Guardrails + DLP in front of a user-facing chatbot to moderate prompts/responses and strip PII without writing a separate moderation service.
- Consolidate three provider API keys behind BYOK + the Unified OpenAI-compatible endpoint so the app picks models with a `{provider}/{model}` string and bills through one Cloudflare invoice.

**Pairs with:** Workers AI (env.AI.run with @cf/ models routes through the same binding), Cloudflare Workers / Pages (native AI binding), Secrets Store / BYOK for provider key management, Logpush -> R2/external sink for log archival, AI Agents SDK and Vercel AI SDK / OpenAI SDK / Anthropic SDK (all work behind the gateway)

**Pricing:** Core features (dashboard analytics, caching, rate limiting) are free on all plans — only a Cloudflare account needed. Persistent logs included up to plan limits (100k Free / 10M-per-gateway Paid). Guardrails billed as Workers AI token-based inference (scales with prompt/response length). Unified Billing adds a flat 5% fee on credits purchased (provider rates pass through with no markup). Logpush is Paid-only: 10M/month then +$0.05/million. DLP free, with deeper profiles via Zero Trust. (verify — drifts)

**Limits:**
- Gateways: 10/account (Free), 20/account (Paid); gateway name <= 64 chars
- Persistent logs: 100,000 total across all gateways (Workers Free); 10,000,000 per gateway (Workers Paid)
- Log size: 10 MB per log (larger not stored); log storage rate limit 500 logs/sec/gateway
- Caching: 25 MB max cacheable request; cache TTL max 1 month
- Custom metadata: 5 entries per request; datasets: 10 per gateway
- Logpush: Workers Paid only, 4 jobs/account, 1 MB/log, 10M/month then +$0.05/million
- Unified Billing request rate: 200 requests / 60s / gateway

**Notes:** Not an inference provider itself — it proxies your existing provider calls, so you still bring (and pay) the upstream LLM provider; it adds observability/control, not the model. Best fit when you already make many LLM calls and want caching/cost/rate-limit/failover without rebuilding middleware. Caching only helps with repeated identical (non-streaming-unique) requests; high-cardinality prompts see low hit rates. Lock-in is mild for the passthrough/unified endpoints (revert by changing the base URL back), heavier if you adopt Dynamic Routing, BYOK, Unified Billing, or the Workers env.AI binding. Guardrails/DLP/Logpush cost money or require Paid/Zero Trust tiers despite the 'free core' framing. Provider/model name strings (e.g. claude-sonnet-4-5, gpt-5-mini) and exact pricing pulled live 2026-06-15 and drift fast — re-verify before quoting. Did not separately verify streaming behavior, WebSocket/real-time API support, or per-provider quirks beyond the unified endpoint.

**Docs:** https://developers.cloudflare.com/ai-gateway/llms.txt, https://developers.cloudflare.com/ai-gateway/index.md, https://developers.cloudflare.com/ai-gateway/features/index.md, https://developers.cloudflare.com/ai-gateway/reference/pricing/index.md, https://developers.cloudflare.com/ai-gateway/reference/limits/index.md, https://developers.cloudflare.com/ai-gateway/usage/chat-completion/index.md, https://developers.cloudflare.com/ai-gateway/usage/worker-binding-methods/index.md, https://developers.cloudflare.com/ai-gateway/get-started/index.md

---

## Cloudflare AI Search
`ai-search` · AI / RAG & Retrieval · confidence: `high` · lock-in: `deep`

**Is:** A fully managed retrieval (RAG) pipeline that ingests your content, chunks and embeds it, stores the vectors, and answers natural-language queries — with optional LLM-generated responses — over a Workers binding, REST API, or built-in MCP endpoint.

**Replaces:** The hand-rolled RAG stack: an embeddings cron job + a self-hosted pgvector/Pinecone/Weaviate index + a chunking script + a document parser (unstructured.io / LlamaIndex loaders) + an OpenAI chat-completions wrapper glued together to answer questions over your docs.

**Use it via:** Worker binding in wrangler.jsonc: ai_search (single-instance, e.g. "binding": "MY_SEARCH") or ai_search_namespaces (multi-instance, e.g. "binding": "AI_SEARCH"). Code: const inst = env.AI_SEARCH.get("my-instance"); then await inst.search({messages:[...]}) -> {search_query, chunks[]} or await inst.chatCompletions({messages, model:"@cf/meta/llama-3.3-70b-instruct-fp8-fast", stream}) -> {choices[0].message.content, usage, chunks}. REST: POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai-search/instances/{instance}/search and .../chat/completions (OpenAI-compatible messages format, stream:true for SSE); namespace variants at .../ai-search/namespaces/{ns}/... with ai_search_options.instance_ids. Plus a per-instance MCP endpoint.

**Capabilities:**
- Automated, continuous indexing of a connected data source (no manual embed-on-write cron)
- Markdown conversion of rich files (PDF, .docx, .xlsx, images, HTML/XML, ODF, CSV/Numbers) via Workers AI before chunking
- Chunking + embedding via Workers AI embedding models, vectors stored and searched for you
- Hybrid search: semantic (vector) + optional BM25 keyword matching with configurable fusion
- Optional LLM query rewriting and optional cross-encoder reranking in the query pipeline
- Two query modes: search() returns scored chunks; chatCompletions() returns an OpenAI-compatible generated answer with cited source chunks
- Metadata filtering with up to 5 custom metadata fields
- Multi-tenant retrieval via namespaces — query one or many instances by instance_ids (per-tenant / per-agent file search)
- Built-in MCP endpoint on every instance for AI-agent tool use
- Embeddable UI search components

**Detection signals — the lens fires on these:**
- Vector DB clients: @pinecone-database/pinecone, weaviate-ts-client/weaviate-client, @qdrant/js-client-rest, chromadb, pgvector / `CREATE EXTENSION vector` / vector(1536) columns, milvus
- Embedding calls in app code or a cron: openai.embeddings.create, text-embedding-3-small/-ada-002, @huggingface/inference embeddings, cohere.embed, sentence-transformers / SentenceTransformer
- Env vars: PINECONE_API_KEY, PINECONE_INDEX, WEAVIATE_URL, QDRANT_URL, OPENAI_API_KEY paired with a vector store, DATABASE_URL on a Postgres that also has a pgvector table
- RAG orchestration frameworks: langchain / @langchain/*, llamaindex / llama-index, haystack, semantic-kernel — especially RetrievalQA, VectorStoreIndex, .as_retriever()
- Document parsing/loader deps: unstructured, pypdf / pdf-parse, mammoth (docx), python-docx, openpyxl, a 'chunk' / 'splitter' / RecursiveCharacterTextSplitter utility
- A scheduled job (cron / queue worker / Airflow DAG) named like ingest/index/embed/reindex that re-embeds documents on change
- Hand-written hybrid-search or reranking code: BM25 + cosine fusion, cohere.rerank, cross-encoder/ms-marco rerankers
- Docs/knowledge-base or 'chat with your PDFs/docs' feature backed by an R2/S3 bucket of source files
- An existing Cloudflare footprint (Workers + R2 bucket of documents) where retrieval is being bolted on manually

**Ideas:**
- Point AI Search at an existing R2 bucket of PDFs/docs and replace a homegrown embeddings cron + Pinecone index with a single inst.search() call — drop the vector DB bill entirely.
- Add a 'chat with our docs' / knowledge-base assistant: use the OpenAI-compatible chat/completions endpoint so existing OpenAI SDK code keeps working but answers are grounded in your content with cited chunks.
- Give an AI agent retrieval + memory by attaching the per-instance MCP endpoint, or do per-tenant document search by mapping each customer to a namespace instance and querying by instance_ids.

**Pairs with:** R2 (object store that holds the source documents to index — zero egress), Workers AI (supplies the Markdown conversion, embedding models, and the generation/query-rewrite LLMs), Vectorize (the underlying vector index for legacy instances), AI Gateway (observability/caching/rate-limiting over the model calls), Workers / Agents SDK (consume search via binding; MCP endpoint plugs into agent tool use), Browser Run (used for crawling website data sources)

**Pricing:** Free during open beta within plan limits. New instances (after 2026-04-16): AI Search itself is free; Workers AI and AI Gateway usage billed separately. Legacy instances: you pay only for the underlying components — R2, Vectorize, Workers AI, AI Gateway, Browser Run. Cloudflare says billing details will be announced 30+ days before any charges begin. Free plan caps: 100 instances, 100k files/instance, 20k queries/mo, 500 pages crawled/day. Paid plan: 5,000 instances, up to 1M files/instance (500k for hybrid), unlimited queries. (verify — drifts)

**Limits:**
- Max file size: 4 MB — larger files are skipped and logged as errors
- Free plan: 100 instances/account, 100,000 files/instance, 20,000 queries/month, 500 pages crawled/day, 5 custom metadata fields, 500-char metadata values
- Paid plan: 5,000 instances/account, 1,000,000 files/instance (500,000 if hybrid/keyword search enabled), unlimited queries, unlimited daily crawl
- 3 data source types only: built-in upload storage, Website crawler (domain you own), and a Cloudflare R2 bucket
- 5 custom metadata fields max; metadata value length capped at 500 characters
- Open beta — APIs, pricing, and limits are explicitly subject to change

**Notes:** Honest caveats: (1) This is the rebranded/evolved successor to what Cloudflare previously shipped as AutoRAG — older code, blog posts, and bindings may still say 'AutoRAG'; the current docs use 'AI Search' and the ai_search / ai_search_namespaces binding keys. I did not find the string 'AutoRAG' in the pages fetched this run, so treat the rename as inferred from product shape, not confirmed verbatim. (2) Open beta: free-but-undefined pricing is a real planning risk — the eventual paid model is unannounced, and legacy vs new instances bill differently. (3) Lock-in: ingestion, chunking, embedding-model choice, retrieval, and the MCP endpoint are all Cloudflare-managed, so you trade the flexibility of a custom pipeline (custom chunkers, arbitrary embedding models, your own reranker) for convenience. If you need a specific embedding model, exotic chunking, or a vector store you can query with raw SQL/filters, raw Vectorize + Workers AI (or your own stack) is the better fit. (4) The 4 MB per-file cap means very large PDFs must be pre-split. (5) Source content realistically needs to live in R2 or a crawlable site you own; it is not a general connector hub (no native Notion/Google Drive/Confluence sources listed).

**Docs:** https://developers.cloudflare.com/ai-search/llms.txt, https://developers.cloudflare.com/ai-search/index.md, https://developers.cloudflare.com/ai-search/concepts/how-ai-search-works/index.md, https://developers.cloudflare.com/ai-search/platform/limits-pricing/index.md, https://developers.cloudflare.com/ai-search/configuration/data-source/index.md, https://developers.cloudflare.com/ai-search/api/search/workers-binding/index.md, https://developers.cloudflare.com/ai-search/api/search/rest-api/index.md

---

## Cloudflare Agents (Agents SDK)
`cloudflare-agents` · AI / Stateful agents runtime · confidence: `high` · lock-in: `deep`

**Is:** A TypeScript SDK for building stateful AI agents that run on Cloudflare's edge, where each agent instance is a Durable Object with its own embedded SQLite database, persistent state, WebSocket sync, and built-in scheduling.

**Replaces:** A self-hosted stateful-agent backend: a long-running Node/Python process (LangGraph/CrewAI on a VM or container) + Redis or Postgres for per-conversation state/memory + a Pusher/Ably-style socket layer for streaming + a cron worker for scheduled agent tasks. Agents collapses all of that into one per-instance object.

**Use it via:** npm install agents. Extend class Agent<Env, State> (or AIChatAgent for chat). wrangler.jsonc binds it as a Durable Object: durable_objects.bindings = [{ name: 'AGENT', class_name: 'Agent' }] plus a migrations entry. Route via routeAgentRequest(request, env) or getAgentByName(env.AGENT, name); default URL shape /agents/:agent-name/:instance-name. Core methods: onStart, onRequest, onConnect/onMessage/onClose, onEmail, this.state/this.setState, this.sql, this.schedule/scheduleEvery/cancelSchedule, onStateChanged, validateStateChange.

**Capabilities:**
- Per-agent-instance persistent state via this.setState()/this.state, auto-saved to SQLite and surviving restarts and hibernation
- Embedded zero-latency SQLite per agent via this.sql`...` tagged-template queries (arbitrary schemas, optional TS typing this.sql<User>), up to 1 GB state per unique agent
- Real-time state sync: setState() broadcasts to all connected WebSocket clients automatically; onStateChanged(state, source) distinguishes server vs client origin; validateStateChange() can veto updates
- Built-in WebSocket server lifecycle (onConnect, onMessage, onClose) plus HTTP (onRequest) and email (onEmail) entrypoints on the same class
- Built-in scheduling: this.schedule(when, 'methodName', payload) accepts a delay in seconds, a Date, or a cron string; scheduleEvery() for intervals; tasks persist in SQLite via Durable Object alarms and survive hibernation; cancelSchedule()/getScheduleById()/listSchedules()
- Hibernation economics: agents sleep when idle and wake on demand, so you pay only for active compute
- Tool/LLM integration: works with OpenAI, Anthropic and other providers; MCP (Model Context Protocol) tool access; browser and AI-search tools; AIChatAgent helper for chat UIs
- @callable() decorator exposes agent methods directly to clients; getAgentByName() and routeAgentRequest() for addressing/routing specific instances

**Detection signals — the lens fires on these:**
- package.json deps: langchain / langgraph / @langchain/langgraph, crewai, autogen, llamaindex agent runtimes — especially paired with a separate state store
- An OpenAI/Anthropic client (openai, @anthropic-ai/sdk) plus a hand-rolled per-conversation memory layer (REDIS_URL, a `conversations`/`messages` Postgres table, or a sessions table keyed by conversation id)
- A long-running agent loop kept alive in a container/VM (Dockerfile, pm2, a `while True` agent loop, a worker dyno) because the framework can't hibernate
- Separate realtime layer for streaming agent output: socket.io, Pusher, Ably, ws server, SSE endpoints hand-wired alongside the agent
- A cron/scheduler (node-cron, BullMQ, Celery beat, a CRON_TZ env, a `scheduled_jobs` table) used to fire per-user or per-agent follow-up tasks
- Manual DO-style addressing already in the codebase (idFromName / get(id) on a Durable Object) reimplementing what getAgentByName provides
- wrangler.jsonc/wrangler.toml with durable_objects bindings + an LLM SDK, indicating a Worker that is most of the way to an Agent already

**Ideas:**
- Turn a stateful chatbot/copilot into a per-user Agent instance so each conversation keeps its own SQLite-backed memory and streams over WebSockets without a Redis box or a Pusher subscription
- Move 'follow up with this user in 3 days' / recurring-digest logic off node-cron + a jobs table onto this.schedule()/scheduleEvery(), which persists across hibernation via DO alarms
- Build a human-in-the-loop agent (long-running task that pauses for approval) using persistent state + scheduled wake-ups instead of an always-on worker process
- Expose agent actions to a front-end with @callable() methods and live this.state sync instead of building a REST+websocket protocol by hand

**Pairs with:** Workers AI / Workers AI gateway or OpenAI/Anthropic for the model calls, Durable Objects (Agents is built directly on them), Vectorize (RAG / long-term semantic memory beyond per-agent SQLite), Workflows (deterministic multi-step orchestration alongside adaptive agents), Browser Run and AI Search as agent tools, MCP servers (build with McpAgent) for tool access, Email Routing / Email Sending via onEmail for email-driven agents

**Pricing:** No standalone Agents price; an Agent instance is a Durable Object, so you pay the Workers Paid plan ($5/mo base) plus Durable Objects usage — billed on requests + active compute duration — while idle/hibernating agents incur no compute charge. SQLite-backed state counts toward Durable Objects storage. Free Workers plan can run small experiments but production needs the paid plan. (verify — drifts)

**Limits:**
- Max state stored per unique Agent: 1 GB
- Max compute time per Agent: 30 seconds, refreshed per HTTP request / incoming WebSocket message
- Wall-clock duration per step: unlimited (e.g. waiting on an LLM or DB call does not count against the 30s CPU budget)
- Max concurrent (running) Agents per account: tens of millions+
- Max Agent definitions (classes) per account: ~250,000+
- Deployed script size up to 10 MB on the Workers Paid plan
- State broadcast to all clients on every setState() change — docs advise keeping live state small and pushing large collections to this.sql instead

**Notes:** Honest caveats: (1) Hard lock-in — an Agent IS a Durable Object subclass with Cloudflare-specific bindings, wrangler config, and lifecycle hooks; porting off-platform means rebuilding the state/sync/scheduling layer. (2) Not a fit for stateless one-shot LLM calls (a plain Worker is cheaper/simpler) or for heavy CPU-bound work — the 30s CPU budget per request rules out long synchronous compute (though waiting on I/O/LLMs is unlimited wall-clock). (3) State is partitioned per instance with no built-in cross-agent query/transaction; aggregating across many agents needs an external store (D1/Vectorize). (4) Pricing for Agents specifically is NOT published as its own SKU — the figures here are inferred from the Workers Paid plan + Durable Objects billing model the SDK rides on; the docs search surfaced only unrelated 'Dynamic Workers' pricing, so treat the dollar figures as unverified. (5) 'Keep state small' is a real constraint — the auto-broadcast-on-change design punishes large reactive state objects.

**Docs:** https://developers.cloudflare.com/agents/llms.txt, https://developers.cloudflare.com/agents/concepts/what-are-agents/index.md, https://developers.cloudflare.com/agents/runtime/agents-api/index.md, https://developers.cloudflare.com/agents/runtime/lifecycle/state/index.md, https://developers.cloudflare.com/agents/platform/limits/index.md, https://developers.cloudflare.com/agents/runtime/execution/schedule-tasks/index.md

---

## Cloudflare Vectorize
`vectorize` · AI / Vector Database · confidence: `high` · lock-in: `deep`

**Is:** A globally distributed vector database for storing and querying embeddings (text/image/audio) to power semantic search, RAG, recommendations, and classification, native to Cloudflare Workers.

**Replaces:** A self-hosted pgvector/Postgres box (or a paid Pinecone/Weaviate/Qdrant subscription) plus a separate embeddings cron/pipeline — Vectorize is the managed vector store, and Workers AI supplies the embeddings in the same runtime.

**Use it via:** Worker binding declared in wrangler as a `vectorize` array: `{ "binding": "VECTORIZE", "index_name": "my-index" }` (wrangler.toml: `[[vectorize]]`). Used as `env.VECTORIZE.query(vec, { topK, returnMetadata: "all" })`, `.upsert([...])`, `.insert([...])`, `.getByIds([...])`, `.deleteByIds([...])`, `.describe()`. CLI: `npx wrangler vectorize create <name> --dimensions=768 --metric=cosine`. Also a REST API under `/accounts/{id}/vectorize/v2/indexes` (HTTP API allows larger 5,000-vector upsert batches).

**Capabilities:**
- Store and query dense vector embeddings with topK nearest-neighbor search
- Three distance metrics: cosine, euclidean (L2), dot product (set at index creation)
- insert / upsert / query / getByIds / deleteByIds / describe via Worker binding
- Metadata filtering and up to 10 metadata indexes per index; namespaces (segment a single index into up to 50k partitions on Workers Paid)
- returnValues + returnMetadata controls on query results
- Pairs directly with Workers AI embedding models (e.g. @cf/baai/bge-base-en-v1.5 -> 768 dims) or external embeddings (OpenAI, etc.)
- No egress/data-transfer fees; no charge for CPU, memory, index hours, or empty indexes

**Detection signals — the lens fires on these:**
- npm deps: `@pinecone-database/pinecone`, `weaviate-ts-client`/`weaviate-client`, `@qdrant/js-client-rest`, `chromadb`, `@zilliz/milvus2-sdk-node`, `pgvector`
- Postgres with the `vector` extension / `CREATE EXTENSION vector` / columns typed `vector(1536)` and `<=>` / `<->` / `<#>` operators in SQL
- env vars: `PINECONE_API_KEY`, `PINECONE_INDEX`, `WEAVIATE_URL`, `QDRANT_URL`, `QDRANT_API_KEY`
- An embeddings cron/worker that calls `openai.embeddings.create` or a sentence-transformers job and writes vectors into a separate store
- RAG plumbing: LangChain/LlamaIndex vector-store adapters (`PineconeStore`, `Chroma`, `PGVectorStore`), `cosine_similarity` helpers, hand-rolled kNN over an array of embeddings in memory or KV/D1
- Already on Cloudflare (wrangler.jsonc, Workers AI `env.AI.run`, R2/D1/KV bindings) but reaching off-platform for vector search

**Ideas:**
- RAG over the team's docs/support KB: chunk -> embed with Workers AI bge-base-en-v1.5 (768 dims) -> upsert to Vectorize -> query topK and stuff context into an LLM, all inside one Worker
- Semantic / 'related items' search and dedup for a product catalog or content site, using metadata filtering + namespaces to scope per-tenant
- Recommendation or anomaly/duplicate detection by nearest-neighbor lookup against stored embeddings instead of standing up Pinecone or a pgvector box

**Pairs with:** Workers AI (generate embeddings, e.g. @cf/baai/bge-base-en-v1.5; LLM for the generation step in RAG), Cloudflare Workers (the runtime the binding lives in), R2 (source images/files), D1 (relational metadata / user profiles), KV (cached documents), AI Gateway / external embedding providers (OpenAI) when not using Workers AI

**Pricing:** Free tier (Workers Free): 30M queried + 5M stored vector dimensions / month. Paid (Workers Paid): first 50M queried dims/mo included then $0.01 / 1M queried dims; first 10M stored dims included then $0.05 / 100M stored dims. Billed only on queried + stored dimensions (vectors x dimension count); no charge for CPU/memory/index-hours/empty indexes; no egress fees. (verify — drifts)

**Limits:**
- Max dimensions per vector: 1536 (32-bit precision)
- Max vectors per index: 10,000,000
- Indexes per account: 100 (Free) / 50,000 (Workers Paid)
- Metadata per vector: 10 KiB; max 10 metadata indexes per index; indexed data per metadata index per vector: 64 bytes
- Namespaces per index: 1,000 (Free) / 50,000 (Workers Paid); namespace name <=64 bytes
- topK capped at 50 when returning values/metadata, else 100
- Upsert batch: 1,000 vectors (Workers binding) / 5,000 (HTTP API); max upload 100 MB; list-vectors page max 1,000
- Vector ID <=64 bytes; index name <=64 bytes

**Notes:** Hard ceiling of 1536 dimensions and 32-bit float precision — embedding models with larger output (e.g. OpenAI text-embedding-3-large at 3072) must be dimension-reduced or won't fit; no quantization/binary-vector or hybrid (sparse+dense / BM25) search surfaced in these docs, so full-text-hybrid RAG still needs a complementary store. 10M vectors/index cap means very large corpora need sharding across indexes. Billing on *queried* dimensions = (queried + stored vectors) x dims, so high-QPS workloads over large indexes can cost more than the storage line suggests — model it. Distance metric and dimensions are fixed at index creation (immutable), so changing embedding models means recreating the index. Lock-in: Worker-binding API and wrangler config are Cloudflare-specific; portability is mainly that the vectors themselves are standard floats. The v2 REST API path (`/vectorize/v2/indexes`) and exact per-million prices should be re-verified against the live pricing/changelog pages before quoting to a customer.

**Docs:** https://developers.cloudflare.com/vectorize/llms.txt, https://developers.cloudflare.com/vectorize/index.md, https://developers.cloudflare.com/vectorize/platform/pricing/index.md, https://developers.cloudflare.com/vectorize/platform/limits/index.md, https://developers.cloudflare.com/vectorize/reference/client-api/index.md, https://developers.cloudflare.com/vectorize/reference/what-is-a-vector-database/index.md, https://developers.cloudflare.com/vectorize/get-started/embeddings/index.md

---

## Workers AI
`workers-ai` · AI / Inference · confidence: `high` · lock-in: `sticky`

**Is:** Serverless GPU inference that runs 50+ open-source models (LLMs, embeddings, image generation, speech-to-text, classification) on Cloudflare's edge network, callable from a Worker binding or REST API.

**Replaces:** A GPU box / managed inference vendor (OpenAI/Anthropic API spend, Replicate, Hugging Face Inference Endpoints, AWS Bedrock/SageMaker, a self-hosted vLLM/Ollama server on a rented A100) — plus the embeddings cron and Whisper transcription job a dev would otherwise wire up themselves.

**Use it via:** Worker binding: add `{ "ai": { "binding": "AI" } }` to wrangler.jsonc (or `[ai]\nbinding = "AI"` in wrangler.toml), then `await env.AI.run("@cf/meta/llama-3.1-8b-instruct", { prompt })`. REST: `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}` with `Authorization: Bearer <token>`. OpenAI-compatible: `POST .../v1/chat/completions` and `.../v1/embeddings`, usable directly via the `openai` npm SDK by overriding baseURL. Model IDs look like `@cf/<vendor>/<model>` (e.g. @cf/meta/llama-3.3-70b-instruct-fp8-fast, @cf/baai/bge-large-en-v1.5, @cf/black-forest-labs/flux-1-schnell, @cf/openai/whisper).

**Capabilities:**
- Text generation / chat LLMs (Llama 3.1/3.3, Mistral, Qwen, Gemma, Phi, etc.) via env.AI.run() or REST
- Text embeddings (BGE family) for RAG — pairs natively with Vectorize
- Image generation (Flux Schnell, Stable Diffusion, Leonardo Phoenix)
- Automatic speech recognition / transcription (Whisper, Deepgram Nova-3)
- Image classification, object detection, image-to-text, summarization, translation, text classification
- JSON mode / structured outputs via response_format (incl. json_schema) for reliable structured extraction
- Function calling / tool use on supported models
- OpenAI-compatible endpoints (/v1/chat/completions and /v1/embeddings) — drop-in for the OpenAI SDK
- LoRA adapters to fine-tune supported base models (pass `lora` param)
- Streaming responses; integrates with AI Gateway for caching, logging, rate limiting and evals

**Detection signals — the lens fires on these:**
- npm `openai` / `@anthropic-ai/sdk` / `@google/generative-ai` / `cohere-ai` used purely for simple generate/embed/classify calls
- Env vars OPENAI_API_KEY, ANTHROPIC_API_KEY, REPLICATE_API_TOKEN, HUGGINGFACEHUB_API_TOKEN, TOGETHER_API_KEY
- Python `transformers`, `torch`, `sentence-transformers`, `vllm`, `llama-cpp-python`, `faster-whisper` in requirements.txt / a Dockerfile pulling a CUDA base image
- A separate GPU service (Modal, Runpod, Replicate, SageMaker endpoint, an Ollama container) fronted by the app just to run inference
- A cron/queue that batch-computes embeddings and writes them to pgvector/Pinecone (embeddings step can move to @cf/baai/bge-* + Vectorize)
- Self-hosted Whisper / ffmpeg transcription pipeline, or paying AssemblyAI/Deepgram for speech-to-text
- Image-generation calls to Replicate/Stability/DALL-E, or a Stable Diffusion worker on rented GPUs
- Hand-rolled JSON-extraction prompt-and-reparse logic (could use JSON mode / response_format)
- Already on Workers/Pages with `nodejs_compat` doing fetch() to an external LLM API — a candidate to collapse into the AI binding (no egress, no key management)

**Ideas:**
- Build edge RAG: embed docs with @cf/baai/bge-large-en-v1.5, store vectors in Vectorize, and answer with a Llama model — all inside one Worker, zero external AI vendor.
- Replace a paid transcription vendor by piping uploaded audio (R2) through @cf/openai/whisper for cheap per-minute speech-to-text.
- Swap brittle 'return JSON' prompting for JSON mode (response_format + json_schema) to get schema-validated structured extraction from user text.
- Use AI Gateway in front of Workers AI to add response caching, request logging, and rate limiting without app code changes.

**Pairs with:** Vectorize (vector DB for embeddings / RAG), AI Gateway (caching, logging, rate limiting, evals, multi-provider routing), AI Search / AutoRAG (managed RAG pipeline), R2 (store source audio/images/docs to feed models), Workers / Pages (host the inference logic), Agents SDK (agentic apps that call models)

**Pricing:** Free allocation of 10,000 Neurons/day on both Free and Paid Workers plans; beyond that $0.011 per 1,000 Neurons. Neurons abstract GPU work and map to model usage, e.g. Llama 3.1 70B ~$0.293/M input + $2.253/M output tokens, Mistral 7B ~$0.110/$0.190 per M tokens, Whisper ~$0.0005/audio minute, Flux 1 Schnell ~$0.0000528 per 512x512 tile. (verify — drifts)

**Limits:**
- Per-task rate limits (req/min), e.g. text generation default 300 rpm (model-specific: Mistral 7B 400, Qwen 1.5 0.5B 1500, Qwen 1.5 14B 150), text embeddings 3000 rpm (BGE Large 1500), text-to-image 720 rpm, ASR 720 rpm, image classification / object detection 3000 rpm, summarization 1500 rpm, translation 720 rpm
- Model menu is the catalog of open-source models Cloudflare hosts — you cannot bring an arbitrary proprietary model (only LoRA adapters on supported bases); frontier closed models (GPT-4o, Claude) are not run here, you'd route those via AI Gateway
- Context windows and exact capabilities vary per model — check the individual model page
- Neuron-to-cost mapping is an abstraction; predicting spend requires the per-model pricing table

**Notes:** Best fit when the workload is open-source-model-shaped (chat with Llama/Mistral/Qwen, BGE embeddings, Whisper ASR, Flux/SD image gen, classification) and you want it co-located with Worker logic — no API keys, no egress, scale-to-zero. NOT the right tool if you specifically need frontier closed models (GPT-4o, Claude, Gemini) — for those use AI Gateway as a proxy instead; Workers AI only runs the models in its own catalog. Quality of the open models trails the top proprietary ones, so eval before swapping a critical path. Some models/features are beta and the model list, Neuron pricing, and rate limits change frequently — treat all numbers as point-in-time. Lock-in is modest: the OpenAI-compatible endpoints and standard model weights make it portable, but the AI binding and Neuron billing are Cloudflare-specific.

**Docs:** https://developers.cloudflare.com/workers-ai/llms.txt, https://developers.cloudflare.com/workers-ai/index.md, https://developers.cloudflare.com/workers-ai/platform/pricing/index.md, https://developers.cloudflare.com/workers-ai/platform/limits/index.md, https://developers.cloudflare.com/workers-ai/get-started/workers-wrangler/index.md, https://developers.cloudflare.com/workers-ai/features/json-mode/, https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/

---
