# -*- coding: utf-8 -*-
"""Heuristic AI-trace scanner for Chinese webnovel txt samples.

Not an authorship oracle — relative ranking for corpus triage.
Samples early + mid chapters, scores pattern density, emits JSON report.
"""
from __future__ import annotations

import json
import math
import os
import random
import re
from collections import Counter
from pathlib import Path

BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
OUT_DIR = BOOK_DIR / "_analysis"
OUT_DIR.mkdir(exist_ok=True)

CHAPTER_SPLIT = re.compile(
    r"(?m)^(?:第\s*[0-9一二三四五六七八九十百千零两]+\s*章[^\n]*|"
    r"Chapter\s*\d+[^\n]*)$"
)

# Strong / mid / weak AI-ish patterns for 网文语境
STRONG_PATTERNS = [
    (r"不是[^，。！？\n]{1,12}，而是", "不是X而是Y"),
    (r"并非[^，。！？\n]{1,12}，而是", "并非X而是Y"),
    (r"与其说[^，。！？\n]{1,16}，不如说", "与其说不如说"),
    (r"值得注意的是", "值得注意的是"),
    (r"更重要的是", "更重要的是"),
    (r"换句话说", "换句话说"),
    (r"总而言之|综上所述|归根结底|本质上来说", "总结升维词"),
    (r"不禁让人(?:感到|想到|意识到)", "不禁让人"),
    (r"仿佛在提醒|仿佛在告诉|仿佛在说", "拟人解说腔"),
]

MID_PATTERNS = [
    (r"与此同时", "与此同时"),
    (r"就在这时|就在此刻|就在这一刻", "就在这时"),
    (r"心中暗道|暗暗想道|心里默默", "心中暗道"),
    (r"深吸一口气", "深吸一口气"),
    (r"目光(?:深邃|幽深|一凝|微眯)", "目光套话"),
    (r"嘴角(?:微微|微微一|轻轻)(?:上扬|上翘|勾起)", "嘴角微扬"),
    (r"不由得(?:一愣|一怔|心头一震)", "不由得一愣"),
    (r"脑海中(?:闪过|浮现|回响起)", "脑海闪过"),
    (r"仿佛[^，。！？\n]{2,20}", "仿佛…"),
    (r"似乎[^，。！？\n]{2,16}", "似乎…"),
    (r"一种[^，。！？\n]{2,12}的感觉", "一种…的感觉"),
    (r"不仅仅是[^，。]{1,10}，更是", "不仅仅是更是"),
]

HUMANISH_PATTERNS = [
    (r"(?:卧槽|我靠|他妈的|牛逼|离谱|整不会|整活儿|麻了|绷不住)", "口语脏话/梗"),
    (r"(?:啊啊啊|哈哈哈+|草+|我去|绝了|笑死)", "情绪语气崩坏"),
    (r"[…．]{2,}|……+", "省略号毛边"),
    (r"(?:咋|嘛|咧|咯|嘿|哼|切)", "口语助词"),
]

DIALOGUE_RE = re.compile(r"[「“\"].{1,80}?[」”\"]")
SENT_RE = re.compile(r"[^。！？!?；;\n]+[。！？!?；;]?")


