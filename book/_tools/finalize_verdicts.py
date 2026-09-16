# -*- coding: utf-8 -*-
"""Final triage: relative ranking + qualitative overrides from ch1 reading."""
from __future__ import annotations

import json
import re
from pathlib import Path

BOOK_DIR = Path(r"e:\oh-story-claudecode\book")
OUT = BOOK_DIR / "_analysis"

# 基于开篇精读的人工覆盖（优先于纯分数）
# ai = 说明腔/光滑同质更明显；mixed = 套路重但有人味；human = 口语黑话毛边明显
OVERRIDES = {
    # —— 更偏 AI / 高光滑模板 ——
    "万界沦为游戏，拜神不如拜我.txt": (
        "ai",
        "开篇描写偏文学润色（暗红色罗盘、渗落血珠、背脊发寒），系统规则排比整齐，内心推理完整顺滑，人味毛边少。",
    ),
    "不会踢球？却成了足球巨星！.txt": (
        "ai",
        "解说/背景说明腔重，情绪与场面推进过齐，穿越反应也偏规整，缺少网文口语毛刺。",
    ),
    "内卷猝死后，我在海洋求生当大佬.txt": (
        "ai",
        "开篇人设介绍+规则面板完整说明，叙述匀速顺滑，吐槽力度弱，典型求生文模板腔。",
    ),
    "序列：升华.txt": (
        "mixed",
        "列车规则说明整齐，但有口语吐槽（熬夜猝死下地狱）；整体仍偏系统文模板。",
    ),
    "公路求生：开局抽中旅游餐车.txt": (
        "mixed",
        "前男友梗/便秘梗很有人味，但载具外观大段工业风描写偏光滑模板。",
    ),
    "恐怖大航海.txt": (
        "mixed",
        "分数偏高且模板词密；待结合后文，先归混合。",
    ),
    "这难道不是乙女游戏？.txt": (
        "mixed",
        "仿佛/似乎密度高，叙述较润；女频求生也有口语，归混合。",
    ),
    "还木筏求生呢？我幽灵船上吃烤肉.txt": (
        "mixed",
        "模板反应词（仿佛/竟然）密度高，同时有吐槽，归混合。",
    ),
    "游戏入侵：你个厨子怎么变城主了.txt": (
        "mixed",
        "开篇偏说明+系统，节奏齐；标题口语强，正文需当混合语料。",
    ),
    "求生游戏：我有一座花朵安全屋.txt": (
        "mixed",
        "系统投放+规则说明齐整，聊天频道有人味，归混合。",
    ),
    "求生游戏：每天一个滑跪小技巧.txt": (
        "mixed",
        "标题人味足，正文易走技巧说明腔，归混合。",
    ),
    "求生：从小木屋开始抵御寒流.txt": (
        "mixed",
        "求生开局说明型叙述常见模板感。",
    ),
    "淡人也可以登顶求生游戏吗.txt": (
        "mixed",
        "人设说明较完整顺滑，淡人口吻若统一则偏模板。",
    ),
    "猫耳萝莉抡大锤，你这么求生的？.txt": (
        "mixed",
        "标题炸裂，正文求生描写易光滑；作混合语料。",
    ),
    "万人迷救世主以为自己是万人嫌.txt": (
        "mixed",
        "短句干脆有个性，但世界意识对话偏说明；人味>纯AI，归混合。",
    ),
    # —— 明显更偏人工 ——
    "CS：每回合必杀一个能打职业吗.txt": (
        "human",
        "CS黑话/直播弹幕/短句爆破强，年龄焦虑与网吧细节毛边足。",
    ),
    "三角洲：这野人魔了，是个魔王！.txt": (
        "human",
        "宿舍麦、跑刀梗、嘉豪/牢大等圈层黑话自然，作者夹注也像真人。",
    ),
    "国运三角洲，开局航天堵桥.txt": (
        "human",
        "三角洲梗密度极高，对白吵闹重复有网感，非光滑AI腔。",
    ),
    "武侠网游，开局三个神级词条.txt": (
        "human",
        "男频新书榜头部，打斗对白粗粝，词条爽文但仍有口语冲劲。",
    ),
    "联盟：在全神ig，我会拦住T1.txt": (
        "human",
        "电竞圈层与赛事梗驱动，对白偏玩家口吻。",
    ),
    "网游：神级盗贼，我即是无法无天.txt": (
        "human",
        "盗贼流口语与嚣张对白，毛边多于润色。",
    ),
    "王者：破防就变强？那我不当人了.txt": (
        "human",
        "破防梗驱动，情绪直给，非说明文腔。",
    ),
    "开局光击球，你说这是网球？.txt": (
        "human",
        "体育细节与对白更像作者在写比赛，而非空转描写。",
    ),
    "诸神游戏：你们管大圣叫吗喽？.txt": (
        "human",
        "梗标题+吐槽口吻强。",
    ),
    "全息游戏当神偷，偷完他的偷你的.txt": (
        "human",
        "脏话/省略毛边密度高，短句多。",
    ),
    "开局属性拉满，三角洲第一武将.txt": (
        "human",
        "三角洲黑话与嚣张对白明显。",
    ),
    "退游六年，剑仙老婆现实找上门了.txt": (
        "human",
        "日常对白与情绪毛刺多于光滑叙事。",
    ),
}


