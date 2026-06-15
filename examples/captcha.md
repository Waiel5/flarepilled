# Bot / abuse protection on a form

**Task:** "Stop bots hammering our signup form. We bolted on reCAPTCHA but it nags real
users and ships Google tracking."

## The old way (reCAPTCHA v2/v3)

```html
<script src="https://www.google.com/recaptcha/api.js"></script>
<div class="g-recaptcha" data-sitekey="..."></div>
```
```ts
// server: verify against Google, inherit its tracking + the score-tuning guesswork
const r = await fetch('https://www.google.com/recaptcha/api/siteverify', {
  method: 'POST', body: new URLSearchParams({ secret, response: token }),
})
```

## With Turnstile (no puzzles, no Google tracking)

```html
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>
<div class="cf-turnstile" data-sitekey="0x..."></div>
```
```ts
// server: same shape, Cloudflare endpoint, privacy-preserving challenge
const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
  method: 'POST',
  body: new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token }),
}).then(r => r.json())
if (!r.success) return new Response('failed challenge', { status: 403 })
```
```bash
npx wrangler secret put TURNSTILE_SECRET    # keep the secret out of code
```

**Why it's the swap:** a near-drop-in `siteverify` replacement that mostly runs
invisible (no image puzzles), without sending your users through Google's ad graph.

### The honest catch
- **Lock-in: portable** — it's a sitekey/secret + one endpoint; swapping back out is trivial.
- It's a human-verification signal, **not** a WAF or bot-management product — pair with
  **WAF** / **Bots** for traffic-level mitigation.
- **Verify** current widget modes and any quota against `https://developers.cloudflare.com/turnstile/llms.txt`.
