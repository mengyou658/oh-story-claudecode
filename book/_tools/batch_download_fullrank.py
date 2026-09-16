# -*- coding: utf-8 -*-
"""Serial Tomato WebUI download for full-genre queue (resume-safe)."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:18423"
BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
QUEUE = BOOK_DIR / "_download_queue_全题材阅读榜_20260916.json"
LOG = BOOK_DIR / "_download_log_全题材_20260916.txt"
STATE = BOOK_DIR / "_download_state_全题材_20260916.json"


def api(method: str, path: str, body: dict | None = None, timeout: int = 60):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def log(msg: str):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def busy_jobs():
    data = api("GET", "/api/jobs")
    return [j for j in data.get("items", []) if j.get("state") in ("queued", "running")]


def wait_idle(max_wait: int = 900):
    t0 = time.time()
    while True:
        busy = busy_jobs()
        if not busy:
            return
        j = busy[0]
        p = j.get("progress") or {}
        if int(time.time() - t0) % 12 < 3:
            log(
                f"wait job#{j.get('id')} {j.get('state')} "
                f"{p.get('saved_chapters')}/{p.get('chapter_total')} {j.get('book_id')}"
            )
        if time.time() - t0 > max_wait:
            log(f"WARN wait timeout on {j.get('book_id')}")
            return
        time.sleep(3)


def already_local(book_id: str) -> bool:
    # folder with status OR any prior done record in state
    p = BOOK_DIR / book_id
    if p.is_dir() and (p / "status.json").exists():
        return True
    return False


def create_job(book_id: str) -> bool:
    body = {"book_id": book_id, "range_start": 1, "range_end": 60}
    for attempt in range(10):
        try:
            job = api("POST", "/api/jobs", body)
            log(f"QUEUED job#{job.get('id')} {book_id}")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                log(f"429 {book_id} sleep 8s attempt={attempt+1}")
                time.sleep(8)
                continue
            log(f"FAIL create {book_id} HTTP {e.code}")
            return False
        except Exception as ex:
            log(f"FAIL create {book_id} {ex}")
            time.sleep(3)
    return False


def wait_book_done(book_id: str, timeout: int = 600) -> str:
    t0 = time.time()
    last = None
    while time.time() - t0 < timeout:
        data = api("GET", "/api/jobs")
        items = [j for j in data.get("items", []) if j.get("book_id") == book_id]
        if not items:
            time.sleep(2)
            continue
        j = sorted(items, key=lambda x: x.get("id", 0))[-1]
        st = j.get("state")
        p = j.get("progress") or {}
        last = st
        if st == "done":
            log(f"DONE {book_id} {p.get('saved_chapters')}/{p.get('chapter_total')}")
            return "done"
        if st in ("failed", "error", "cancelled"):
            log(f"FAIL job {book_id} state={st} msg={j.get('message')}")
            return st
        time.sleep(3)
    log(f"TIMEOUT {book_id} last={last}")
    return "timeout"


def main():
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    ids = q["need_ids"]
    state = {"ok": [], "fail": [], "skip": []}
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding="utf-8"))

    done_set = set(state.get("ok", [])) | set(state.get("skip", []))
    log(f"=== start total_need={len(ids)} resume_ok={len(state.get('ok', []))} ===")

    for i, bid in enumerate(ids, 1):
        if bid in done_set:
            continue
        if already_local(bid):
            log(f"SKIP local {bid} ({i}/{len(ids)})")
            state.setdefault("skip", []).append(bid)
            done_set.add(bid)
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
            continue

        wait_idle()
        log(f"--- {i}/{len(ids)} {bid} ---")
        if not create_job(bid):
            state.setdefault("fail", []).append(bid)
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
            continue
        result = wait_book_done(bid)
        if result == "done":
            state.setdefault("ok", []).append(bid)
            done_set.add(bid)
        else:
            state.setdefault("fail", []).append(bid)
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(0.5)

    log(
        f"=== end ok={len(state.get('ok', []))} skip={len(state.get('skip', []))} "
        f"fail={len(state.get('fail', []))} ==="
    )


if __name__ == "__main__":
    main()
