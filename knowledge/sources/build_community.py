#!/usr/bin/env python3
"""Render community-sourced Cloudflare patterns into knowledge/community-patterns.md.

Input : knowledge/sources/community.json  (array of pattern objects from the sweep)
These are ANECDOTES, flagged by confidence: community < medium < high. The lens must
treat them accordingly. # flarepilled: render-only, the honesty is in the confidence tag
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "knowledge" / "sources" / "community.json"
OUT = ROOT / "knowledge" / "community-patterns.md"

# display order: inspiration first, warnings last
CATS = [
    ("unconventional-architecture", "Unconventional architectures"),
    ("clever-combo", "Clever product combos"),
    ("cost-migration", "Cost & migration stories"),
    ("tip", "Tips"),
    ("gotcha", "Gotchas (verify before you rely on these)"),
    ("anti-pattern", "Anti-patterns (don't do this)"),
]
REC = {"do": "✅ do", "avoid": "⚠️ avoid", "idea": "💡 idea"}
CONF_RANK = {"high": 0, "medium": 1, "community": 2}


def assert_unique_titles(patterns):
    seen = {}
    dupes = []
    for idx, pattern in enumerate(patterns, start=1):
        title = (pattern.get("title") or "").strip().lower()
        if not title:
            continue
        if title in seen:
            dupes.append((pattern.get("title"), seen[title], idx))
        else:
            seen[title] = idx
    if dupes:
        lines = [
            f"- {title}: entries {first} and {second}"
            for title, first, second in dupes
        ]
        raise SystemExit("Duplicate community pattern titles found; fix sources/community.json:\n" + "\n".join(lines))


def main():
    patterns = json.loads(SRC.read_text())
    assert_unique_titles(patterns)
    items = patterns

    by_cat = {}
    for p in items:
        by_cat.setdefault(p.get("category", "tip"), []).append(p)

    hi = sum(1 for p in items if p.get("confidence") == "high")
    out = [
        "# Community patterns & gotchas",
        "",
        f"_{len(items)} patterns swept from Reddit / Hacker News / dev blogs ({hi} corroborated "
        "as `high`). **These are anecdotes, not documentation** — confidence is tagged on each: "
        "`high` = also in official docs or widely corroborated · `medium` = multiple sources · "
        "`community` = a single report. The lens may surface `do`/`idea` items as **speculative** "
        "and must verify any `gotcha` against live docs before stating it as fact._",
        "",
    ]
    for key, title in CATS:
        rows = by_cat.get(key)
        if not rows:
            continue
        rows.sort(key=lambda p: CONF_RANK.get(p.get("confidence"), 3))
        out.append(f"## {title} ({len(rows)})")
        out.append("")
        for p in rows:
            rec = REC.get(p.get("recommendation"), "")
            prods = ", ".join(p.get("products") or [])
            out.append(f"### {rec} · {p.get('title','')}")
            out.append(f"`{p.get('confidence','?')}`{' · ' + prods if prods else ''}")
            out.append("")
            if p.get("takeaway"):
                out.append(f"**Takeaway:** {p['takeaway']}")
                out.append("")
            if p.get("summary"):
                out.append(p["summary"])
                out.append("")
            srcs = p.get("sources") or []
            if srcs:
                out.append("Sources: " + " · ".join(srcs))
                out.append("")
        out.append("")
    OUT.write_text("\n".join(out))
    print(f"{len(items)} patterns ({hi} high) → community-patterns.md")
    for key, title in CATS:
        if by_cat.get(key):
            print(f"  {len(by_cat[key]):2d}  {title}")


if __name__ == "__main__":
    main()
