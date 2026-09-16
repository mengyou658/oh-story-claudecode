# -*- coding: utf-8 -*-
"""Classify ALL novels currently in book/ and merge into verdicts_final.json.

Uses heuristic score + keep previous human overrides when file still exists.
New books without override: relative ranking into ai/mixed/human.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
OUT = BOOK_DIR / "_analysis"
OUT.mkdir(exist_ok=True)

# Keep prior qualitative overrides (from 游戏体育 batch)
PREV = OUT / "verdicts_final.json"
OVERRIDES = {}
if PREV.exists():
    prev = json.loads(PREV.read_text(encoding="utf-8"))
    for b in prev.get("books", []):
        # only keep explicit non-default reasons (精读覆盖)
        reason = b.get("reason") or ""
        if "开篇" in reason or "精读" in reason or "黑话" in reason or "说明腔" in reason or "模板" in reason:
            OVERRIDES[b["file"]] = (b["verdict"], reason)

CH_RE = re.compile(r"(?m)^第\s*[0-9一二三四五六七八九十百千零两]+\s*章[^\n]*$")

AI_STRONG = [
    (r"不是[^，。！？\n]{1,12}，而是", "不是X而是Y"),
    (r"并非[^，。！？\n]{1,12}，而是", "并非X而是Y"),
    (r"空气(?:仿佛|似乎)?(?:瞬间)?(?:凝固|静止)", "空气凝固"),
    (r"瞳孔(?:猛地|骤然)?一(?:缩|震)", "瞳孔一缩"),
    (r"不可置信地(?:看|望|瞪)", "不可置信"),
    (r"意味深长地", "意味深长"),
    (r"缓缓(?:开口|说道?)道?", "缓缓开口道"),
    (r"一种[^，。！？\n]{2,14}的感觉", "一种…的感觉"),
    (r"值得注意的是|更重要的是|换句话说|总而言之|归根结底", "议论连接词"),
    (r"容颜绝美|剑眉星目|玉树临风|长发如瀑", "外貌套话"),
    (r"一道身影", "一道身影"),
    (r"记忆如潮水", "记忆潮水"),
]
AI_SOFT = [
    (r"深吸一口气", "深吸一口气"),
    (r"心中暗道|暗暗想道", "心中暗道"),
    (r"嘴角(?:微微)?(?:上扬|上翘|一勾)", "嘴角上扬"),
    (r"目光(?:深邃|幽深|一凝|微眯)", "目光套话"),
    (r"脑海中(?:闪过|浮现)", "脑海闪过"),
    (r"话音刚落", "话音刚落"),
    (r"下一秒|转眼间", "下一秒"),
    (r"就在这(?:时|刻|一瞬间)", "就在这时"),
    (r"不由得一(?:愣|怔)", "不由得一愣"),
    (r"与此同时", "与此同时"),
]
HUMAN = [
    (r"卧槽|我靠|我操|他妈的|牛逼|离谱|麻了|绷不住|笑死|绝了|我去", "脏话梗"),
    (r"啊啊啊+|哈哈哈+|草+", "情绪崩"),
    (r"打野|辅助|中单|adc|野区|一血|五杀|爆头|舔包|rating|major", "游戏黑话"),
    (r"……", "省略毛边"),
]


def sample(path: Path, max_chars=36000) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    ms = list(CH_RE.finditer(text))
    if not ms:
        return text[:max_chars]
    idxs = list(range(min(5, len(ms))))
    if len(ms) > 12:
        mid = len(ms) // 2
        idxs += list(range(mid, min(mid + 3, len(ms))))
    if len(ms) > 25:
        idxs += list(range(max(0, len(ms) - 3), len(ms)))
    chunks, total, seen = [], 0, set()
    for i in idxs:
        if i in seen:
            continue
        seen.add(i)
        a = ms[i].end()
        b = ms[i + 1].start() if i + 1 < len(ms) else min(len(text), a + 6000)
        piece = text[a:b][:5000]
        chunks.append(piece)
        total += len(piece)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def dens(n, chars):
    return n * 1000 / max(chars, 1)


def analyze(path: Path) -> dict:
    s = sample(path)
    chars = len(s)
    strong, soft, human = {}, {}, {}
    sn = softn = hn = 0
    evidence = []
    for pat, name in AI_STRONG:
        n = len(re.findall(pat, s))
        if n:
            strong[name] = n
            sn += n
            if len(evidence) < 5:
                m = re.search(pat, s)
                if m:
                    a, b = max(0, m.start() - 10), min(len(s), m.end() + 18)
                    evidence.append(re.sub(r"\s+", " ", s[a:b]).strip())
    for pat, name in AI_SOFT:
        n = len(re.findall(pat, s))
        if n:
            soft[name] = n
            softn += n
    for pat, name in HUMAN:
        n = len(re.findall(pat, s))
        if n:
            human[name] = n
            hn += n

    zh = [c for c in s if "\u4e00" <= c <= "\u9fff"]
    if len(zh) > 300:
        big = [zh[i] + zh[i + 1] for i in range(len(zh) - 1)]
        ttr = len(set(big)) / len(big)
    else:
        ttr = 0.55
    sents = [x.strip() for x in re.findall(r"[^。！？!?\n]+[。！？!?]?", s) if len(x.strip()) >= 4]
    if len(sents) >= 25:
        lens = [len(x) for x in sents]
        mean = sum(lens) / len(lens)
        cv = math.sqrt(sum((x - mean) ** 2 for x in lens) / len(lens)) / mean
    else:
        cv = 0.6
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    short_ratio = sum(1 for ln in lines if 2 <= len(ln) <= 12) / max(len(lines), 1)

    ai_score = (
        dens(sn, chars) * 12
        + dens(softn, chars) * 3.5
        + max(0, (0.48 - ttr)) * 40
        + max(0, (0.5 - cv)) * 25
        - dens(hn, chars) * 4.5
        - short_ratio * 12
    )
    ai_score = max(0, min(100, ai_score))
    return {
        "file": path.name,
        "ai_score": round(ai_score, 1),
        "metrics": {
            "strong_per1k": round(dens(sn, chars), 3),
            "soft_per1k": round(dens(softn, chars), 3),
            "human_per1k": round(dens(hn, chars), 3),
            "ttr": round(ttr, 4),
            "sent_cv": round(cv, 4),
            "short_line_ratio": round(short_ratio, 3),
            "sample_chars": chars,
        },
        "strong_hits": strong,
        "soft_hits": soft,
        "human_hits": human,
        "evidence_snippets": evidence,
    }


def md_table(title, items, intro):
    lines = [f"# {title}", "", intro, "", f"合计：**{len(items)}** 本", ""]
    for i, it in enumerate(items, 1):
        lines.append(f"## {i}. {it['file']}")
        lines.append("")
        lines.append(f"- **判定**：`{it['verdict']}`")
        lines.append(f"- **启发式分**：{it['ai_score']}")
        lines.append(f"- **说明**：{it['reason']}")
        if it.get("evidence"):
            lines.append(f"- **摘录**：{' ｜ '.join(it['evidence'][:2])}")
        lines.append("")
    return "\n".join(lines)


def main():
    files = sorted(p for p in BOOK_DIR.glob("*.txt") if not p.name.startswith("_"))
    scored = [analyze(p) for p in files]
    scored.sort(key=lambda x: -x["ai_score"])

    # relative cuts on books without override
    n = len(scored)
    # top ~8% ai, next ~20% mixed, rest human — but floor by score
    ai_cut = max(1, int(n * 0.08))
    mixed_cut = max(ai_cut + 1, int(n * 0.28))

    final = []
    for i, base in enumerate(scored):
        f = base["file"]
        if f in OVERRIDES:
            verdict, reason = OVERRIDES[f]
        else:
            if i < ai_cut and base["ai_score"] >= 8:
                verdict = "ai"
                reason = "相对分数靠前：光滑模板词更密，人味信号偏弱（全题材扩库相对归类）。"
            elif i < mixed_cut and base["ai_score"] >= 2:
                verdict = "mixed"
                reason = "相对中高模板密度，作混合语料侧。"
            else:
                verdict = "human"
                reason = "口语/短句/人味信号相对更强，或分数偏低；作人工语料侧。"
        final.append(
            {
                "file": f,
                "verdict": verdict,
                "ai_score": base["ai_score"],
                "reason": reason,
                "evidence": base.get("evidence_snippets") or [],
                "metrics": base.get("metrics"),
                "strong_hits": base.get("strong_hits"),
                "soft_hits": base.get("soft_hits"),
                "human_hits": base.get("human_hits"),
            }
        )

    by = {"ai": [], "mixed": [], "human": []}
    for it in final:
        by[it["verdict"]].append(it)

    disclaimer = (
        "> **用途**：语料分流（AI痕迹对照 / 人味表达抽取），**不是**作者身份实锤。\n"
        "> **方法**：启发式相对分 + 既有精读覆盖。含游戏体育榜 + 全题材阅读榜增量。"
    )
    payload = {
        "disclaimer": "triage for phrase mining, not authorship claim",
        "counts": {k: len(v) for k, v in by.items()},
        "total_books": len(final),
        "books": sorted(
            final,
            key=lambda x: (x["verdict"] != "ai", x["verdict"] != "mixed", -x["ai_score"]),
        ),
    }
    (OUT / "verdicts_final.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "ai_books.md").write_text(md_table("疑似 AI / 高光滑模板书单", by["ai"], disclaimer), encoding="utf-8")
    (OUT / "mixed_books.md").write_text(md_table("混合 / 高套路书单", by["mixed"], disclaimer), encoding="utf-8")
    (OUT / "human_books.md").write_text(md_table("更偏人工书单", by["human"], disclaimer), encoding="utf-8")
    (OUT / "ai_books.txt").write_text("\n".join(x["file"] for x in by["ai"]) + "\n", encoding="utf-8")
    (OUT / "mixed_books.txt").write_text("\n".join(x["file"] for x in by["mixed"]) + "\n", encoding="utf-8")
    (OUT / "human_books.txt").write_text("\n".join(x["file"] for x in by["human"]) + "\n", encoding="utf-8")
    print(json.dumps(payload["counts"] | {"total": len(final)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
