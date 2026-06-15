# LLM calls (caching, cost visibility, fallback)

**Task:** "We call OpenAI straight from our app. No caching (we pay for identical
prompts), no cost visibility, and when it rate-limits or 500s, we just fail."

## The old way (raw provider calls)

```ts
const r = await fetch('https://api.openai.com/v1/chat/completions', {
  method: 'POST',
  headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
  body: JSON.stringify({ model: 'gpt-4', messages }),
})
// no cache → pay again for the same prompt; no logs → no cost/latency visibility;
// no retry/fallback → a provider blip is a user-facing error.
```

## With AI Gateway (one URL change in front of any provider)

```ts
// Route the SAME request through your gateway — caching, rate-limiting, retries,
// fallback, and per-request logs + cost analytics come for free.
const base = `https://gateway.ai.cloudflare.com/v1/${ACCOUNT_ID}/${GATEWAY}/openai`
const r = await fetch(`${base}/chat/completions`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}` },
  body: JSON.stringify({ model: 'gpt-4', messages }),
})
```
```bash
# create the gateway once (dashboard or API), then just swap the base URL
```

**Why it's the swap:** caching identical prompts, automatic retries/fallback to a second
provider, rate-limiting, and **real cost + latency analytics per app** — without writing a
proxy. Pair with **Workers AI** to run the model on Cloudflare too (then there's no
external key or bill at all).

### The honest catch
- **Lock-in: portable** — it's a URL prefix; remove it and you're back to direct calls.
- It's a *gateway* — with OpenAI it still uses **your OpenAI key and bill**; only Workers AI
  moves the inference (and cost) onto Cloudflare.
- **Verify** the current provider list, caching controls, and any request cap against
  `https://developers.cloudflare.com/ai-gateway/llms.txt`.
