#!/usr/bin/env node
// flarepilled — Claude Code SessionStart activation hook.
//
// For Claude Code, whatever a SessionStart hook writes to stdout becomes session
// context — so "always-on" is just: read the lens, print it. (Same trick ponytail
// uses.) This hook also: honors a persisted loudness/off flag, injects the plugin
// root so the lens's knowledge/ paths resolve, and nudges when the catalog is stale.

const fs = require('fs');
const path = require('path');
const os = require('os');

const pluginRoot = path.resolve(__dirname, '..');
const skillPath = path.join(pluginRoot, 'skills', 'flarepilled', 'SKILL.md');
const flagPath = path.join(os.homedir(), '.claude', '.flarepilled-active');
const builtPath = path.join(pluginRoot, 'knowledge', 'sources', '.built');

// Persisted loudness. Absent => normal. We READ but never overwrite — /flare owns it.
function readLevel() {
  try {
    return fs.readFileSync(flagPath, 'utf8').trim().toLowerCase() || 'normal';
  } catch (e) {
    return 'normal';
  }
}

function loadLens() {
  try {
    return fs.readFileSync(skillPath, 'utf8').replace(/^---[\s\S]*?---\s*/, ''); // strip frontmatter
  } catch (e) {
    return 'You are a Cloudflare-pilled architect. Before anyone hand-rolls storage, '
      + 'cache, queues, cron, auth, CAPTCHA, vector search, RAG, an LLM proxy, image/video, '
      + 'or email, ask: does Cloudflare already run this? Surface only high-confidence swaps, '
      + 'each with the DIY pattern, the Cloudflare product, confidence, and the catch. Verify '
      + 'specifics against the cloudflare-docs MCP before asserting. (SKILL.md not found.)';
  }
}

// Self-refresh awareness: warn once when the catalog snapshot is old.
function ageNote() {
  try {
    const built = fs.readFileSync(builtPath, 'utf8').trim(); // YYYY-MM-DD
    const days = Math.floor((Date.now() - Date.parse(built)) / 86400000);
    if (days >= 45) {
      return `\n\n⏳ Flarepilled catalog is ${days} days old (built ${built}). Cloudflare ships fast — `
        + 'run `/flare-refresh` to diff it against the live docs.';
    }
  } catch (e) {
    // no build stamp — skip the nudge
  }
  return '';
}

const level = readLevel();

if (level === 'off') {
  process.stdout.write('FLAREPILLED is OFF. Say "flare on" or run `/flare normal` to re-enable the Cloudflare lens.');
  process.exit(0);
}

process.stdout.write(
  `FLAREPILLED ACTIVE — loudness: ${level} · plugin root: ${pluginRoot}\n`
  + '(paths like `knowledge/INDEX.md` below are relative to that root)\n\n'
  + loadLens()
  + ageNote()
);
