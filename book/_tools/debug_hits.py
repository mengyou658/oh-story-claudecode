# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

p = Path(r"e:\oh-story-claudecode\book\_analysis\ai_trace_scores.json")
data = json.loads(p.read_text(encoding="utf-8"))
for r in data["books"][:12]:
    print(f"=== {r['file']} score={r['ai_score']} ===")
    print("ai_hits:", r.get("ai_hits"))
    print("human_hits:", r.get("human_hits"))
    print("metrics:", r.get("metrics"))
    print()

BOOK = Path(r"e:\oh-story-claudecode\book")
files = sorted(x for x in BOOK.glob("*.txt") if not x.name.startswith("_"))
rows = []
for f in files:
    t = f.read_text(encoding="utf-8", errors="ignore")
    # first ~45k chars ~ early chapters
    s = t[:45000]
    rows.append(
        {
            "file": f.name,
            "fangfu": s.count("仿佛") + s.count("似乎"),
            "jingran": s.count("竟然") + s.count("居然"),
            "shenxi": s.count("深吸一口气"),
            "xiayimiao": s.count("下一秒") + s.count("话音刚落"),
            "buzai_ershi": len(re.findall(r"不是[^，。]{1,10}，而是", s)),
            "tongkong": s.count("瞳孔"),
            "weimiaio": s.count("嘴角"),
            "wocao": len(re.findall(r"卧槽|我靠|我操|离谱|绷不住", s)),
            "chars": len(s),
        }
    )

rows.sort(key=lambda x: -(x["fangfu"] + x["jingran"] * 0.5 + x["shenxi"] * 2 + x["xiayimiao"] * 2 + x["buzai_ershi"] * 3 + x["tongkong"]))
print("RAW TOP:")
for r in rows[:15]:
    print(r)

# extract ch1 samples for qualitative review (first 1800 chars after first chapter header)
out = Path(r"e:\oh-story-claudecode\book\_analysis\ch1_samples.md")
lines = ["# 各书第1章抽样（约1200字）\n"]
for f in files:
    t = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"(?m)^第\s*1\s*章[^\n]*\n", t)
    if m:
        body = t[m.end() : m.end() + 1200]
    else:
        body = t[:1200]
    lines.append(f"\n## {f.name}\n\n```\n{body.strip()}\n```\n")
out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out, "bytes", out.stat().st_size)
