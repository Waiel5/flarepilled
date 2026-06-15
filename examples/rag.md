# RAG over your own docs

**Task:** "A chatbot that answers from our docs. We built the RAG ourselves: chunk the
files, embed with OpenAI, store vectors in pgvector, retrieve top-k, stuff the context."

## The old way (hand-rolled RAG pipeline)

```ts
// ingest: a cron job that re-chunks + re-embeds whenever docs change
for (const doc of docs) {
  const chunks = chunk(doc, 512)
  const vectors = await embed(chunks)                 // OpenAI embeddings $$
  await pg.query('INSERT INTO embeddings ...', vectors) // a pgvector box to run
}
// query: embed the question, similarity search, assemble the prompt, call the LLM
const qv = await embed([question])
const hits = await pg.query('SELECT ... ORDER BY embedding <-> $1 LIMIT 8', [qv])
const answer = await llm(buildPrompt(hits, question))
// + keeping the index fresh, + tuning chunking, + a vector DB to operate.
```

## With AI Search (managed RAG)

```jsonc
// wrangler.jsonc — the AI binding
{ "ai": { "binding": "AI" } }
```
```ts
// Point an AI Search instance at an R2 bucket of docs (dashboard/API). It chunks,
// embeds, indexes, and keeps itself fresh. Then one call does retrieve + generate:
const res = await env.AI.autorag('my-docs').aiSearch({ query: question })
return Response.json({ answer: res.response, sources: res.data })   // citations included
// or .search(...) for retrieval-only if you want to run your own generation.
```

**Why it's the swap:** the chunker, the embeddings job, the vector store, the retrieval
loop, and the freshness cron all collapse into "point it at R2, then query." Built on
**Vectorize + Workers AI** under the hood.

### The honest catch
- **Lock-in: deep** — the index + pipeline are Cloudflare-managed; you trade tuning control for zero ops.
- Less control over chunking/reranking than a bespoke pipeline — fine for most doc-QA, limiting for exotic retrieval.
- Naming/API drift: this is the product formerly explored as **AutoRAG** — **verify** the current
  binding method + name against `https://developers.cloudflare.com/ai-search/llms.txt`.
