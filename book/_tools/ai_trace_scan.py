# -*- coding: utf-8 -*-
"""Webnovel-tuned AI-trace triage for Tomato txt corpus.

Relative ranking only. Emits scores + evidence snippets for manual review.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
OUT_DIR = BOOK_DIR / "_analysis"
OUT_DIR.mkdir(exist_ok=True)

CHAPTER_SPLIT = re.compile(
    r"(?m)^(?:第\s*[0-9一二三四五六七八九十百千零两]+\s*章[^\n]*)$"
)

# 网文 AI / 高模板常见指纹（相对密度）
AI_PATTERNS = [
    # 强
    (3.0, r"空气(?:仿佛|似乎)?(?:瞬间)?(?:凝固|静止)了?", "空气凝固"),
    (3.0, r"瞳孔(?:猛地|骤然)?一(?:缩|震)", "瞳孔一缩"),
    (2.5, r"不可置信地(?:看着|望着|瞪着)", "不可置信地看"),
    (2.5, r"意味深长地(?:看|望|笑)", "意味深长"),
    (2.5, r"缓缓(?:开口|说道?)道?", "缓缓开口道"),
    (2.0, r"三人面面相觑|众人面面相觑", "面面相觑"),
    (2.5, r"不是[^，。！？\n]{1,10}，而是", "不是X而是Y"),
    (2.5, r"并非[^，。！？\n]{1,10}，而是", "并非X而是Y"),
    (2.0, r"值得注意的是|更重要的是|换句话说|总而言之", "议论连接词"),
    (2.0, r"一种[^，。！？\n]{2,14}的感觉", "一种…的感觉"),
    # 中
    (1.5, r"下一秒|转眼间|瞬息之间", "下一秒/转眼间"),
    (1.5, r"话音刚落", "话音刚落"),
    (1.5, r"深吸一口气", "深吸一口气"),
    (1.2, r"心中暗道|暗暗想道", "心中暗道"),
    (1.2, r"嘴角(?:微微)?(?:上扬|上翘|一勾)", "嘴角上扬"),
    (1.2, r"目光(?:深邃|幽深|一凝|微眯)", "目光套话"),
    (1.2, r"脑海中(?:闪过|浮现)", "脑海闪过"),
    (1.0, r"不由得一(?:愣|怔)", "不由得一愣"),
    (1.0, r"就在这(?:时|刻|一瞬间)", "就在这时"),
    (1.0, r"竟然|居然", "竟然/居然"),
    (1.0, r"仿佛|似乎", "仿佛/似乎"),
    (1.2, r"强忍着.{0,6}(?:激动|怒火|泪水|情绪)", "强忍着情绪"),
    (1.5, r"心头一(?:震|紧|凛|跳)", "心头一震"),
    (1.2, r"不禁(?:感叹|叹道|一愣)", "不禁…"),
]

HUMAN_PATTERNS = [
    (2.0, r"卧槽|我靠|我操|他妈的|牛逼|离谱|麻了|绷不住|整不会|笑死|绝了", "脏话/梗"),
    (1.5, r"啊啊啊+|哈哈哈+|草+|我去+", "情绪崩坏"),
    (1.2, r"(?<![a-zA-Z])(?:咋|嘛|咧|咯)(?![a-zA-Z])", "口语助词"),
    (1.0, r"……|…{2,}", "省略毛边"),
    (1.5, r"(?:打野|辅助|中单|adc|ad位|野区|龙坑|一血|五杀|爆头|爆甲|舔包|跑刀)", "游戏黑话"),
]

SENT_RE = re.compile(r"[^。！？!?；;\n]+[。！？!?；;]?")


def chapters_of(text: str):
    matches = list(CHAPTER_SPLIT.finditer(text))
    if not matches:
        return [("(全文)", text)]
    out = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            out.append((m.group(0).strip(), body))
    return out or [("(全文)", text)]


def sample_text(chapters, max_chars=32000):
    n = len(chapters)
    idxs = list(range(min(6, n)))
    if n > 12:
        mid = n // 2
        idxs += list(range(mid, min(mid + 4, n)))
    if n > 25:
        idxs += list(range(max(0, n - 4), n))
    seen, chunks, total = set(), [], 0
    for i in idxs:
        if i in seen:
            continue
        seen.add(i)
        title, body = chapters[i]
        piece = f"\n【{title}】\n{body[:5000]}"
        chunks.append(piece)
        total += len(piece)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def lexical_diversity(text: str) -> float:
    # Chinese: approximate by overlapping bigrams
    chars = [c for c in text if "\u4e00" <= c <= "\u9fff"]
    if len(chars) < 200:
        return 0.5
    bigrams = [chars[i] + chars[i + 1] for i in range(len(chars) - 1)]
    return len(set(bigrams)) / len(bigrams)


def sentence_cv(text: str) -> float:
    lens = [len(s.strip()) for s in SENT_RE.findall(text) if len(s.strip()) >= 4]
    if len(lens) < 30:
        return 0.6
    mean = sum(lens) / len(lens)
    var = sum((x - mean) ** 2 for x in lens) / len(lens)
    return math.sqrt(var) / mean if mean else 0.6


def evidence_snippets(text: str, pattern: str, limit=3):
    snips = []
    for m in re.finditer(pattern, text):
        a = max(0, m.start() - 18)
        b = min(len(text), m.end() + 24)
        snip = re.sub(r"\s+", " ", text[a:b]).strip()
        snips.append(snip)
        if len(snips) >= limit:
            break
    return snips


def score_book(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    chapters = chapters_of(raw)
    sample = sample_text(chapters)
    chars = max(len(sample), 1)

    ai_weighted = 0.0
    ai_hits = {}
    evidence = []
    for w, pat, name in AI_PATTERNS:
        found = list(re.finditer(pat, sample))
        n = len(found)
        if not n:
            continue
        density = n * 1000 / chars
        ai_weighted += w * density
        ai_hits[name] = n
        if w >= 2.0 and len(evidence) < 8:
            evidence.append(
                {
                    "pattern": name,
                    "count": n,
                    "snippets": evidence_snippets(sample, pat),
                }
            )

    human_weighted = 0.0
    human_hits = {}
    for w, pat, name in HUMAN_PATTERNS:
        n = len(re.findall(pat, sample))
        if not n:
            continue
        density = n * 1000 / chars
        human_weighted += w * density
        human_hits[name] = n

    ttr = lexical_diversity(sample)
    cv = sentence_cv(sample)
    # low diversity + low sentence CV → AI-ish
    style_ai = max(0.0, (0.42 - ttr) / 0.15) * 8 + max(0.0, (0.55 - cv) / 0.25) * 6

    score = ai_weighted * 4.2 + style_ai - human_weighted * 5.5
    score = max(0.0, min(100.0, score))

    if score >= 42:
        label = "likely_ai"
    elif score >= 26:
        label = "mixed_or_template"
    else:
        label = "likely_human"

    return {
        "file": path.name,
        "chapter_count_detected": len(chapters),
        "sample_chars": chars,
        "ai_score": round(score, 1),
        "label": label,
        "metrics": {
            "ai_weighted_density": round(ai_weighted, 3),
            "human_weighted_density": round(human_weighted, 3),
            "bigram_ttr": round(ttr, 4),
            "sentence_length_cv": round(cv, 4),
            "style_ai_component": round(style_ai, 2),
        },
        "ai_hits": ai_hits,
        "human_hits": human_hits,
        "evidence": evidence,
    }


def main():
    files = sorted(p for p in BOOK_DIR.glob("*.txt") if not p.name.startswith("_"))
    results = [score_book(p) for p in files]
    results.sort(key=lambda x: -x["ai_score"])
    summary = {
        "note": "启发式相对排序，非作者身份鉴定。likely_ai/mixed 需结合抽样精读。",
        "total": len(results),
        "likely_ai": sum(1 for r in results if r["label"] == "likely_ai"),
        "mixed_or_template": sum(
            1 for r in results if r["label"] == "mixed_or_template"
        ),
        "likely_human": sum(1 for r in results if r["label"] == "likely_human"),
        "books": results,
    }
    out = OUT_DIR / "ai_trace_scores.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "total": summary["total"],
                "likely_ai": summary["likely_ai"],
                "mixed": summary["mixed_or_template"],
                "human": summary["likely_human"],
                "top10": [
                    {"score": r["ai_score"], "label": r["label"], "file": r["file"]}
                    for r in results[:10]
                ],
                "bottom5": [
                    {"score": r["ai_score"], "label": r["label"], "file": r["file"]}
                    for r in results[-5:]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