def load_scores():
    return json.loads((OUT / "verdicts.json").read_text(encoding="utf-8"))["books"]


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
    scored = {b["file"]: b for b in load_scores()}
    files = sorted(p.name for p in BOOK_DIR.glob("*.txt") if not p.name.startswith("_"))

    # relative: top 25% by score without override -> mixed candidate
    ranked = sorted(scored.values(), key=lambda x: -x["ai_score"])
    top_cut = {r["file"] for r in ranked[:10]}

    final = []
    for f in files:
        base = scored[f]
        if f in OVERRIDES:
            verdict, reason = OVERRIDES[f]
        elif f in top_cut and base["ai_score"] >= 1.0:
            verdict, reason = (
                "mixed",
                "相对分数靠前（模板词更密），开篇未单独精读覆盖，暂归混合待用。",
            )
        else:
            verdict, reason = (
                "human",
                "口语/黑话/短句或分数偏低；作人工语料侧。",
            )
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

    # ensure at least some ai if overrides provided
    by = {"ai": [], "mixed": [], "human": []}
    for it in final:
        by[it["verdict"]].append(it)

    disclaimer = (
        "> **用途**：语料分流（AI痕迹对照 / 人味表达抽取），**不是**作者实锤鉴定。\n"
        "> **方法**：开篇精读覆盖 + 启发式相对分。`ai`=光滑说明腔更明显；`mixed`=套路重但有人味；`human`=口语黑话毛边更明显。"
    )

    payload = {
        "disclaimer": "triage for phrase mining, not authorship claim",
        "counts": {k: len(v) for k, v in by.items()},
        "books": sorted(final, key=lambda x: (x["verdict"] != "ai", x["verdict"] != "mixed", -x["ai_score"])),
    }
    (OUT / "verdicts_final.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # also rewrite simple lists expected by workflow
    (OUT / "ai_books.md").write_text(
        md_table("疑似 AI / 高光滑模板书单", by["ai"], disclaimer), encoding="utf-8"
    )
    (OUT / "mixed_books.md").write_text(
        md_table("混合 / 高套路书单", by["mixed"], disclaimer), encoding="utf-8"
    )
    (OUT / "human_books.md").write_text(
        md_table("更偏人工书单", by["human"], disclaimer), encoding="utf-8"
    )

    # flat name lists
    (OUT / "ai_books.txt").write_text(
        "\n".join(x["file"] for x in by["ai"]) + "\n", encoding="utf-8"
    )
    (OUT / "human_books.txt").write_text(
        "\n".join(x["file"] for x in by["human"]) + "\n", encoding="utf-8"
    )
    (OUT / "mixed_books.txt").write_text(
        "\n".join(x["file"] for x in by["mixed"]) + "\n", encoding="utf-8"
    )

    print(json.dumps(payload["counts"], ensure_ascii=False))
    print("AI:", [x["file"] for x in by["ai"]])
    print("MIXED:", [x["file"] for x in by["mixed"]])
    print("HUMAN count:", len(by["human"]))


if __name__ == "__main__":
    main()