def split_chapters(text: str) -> list[tuple[str, str]]:
    parts = CHAPTER_SPLIT.split(text)
    titles = CHAPTER_SPLIT.findall(text)
    if not titles:
        # no chapter headers — treat whole as one blob, take head/mid slices
        return [("(全文抽样)", text)]
    chapters = []
    # split keeps separators out when using findall+split carefully
    # CHAPTER_SPLIT.split removes headers; re-find positions
    matches = list(CHAPTER_SPLIT.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            chapters.append((m.group(0).strip(), body))
    return chapters or [("(全文抽样)", text)]


def sample_text(chapters: list[tuple[str, str]], max_chars: int = 28000) -> str:
    if not chapters:
        return ""
    n = len(chapters)
    idxs = []
    # early
    idxs.extend(range(min(5, n)))
    # mid
    if n > 10:
        mid = n // 2
        idxs.extend(range(mid, min(mid + 3, n)))
    # late-of-sample
    if n > 20:
        idxs.extend(range(max(0, n - 3), n))
    seen = set()
    chunks = []
    total = 0
    for i in idxs:
        if i in seen:
            continue
        seen.add(i)
        title, body = chapters[i]
        piece = f"\n【{title}】\n{body[:4500]}"
        chunks.append(piece)
        total += len(piece)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def sentence_lengths(text: str) -> list[int]:
    lens = []
    for m in SENT_RE.finditer(text):
        s = m.group(0).strip()
        if len(s) < 4:
            continue
        lens.append(len(s))
    return lens


def uniformity(lens: list[int]) -> float:
    if len(lens) < 20:
        return 0.0
    mean = sum(lens) / len(lens)
    if mean <= 0:
        return 0.0
    var = sum((x - mean) ** 2 for x in lens) / len(lens)
    cv = math.sqrt(var) / mean  # lower = more uniform
    # map: cv 0.35~very uniform AI-ish; cv>0.8 humanish
    score = max(0.0, min(1.0, (0.75 - cv) / 0.45))
    return score


def count_patterns(text: str, patterns: list[tuple[str, str]]) -> tuple[int, dict]:
    hits = Counter()
    total = 0
    for pat, name in patterns:
        n = len(re.findall(pat, text))
        if n:
            hits[name] = n
            total += n
    return total, dict(hits)


def paragraph_stats(text: str) -> dict:
    paras = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    if not paras:
        paras = [p.strip() for p in text.splitlines() if p.strip()]
    plens = [len(p) for p in paras if len(p) > 10]
    if len(plens) < 8:
        return {"para_uniform": 0.0, "para_count": len(plens)}
    mean = sum(plens) / len(plens)
    var = sum((x - mean) ** 2 for x in plens) / len(plens)
    cv = math.sqrt(var) / mean if mean else 1
    return {
        "para_uniform": max(0.0, min(1.0, (0.7 - cv) / 0.4)),
        "para_count": len(plens),
        "para_mean": round(mean, 1),
    }


def score_book(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    # strip downloader meta if any
    chapters = split_chapters(raw)
    sample = sample_text(chapters)
    chars = max(len(sample), 1)
    per1k = lambda n: n * 1000 / chars

    s_n, s_hits = count_patterns(sample, STRONG_PATTERNS)
    m_n, m_hits = count_patterns(sample, MID_PATTERNS)
    h_n, h_hits = count_patterns(sample, HUMANISH_PATTERNS)

    lens = sentence_lengths(sample)
    uni = uniformity(lens)
    pstat = paragraph_stats(sample)
    dlg = len(DIALOGUE_RE.findall(sample))

    # density scores
    strong_d = per1k(s_n)
    mid_d = per1k(m_n)
    human_d = per1k(h_n)

    # composite 0-100
    ai_score = (
        min(strong_d * 18, 35)
        + min(mid_d * 6, 30)
        + uni * 18
        + pstat["para_uniform"] * 12
        - min(human_d * 10, 25)
    )
    ai_score = max(0.0, min(100.0, ai_score))

    if ai_score >= 55:
        label = "likely_ai"
    elif ai_score >= 38:
        label = "mixed_or_template"
    else:
        label = "likely_human"

    return {
        "file": path.name,
        "path": str(path),
        "chapter_count_detected": len(chapters),
        "sample_chars": chars,
        "ai_score": round(ai_score, 1),
        "label": label,
        "metrics": {
            "strong_hits_per1k": round(strong_d, 3),
            "mid_hits_per1k": round(mid_d, 3),
            "humanish_hits_per1k": round(human_d, 3),
            "sentence_uniformity": round(uni, 3),
            "dialogue_count_in_sample": dlg,
            **{k: v for k, v in pstat.items()},
        },
        "strong_hits": s_hits,
        "mid_hits": m_hits,
        "humanish_hits": h_hits,
    }


def main():
    files = sorted(
        p for p in BOOK_DIR.glob("*.txt") if not p.name.startswith("_")
    )
    results = [score_book(p) for p in files]
    results.sort(key=lambda x: -x["ai_score"])

    summary = {
        "total": len(results),
        "likely_ai": sum(1 for r in results if r["label"] == "likely_ai"),
        "mixed_or_template": sum(
            1 for r in results if r["label"] == "mixed_or_template"
        ),
        "likely_human": sum(1 for r in results if r["label"] == "likely_human"),
        "books": results,
    }
    out = OUT_DIR / "ai_trace_scores.json"
    out.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {out} total={len(results)}")
    for r in results:
        print(f"{r['ai_score']:5.1f}  {r['label']:20s}  {r['file']}")


if __name__ == "__main__":
    main()
