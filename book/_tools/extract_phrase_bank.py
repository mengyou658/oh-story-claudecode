# -*- coding: utf-8 -*-
"""Extract AI-ish vs human-ish expression pairs for later replacement.

Pulls matched patterns + nearby sentences from ai/mixed vs human books,
and builds a reusable phrase bank JSON.
"""
from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from pathlib import Path

BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
OUT = BOOK_DIR / "_analysis"
VERDICTS = json.loads((OUT / "verdicts_final.json").read_text(encoding="utf-8"))

# meaning buckets: same intent, different surface forms
BUCKETS = [
    {
        "id": "shock_reaction",
        "meaning": "受到惊吓/震惊时的反应",
        "ai_patterns": [
            r"[^。！？\n]{0,20}瞳孔[^。！？\n]{0,20}",
            r"[^。！？\n]{0,16}不可置信[^。！？\n]{0,20}",
            r"[^。！？\n]{0,12}空气[^。！？\n]{0,10}凝固[^。！？\n]{0,10}",
            r"[^。！？\n]{0,16}心头一(?:震|紧|凛)[^。！？\n]{0,16}",
        ],
        "human_patterns": [
            r"[^。！？\n]{0,20}(?:卧槽|我靠|我操|我去)[^。！？\n]{0,30}",
            r"[^。！？\n]{0,24}吓死我了[^。！？\n]{0,24}",
            r"[^。！？\n]{0,20}愣住了?[^。！？\n]{0,20}",
        ],
    },
    {
        "id": "calm_down",
        "meaning": "强压情绪/让自己冷静",
        "ai_patterns": [
            r"[^。！？\n]{0,10}深吸一口气[^。！？\n]{0,30}",
            r"[^。！？\n]{0,10}强忍着[^。！？\n]{0,24}",
            r"[^。！？\n]{0,16}努力让自己冷静[^。！？\n]{0,16}",
        ],
        "human_patterns": [
            r"[^。！？\n]{0,20}(?:咳咳|行吧|得了)[^。！？\n]{0,24}",
            r"[^。！？\n]{0,24}别慌[^。！？\n]{0,24}",
        ],
    },
    {
        "id": "inner_thought",
        "meaning": "内心独白/暗自判断",
        "ai_patterns": [
            r"[^。！？\n]{0,8}心中暗道[^。！？\n]{0,36}",
            r"[^。！？\n]{0,8}暗暗想道[^。！？\n]{0,36}",
            r"[^。！？\n]{0,8}脑海中(?:闪过|浮现)[^。！？\n]{0,36}",
        ],
        "human_patterns": [
            r"[^。！？\n]{0,8}他(?:想|寻思|琢磨)[^。！？\n]{0,36}",
            r"[^。！？\n]{0,30}(?:这谁顶得住|这合理吗|什么鬼)[^。！？\n]{0,20}",
        ],
    },
    {
        "id": "smug_smile",
        "meaning": "得意/轻笑的表情",
        "ai_patterns": [
            r"[^。！？\n]{0,12}嘴角(?:微微)?(?:上扬|上翘|一勾)[^。！？\n]{0,20}",
            r"[^。！？\n]{0,12}意味深长地(?:笑|看)[^。！？\n]{0,16}",
        ],
        "human_patterns": [
            r"[^。！？\n]{0,16}(?:笑了|乐了|哼了一声)[^。！？\n]{0,20}",
            r"[^。！？\n]{0,20}哈哈[^。！？\n]{0,24}",
        ],
    },
    {
        "id": "contrast_not_but",
        "meaning": "转折强调（不是A而是B）",
        "ai_patterns": [
            r"[^。！？\n]{0,8}不是[^，。！？\n]{1,14}，而是[^。！？\n]{1,24}",
            r"[^。！？\n]{0,8}并非[^，。！？\n]{1,14}，而是[^。！？\n]{1,24}",
        ],
        "human_patterns": [
            r"[^。！？\n]{0,20}哪是[^。！？\n]{1,20}",
            r"[^。！？\n]{0,16}根本不是[^。！？\n]{1,24}",
            r"[^。！？\n]{0,16}说白了[^。！？\n]{1,24}",
        ],
    },
    {
        "id": "sudden_turn",
        "meaning": "突然转折/下一拍发生",
        "ai_patterns": [
            r"[^。！？\n]{0,10}下一秒[^。！？\n]{0,36}",
            r"[^。！？\n]{0,10}话音刚落[^。！？\n]{0,36}",
            r"[^。！？\n]{0,10}就在这(?:时|刻)[^。！？\n]{0,36}",
        ],
        "human_patterns": [
            r"[^。！？\n]{0,10}紧接着[^。！？\n]{0,36}",
            r"[^。！？\n]{0,10}这会儿[^。！？\n]{0,36}",
            r"[^。！？\n]{0,8}忽然[^。！？\n]{0,36}",
        ],
    },
    {
        "id": "gaze_desc",
        "meaning": "描写眼神/目光",
        "ai_patterns": [
            r"[^。！？\n]{0,10}目光(?:深邃|幽深|一凝|微眯)[^。！？\n]{0,24}",
            r"[^。！？\n]{0,10}眼神复杂[^。！？\n]{0,20}",
        ],
        "human_patterns": [
            r"[^。！？\n]{0,16}看了(?:他|她|一眼)[^。！？\n]{0,20}",
            r"[^。！？\n]{0,16}盯着[^。！？\n]{0,24}",
        ],
    },
]


