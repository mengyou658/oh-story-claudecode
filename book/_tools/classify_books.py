# -*- coding: utf-8 -*-
"""Calibrated triage for Tomato 游戏体育 webnovels.

Produces:
- ai_books.md / human_books.md / mixed_books.md
- verdicts.json
Relative, evidence-based; not an authorship certificate.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
OUT = BOOK_DIR / "_analysis"
OUT.mkdir(exist_ok=True)

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
    (r"强忍着.{0,8}(?:激动|怒火|情绪)", "强忍情绪"),
]

HUMAN = [
    (r"卧槽|我靠|我操|他妈的|牛逼|离谱|麻了|绷不住|笑死|绝了|我去", "脏话梗"),
    (r"啊啊啊+|哈哈哈+|草+", "情绪崩"),
    (r"打野|辅助|中单|adc|野区|龙坑|一血|五杀|爆头|舔包|跑刀|rating|major|突破手", "游戏黑话"),
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
    strong_n = soft_n = human_n = 0
    evidence = []
    for pat, name in AI_STRONG:
        n = len(re.findall(pat, s))
        if n:
            strong[name] = n
            strong_n += n
            if len(evidence) < 6:
                m = re.search(pat, s)
                if m:
                    a, b = max(0, m.start() - 12), min(len(s), m.end() + 20)
                    evidence.append(re.sub(r"\s+", " ", s[a:b]).strip())
    for pat, name in AI_SOFT:
        n = len(re.findall(pat, s))
        if n:
            soft[name] = n
            soft_n += n
    for pat, name in HUMAN:
        n = len(re.findall(pat, s))
        if n:
            human[name] = n
            human_n += n

    # stylistic
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

    # short-line ratio (human esports often has clipped lines)
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    short_ratio = sum(1 for ln in lines if 2 <= len(ln) <= 12) / max(len(lines), 1)

    # dialogue-ish
    dlg = len(re.findall(r"[「“\"].{1,60}?[」”\"]", s))

    ai_score = (
        dens(strong_n, chars) * 12
        + dens(soft_n, chars) * 3.5
        + max(0, (0.48 - ttr)) * 40
        + max(0, (0.5 - cv)) * 25
        - dens(human_n, chars) * 4.5
        - short_ratio * 12
    )
    ai_score = max(0, min(100, ai_score))

    # calibrated labels for this corpus (番茄游戏体育偏口语)
    if ai_score >= 28 and dens(strong_n, chars) >= 0.15:
        verdict = "ai"
    elif ai_score >= 16 or (dens(soft_n, chars) >= 1.2 and dens(human_n, chars) < 1.0):
        verdict = "mixed"
    else:
        verdict = "human"

    return {
        "file": path.name,
        "verdict": verdict,
        "ai_score": round(ai_score, 1),
        "metrics": {
            "strong_per1k": round(dens(strong_n, chars), 3),
            "soft_per1k": round(dens(soft_n, chars), 3),
            "human_per1k": round(dens(human_n, chars), 3),
            "ttr": round(ttr, 4),
            "sent_cv": round(cv, 4),
            "short_line_ratio": round(short_ratio, 3),
            "dialogue_count": dlg,
            "sample_chars": chars,
        },
        "strong_hits": strong,
        "soft_hits": soft,
        "human_hits": human,
        "evidence_snippets": evidence,
    }


def md_list(title: str, items: list[dict], note: str) -> str:
    lines = [f"# {title}", "", note, "", f"合计：**{len(items)}** 本", "", "| 书名 | 分数 | 说明 |", "|---|---:|---|"]
    for it in items:
        reasons = []
        if it["strong_hits"]:
            reasons.append("强模板：" + "、".join(f"{k}×{v}" for k, v in list(it["strong_hits"].items())[:4]))
        if it["soft_hits"]:
            top = sorted(it["soft_hits"].items(), key=lambda x: -x[1])[:3]
            reasons.append("软模板：" + "、".join(f"{k}×{v}" for k, v in top))
        if it["human_hits"]:
            top = sorted(it["human_hits"].items(), key=lambda x: -x[1])[:3]
            reasons.append("人味信号：" + "、".join(f"{k}×{v}" for k, v in top))
        if it["evidence_snippets"]:
            reasons.append("摘录：" + " / ".join(it["evidence_snippets"][:2]))
        m = it["metrics"]
        reasons.append(
            f"指标 strong/soft/human每千字={m['strong_per1k']}/{m['soft_per1k']}/{m['human_per1k']}，短句比={m['short_line_ratio']}"
        )
        expl = "<br>".join(reasons) if reasons else "（无明显强证据，按综合分归类）"
        lines.append(f"| {it['file']} | {it['ai_score']} | {expl} |")
    lines.append("")
    return "\n".join(lines)


def main():
    files = sorted(p for p in BOOK_DIR.glob("*.txt") if not p.name.startswith("_"))
    results = [analyze(p) for p in files]
    results.sort(key=lambda x: -x["ai_score"])

    ai = [r for r in results if r["verdict"] == "ai"]
    mixed = [r for r in results if r["verdict"] == "mixed"]
    human = [r for r in results if r["verdict"] == "human"]

    disclaimer = (
        "> 说明：基于开篇+中段抽样的**启发式相对归类**，用于语料分流，"
        "> **不能**当作作者身份鉴定。`ai`=`AI痕迹偏高/高模板`，`mixed`=`模板重但有人味`，`human`=`口语/黑话/毛边更明显`。"
    )

    (OUT / "verdicts.json").write_text(
        json.dumps(
            {
                "disclaimer": "heuristic triage only",
                "counts": {"ai": len(ai), "mixed": len(mixed), "human": len(human)},
                "books": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUT / "ai_books.md").write_text(
        md_list("疑似 AI / 高模板书单", ai, disclaimer), encoding="utf-8"
    )
    (OUT / "mixed_books.md").write_text(
        md_list("混合 / 高套路书单", mixed, disclaimer), encoding="utf-8"
    )
    (OUT / "human_books.md").write_text(
        md_list("更偏人工书单", human, disclaimer), encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "ai": len(ai),
                "mixed": len(mixed),
                "human": len(human),
                "ai_files": [x["file"] for x in ai],
                "mixed_files": [x["file"] for x in mixed],
                "top_human": [x["file"] for x in sorted(human, key=lambda z: z["ai_score"])[:8]],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
