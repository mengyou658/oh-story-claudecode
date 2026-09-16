# -*- coding: utf-8 -*-
"""Extract bookIds from full-genre ranking MDs and compare with local book/."""
from __future__ import annotations

import json
import re
from pathlib import Path

RANK_DIR = Path(r"e:\oh-story-claudecode\扫榜结果\跨平台_全榜_20260916")
BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
OUT = BOOK_DIR / "_analysis"
OUT.mkdir(exist_ok=True)

files = [
    RANK_DIR / "番茄男频阅读榜_全题材_20260916.md",
    RANK_DIR / "番茄女频阅读榜_全题材_20260916.md",
]

# already downloaded bookIds (status folders)
have_ids = {p.name for p in BOOK_DIR.iterdir() if p.is_dir() and p.name.isdigit()}

entries = []
seen = set()
for f in files:
    text = f.read_text(encoding="utf-8")
    # match heading + bookId nearby
    for m in re.finditer(
        r"###\s*#(\d+)\s+([^\r\n]+)\r?\n([\s\S]*?)\*\*bookId[：:]\*\*\s*(\d+)",
        text,
    ):
        rank, title, block, bid = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
        if bid in seen:
            continue
        seen.add(bid)
        # try author line
        author = ""
        am = re.search(r"^\*([^*·]+)·", block, re.M)
        if am:
            author = am.group(1).strip()
        entries.append(
            {
                "book_id": bid,
                "title": title,
                "author": author,
                "rank": int(rank),
                "source": f.name,
                "already_downloaded": bid in have_ids,
            }
        )
    # fallback bare bookIds
    for m in re.finditer(r"\*\*bookId[：:]\*\*\s*(\d+)", text):
        bid = m.group(1)
        if bid not in seen:
            seen.add(bid)
            entries.append(
                {
                    "book_id": bid,
                    "title": "(标题待解析)",
                    "author": "",
                    "rank": 0,
                    "source": f.name,
                    "already_downloaded": bid in have_ids,
                }
            )

need = [e for e in entries if not e["already_downloaded"]]
queue = {
    "total_unique": len(entries),
    "already": len(entries) - len(need),
    "need_download": len(need),
    "entries": entries,
    "need_ids": [e["book_id"] for e in need],
}
out = BOOK_DIR / "_download_queue_全题材阅读榜_20260916.json"
out.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: queue[k] for k in ("total_unique", "already", "need_download")}, ensure_ascii=False))
print("need sample:", need[:5])