def load_text(name: str) -> str:
    return (BOOK_DIR / name).read_text(encoding="utf-8", errors="ignore")


def harvest(text: str, patterns: list[str], limit=40) -> list[str]:
    out, seen = [], set()
    for pat in patterns:
        for m in re.finditer(pat, text):
            s = re.sub(r"\s+", "", m.group(0)).strip("，。！？；、 ")
            if 6 <= len(s) <= 48 and s not in seen:
                seen.add(s)
                out.append(s)
                if len(out) >= limit:
                    return out
    return out


def main():
    by = defaultdict(list)
    for b in VERDICTS["books"]:
        by[b["verdict"]].append(b["file"])

    # treat mixed as potential AI-side source for "ai_like" phrases,
    # human books as replacement targets
    ai_side = by["ai"] + by["mixed"]
    human_side = by["human"]
    if not ai_side:
        # fallback: top quartile by score as ai-side
        ranked = sorted(VERDICTS["books"], key=lambda x: -x["ai_score"])
        ai_side = [x["file"] for x in ranked[:12]]
        human_side = [x["file"] for x in ranked[-20:]]

    ai_corpus = "\n".join(load_text(f)[:80000] for f in ai_side)
    hu_corpus = "\n".join(load_text(f)[:80000] for f in human_side)

    bank = {
        "meta": {
            "purpose": "后期把偏AI/模板句替换成更口语的人味表达",
            "ai_source_books": ai_side,
            "human_source_books": human_side,
            "note": "同义近义对照；替换时需按语境微调，不可无脑全文替换",
        },
        "buckets": [],
    }

    # curated seed pairs (high-precision manual seeds for webnovel)
    curated = [
        {
            "meaning": "震惊",
            "ai": ["瞳孔猛地一缩", "不可置信地看着眼前的一切", "空气仿佛瞬间凝固"],
            "human": ["我靠？", "我去，这什么情况", "愣住了", "吓我一跳"],
        },
        {
            "meaning": "强压情绪",
            "ai": ["深吸一口气，强压下心中的激动", "努力让自己冷静下来"],
            "human": ["他骂了一句", "行吧行吧", "先缓缓", "别整这些"],
        },
        {
            "meaning": "内心独白",
            "ai": ["他心中暗道", "脑海中闪过一个念头"],
            "human": ["他寻思", "他琢磨了一下", "这合理吗", "想了想"],
        },
        {
            "meaning": "得意",
            "ai": ["嘴角微微上扬", "意味深长地笑了笑"],
            "human": ["他乐了", "哼了一声", "笑出声来", "哈哈"],
        },
        {
            "meaning": "不是A是B",
            "ai": ["这不是结束，而是开始", "他感受到的不是恐惧，而是兴奋"],
            "human": ["说白了就是", "哪是什么…，根本就是", "别美化了，就是"],
        },
        {
            "meaning": "突然转折",
            "ai": ["下一秒", "话音刚落", "就在这时"],
            "human": ["紧接着", "这会儿", "忽然", "结果"],
        },
        {
            "meaning": "眼神",
            "ai": ["目光深邃", "目光微眯", "眼神复杂"],
            "human": ["看了他一眼", "盯着不放", "斜了他一眼"],
        },
        {
            "meaning": "系统提示接收",
            "ai": ["一行行冰冷的文字浮现眼前", "机械的提示音在耳边响起"],
            "human": ["面板弹出来了", "系统又开始哔哔", "提示刷了一屏"],
        },
        {
            "meaning": "穿越反应",
            "ai": ["他很快整理好了当下的情况", "记忆如潮水般涌来"],
            "human": ["这儿哪儿啊", "我穿越了？", "等等，这不对劲"],
        },
        {
            "meaning": "战斗自信",
            "ai": ["胜局已定", "一切尽在掌握"],
            "human": ["稳了", "这把有了", "对面别跳了"],
        },
    ]

    pairs = []
    for c in curated:
        for a in c["ai"]:
            for h in c["human"]:
                pairs.append(
                    {
                        "meaning": c["meaning"],
                        "ai_expr": a,
                        "human_expr": h,
                        "source": "curated",
                    }
                )

    for b in BUCKETS:
        ai_sents = harvest(ai_corpus, b["ai_patterns"], limit=25)
        hu_sents = harvest(hu_corpus, b["human_patterns"], limit=25)
        bank["buckets"].append(
            {
                "id": b["id"],
                "meaning": b["meaning"],
                "ai_examples": ai_sents,
                "human_examples": hu_sents,
            }
        )
        # cross product sample (bounded)
        for a in ai_sents[:8]:
            for h in hu_sents[:5]:
                pairs.append(
                    {
                        "meaning": b["meaning"],
                        "ai_expr": a,
                        "human_expr": h,
                        "source": "harvested",
                    }
                )

    # dedupe
    seen = set()
    uniq = []
    for p in pairs:
        key = (p["ai_expr"], p["human_expr"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)

    random.Random(42).shuffle(uniq)
    bank["replacement_pairs"] = uniq
    bank["stats"] = {
        "pair_count": len(uniq),
        "bucket_count": len(bank["buckets"]),
        "ai_source_count": len(ai_side),
        "human_source_count": len(human_side),
    }

    out = OUT / "ai_human_phrase_bank.json"
    out.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(bank["stats"], ensure_ascii=False))
    print("wrote", out)


if __name__ == "__main__":
    main()
