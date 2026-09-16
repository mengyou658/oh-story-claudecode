# -*- coding: utf-8 -*-
"""Write remaining undownloaded full-genre books for next resume."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BOOK = Path(r"e:\oh-story-claudecode\book")
OUT = BOOK / "_analysis"
OUT.mkdir(exist_ok=True)

queue = json.loads((BOOK / "_download_queue_全题材阅读榜_20260916.json").read_text(encoding="utf-8"))
state_p = BOOK / "_download_state_全题材_20260916.json"
state = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {"ok": [], "fail": [], "skip": []}

done = set(state.get("ok", [])) | set(state.get("skip", []))
meta = {e["book_id"]: e for e in queue["entries"]}

pending_ids = [bid for bid in queue["need_ids"] if bid not in done]
# include fails for retry
for bid in state.get("fail", []):
    if bid not in pending_ids and bid not in done:
        pending_ids.append(bid)

pending_entries = []
for bid in pending_ids:
    e = meta.get(bid, {"book_id": bid, "title": "(未知)", "author": "", "source": "", "rank": 0})
    pending_entries.append(
        {
            "book_id": bid,
            "title": e.get("title"),
            "author": e.get("author"),
            "rank": e.get("rank"),
            "source": e.get("source"),
            "range": "1-60",
            "status": "pending",
        }
    )

payload = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "note": "全题材阅读榜未下载完的书，下次继续用 batch_download_fullrank.py / WebUI 串行下前60章",
    "resume_how": [
        "启动 F:\\book\\TomatoNovelDownloader-Win64-v2.4.15.exe --server",
        "save_path 设为 e:\\oh-story-claudecode\\book，novel_format=txt",
        "将本文件 need_ids 写回队列或直接喂给 batch_download_fullrank.py",
        "POST /api/jobs {book_id, range_start:1, range_end:60} 串行执行",
    ],
    "progress": {
        "queue_total_need": len(queue["need_ids"]),
        "downloaded_ok": len(state.get("ok", [])),
        "skipped_local": len(state.get("skip", [])),
        "failed": len(state.get("fail", [])),
        "pending": len(pending_ids),
        "local_txt_novels": len([p for p in BOOK.glob("*.txt") if not p.name.startswith("_")]),
    },
    "need_ids": pending_ids,
    "books": pending_entries,
}

# JSON + readable markdown
jp = BOOK / "_pending_download_全题材_20260916.json"
jp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

md = [
    "# 全题材阅读榜 · 未下载书单（下次继续）",
    "",
    f"- 生成时间：{payload['created_at']}",
    f"- 已下载成功：{payload['progress']['downloaded_ok']}",
    f"- 待下载：{payload['progress']['pending']}",
    f"- 本地 txt 小说数：{payload['progress']['local_txt_novels']}",
    "",
    "## 续下方法",
    "",
    "1. `F:\\book\\TomatoNovelDownloader-Win64-v2.4.15.exe --server`",
    "2. save_path → `e:\\oh-story-claudecode\\book`，格式 txt",
    "3. 对本文件 `need_ids` 串行 `POST /api/jobs`：`range_start=1, range_end=60`",
    "4. 或改 `_download_queue_全题材阅读榜_20260916.json` 的 need_ids 后跑 `book/_tools/batch_download_fullrank.py`",
    "",
    "## 待下载列表",
    "",
    "| # | bookId | 书名 | 作者 | 来源 |",
    "|---:|---|---|---|---|",
]
for i, e in enumerate(pending_entries, 1):
    md.append(
        f"| {i} | `{e['book_id']}` | {e['title']} | {e.get('author') or ''} | {e.get('source') or ''} |"
    )
md.append("")
mp = BOOK / "_pending_download_全题材_20260916.md"
mp.write_text("\n".join(md), encoding="utf-8")

# also update state note
state["paused_at"] = payload["created_at"]
state["pending_count"] = len(pending_ids)
state_p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(payload["progress"], ensure_ascii=False, indent=2))
print("wrote", jp.name, mp.name)
