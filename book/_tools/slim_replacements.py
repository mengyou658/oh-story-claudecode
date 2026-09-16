# -*- coding: utf-8 -*-
"""Build a clean, short replacement dictionary for later rewriting."""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(r"e:\oh-story-claudecode\book\_analysis")
bank = json.loads((OUT / "ai_human_phrase_bank.json").read_text(encoding="utf-8"))

# Prefer curated + short harvested
clean_pairs = []
for p in bank["replacement_pairs"]:
    a, h = p["ai_expr"], p["human_expr"]
    if p["source"] == "curated":
        clean_pairs.append(p)
        continue
    # harvested: keep only compact expressions
    if 4 <= len(a) <= 24 and 2 <= len(h) <= 18:
        # drop if looks like broken fragment
        if any(x in a for x in ["】", "【", "http"]):
            continue
        clean_pairs.append(p)

# compact map: ai_expr -> list of human alternatives
mapping = {}
for p in clean_pairs:
    mapping.setdefault(p["ai_expr"], {
        "meaning": p["meaning"],
        "replace_with": [],
    })
    if p["human_expr"] not in mapping[p["ai_expr"]]["replace_with"]:
        mapping[p["ai_expr"]]["replace_with"].append(p["human_expr"])

slim = {
    "purpose": "AI/模板句 → 人味句 替换词典（短表达优先）",
    "usage": "写作时按 meaning 选一组；替换后按语境改人称/时态，禁止无脑全局替换",
    "pair_count": len(clean_pairs),
    "unique_ai_expr": len(mapping),
    "pairs": clean_pairs,
    "map": mapping,
    "buckets_summary": [
        {
            "id": b["id"],
            "meaning": b["meaning"],
            "ai_top": b["ai_examples"][:8],
            "human_top": b["human_examples"][:8],
        }
        for b in bank["buckets"]
    ],
}

out = OUT / "ai_to_human_replacements.json"
out.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {out} pairs={len(clean_pairs)} keys={len(mapping)}")
