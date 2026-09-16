# -*- coding: utf-8 -*-
"""Replace person names with {xx} in human_expr / human_top only.

Touches ONLY:
  - ai_to_human_replacements.json → pairs[].human_expr, buckets_summary[].human_top[]
  - ai_human_phrase_bank.json → replacement_pairs[].human_expr

Does NOT touch ai_*, replace_with, human_examples, curated human[], etc.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

OUT = Path(r"e:\oh-story-claudecode\book\_analysis")
REPL_PATH = OUT / "ai_to_human_replacements.json"
BANK_PATH = OUT / "ai_human_phrase_bank.json"

SURNAMES = set(
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍却璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓"
)

# Never treat these as names (whole token)
BLOCK = {
    "空气", "元帅", "左手", "右手", "双眼", "方向", "满是", "余光", "明镜", "明元",
    "然后", "但是", "因为", "所以", "如果", "虽然", "只是", "还是", "就是", "不是",
    "而是", "以及", "或者", "关于", "对于", "通过", "进行", "表示", "出现", "发生",
    "成为", "他们", "她们", "自己", "什么", "这个", "那个", "一个", "没有", "已经",
    "可以", "知道", "感觉", "发现", "突然", "立刻", "马上", "开始", "继续", "起来",
    "下来", "过来", "过去", "出来", "进去", "回来", "离开", "到达", "进入", "走向",
    "看着", "听到", "想到", "觉得", "认为", "强压", "强撑", "强笑", "勾唇", "徐地",
    "全员", "后大", "从面", "从震", "怀的", "孔猛", "孔微", "孔骤", "明缓", "那一",
    "能会", "向他", "向她", "王嘴", "李知", "路都", "宁淡", "王的", "金手指",
    "国王", "王后", "王子", "公主", "市长", "县长", "局长", "书记", "主任", "老师",
    "先生", "小姐", "老板", "师傅", "师兄", "师姐", "师弟", "师妹", "道友", "前辈",
    "同学", "同事", "朋友", "家人", "父亲", "母亲", "儿子", "女儿", "老公", "老婆",
    "丈夫", "妻子", "兄弟", "姐妹", "叔叔", "阿姨", "爷爷", "奶奶", "外公", "外婆",
    "东西", "事情", "问题", "时候", "地方", "样子", "声音", "脸色", "眼神", "目光",
    "心里", "心中", "脑海", "胸口", "肩膀", "手指", "拳头", "脚步", "身影", "气息",
    "瞬间", "转眼", "忽然", "猛地", "缓缓", "微微", "轻轻", "悄悄", "暗自", "不禁",
    "竟然", "仿佛", "宛如", "如同", "似乎", "好像", "可能", "大概", "或许", "也许",
    "终于", "果然", "居然", "简直", "几乎", "完全", "彻底", "真正", "其实", "原来",
    "现在", "刚才", "今天", "明天", "昨天", "早上", "晚上", "夜里", "白天", "此时",
    "此刻", "当时", "随后", "接着", "于是", "因此", "不过", "可是", "然而",
    "而且", "并且", "同时", "另外", "此外", "总之", "再说", "况且", "何况", "除非",
    "无论", "不管", "尽管", "即使", "哪怕", "只要", "只有", "以免", "以便",
    "以来", "以后", "以前", "以上", "以下", "以内", "以外", "之间", "之中", "之外",
    "左右", "上下", "前后", "内外", "大小", "多少", "长短", "高低", "远近", "深浅",
    "力量", "能力", "实力", "气势", "威压", "压迫", "气氛", "氛围", "环境", "场面",
    "系统", "面板", "提示", "任务", "奖励", "经验", "等级", "属性", "技能", "装备",
    "年轻人", "上位者", "一段时间", "段时间", "太子爷", "卫生舱", "平衡感",
    "太搞笑", "别好看", "别社死", "人勿近", "人说话", "人骂娘", "人阻拦",
    "东西吃", "从面前", "向王扬", "万大洋", "上发烧", "人更快", "人承认",
    "养不良", "况给你", "后释怀", "子他妈", "安还没", "容置疑", "师圈里",
    "张好看", "强手下", "扶贫啊", "时不怎", "时候也", "南洋去",
    "真人", "真人吗", "时间", "时候", "方面", "面前", "之后", "之前",
    "之后", "之间", "之中", "之上", "之下", "之内", "之外",
    "马上下", "马上就", "马上要", "马上能",
    "黄金", "金光", "银光", "雷击", "仙人", "棺材", "麻将", "桌子",
    "办公室", "公司", "学校", "医院", "国家", "世界", "游戏", "系统",
}

TITLE_SUFFIX = (
    r"(?:局长|县长|市长|书记|主任|总裁|董事长|经理|总|哥|姐|叔|婶|爷|奶|"
    r"先生|小姐|老师|教授|医生|警官|队长|班长|少爷|夫人|同志|"
    r"师兄|师姐|师弟|师妹|道友|前辈|老板|师傅|大人|陛下|殿下|公子|瘸子)"
)

# Stronger agent context — must look like a person acting
AGENT_AFTER = (
    r"(?:的[嘴瞳眉眼心脑脸手腿脚]|瞳孔|眉头|嘴角|脸色|眼神|目光|心中|心里|脑海|胸口|"
    r"深吸|缓缓|猛地|微微|下意识|转头|抬头|点头|摇头|站起|"
    r"愣|一愣|一缩|骤缩|瞬间|很快|"
    r"开口|说道|沉声|冷笑|怒道|喊道|问道|答道|叹道|骂道|接话|"
    r"看着|看了|望向|盯着|瞪了|瞥了|扫了|"
    r"感到|发现|意识到|不由|忍不住|反应过来|清醒|"
    r"行了一礼|点了点头|摇了摇头|吸了一口|叹了口气|笑了|哭了|"
    r"道[：:“\"「]|说[：:“\"「]|问[：:“\"「]|喊[：:“\"「])"
)

# Left boundary: start / punct / whitespace / quote
LEFT_OK = r"(?:^|[，,。！？!?:：；;、“\"「『（\(\s【])"

GIVEN_BAD = set("的了着过得地么们一二三四五六七八九十百千万亿上下前后内外")

# Seed: confirmed novel character names from this corpus
SEED_NAMES = [
    "谢柠", "钟临", "马小帅", "陈长生", "李学文", "沈湄", "许博", "龚煜",
    "周浩", "罗子君", "秦风", "陈景承", "李念生", "柳清", "岑厌",
    "沈思晴", "温苓", "李素梅", "顾明月", "齐原", "霍云铮",
    "王建国", "李家胜", "雷克斯", "陆沉", "陆霆锋", "白野", "林韵",
    "程友善", "凌昭", "陈志远", "叶潇", "穆谣", "陆泽", "杨逸", "沈曼妮",
    "张桂兰", "叶七言", "周海波", "穆宁", "左星河", "李安平", "左皇",
    "向骑", "一休", "王蛇", "谭杰", "李瘸子", "凌玲", "李飞图",
    "韩局长", "李县长", "王书记",
    "苏夜", "陈闲", "夏雨谣", "贺平生", "谢穗安", "张大彪", "王扬",
    "李建成", "陈怀安", "陆非", "李佑林", "李国强", "陈岩石",
    "林英",
    "江绮遇", "祁逾", "方叙白", "姜眠", "陆珩",
    "宋时安", "林晓", "许澈",
    "谢弥", "沈爅卿", "萧景析", "许霜绒", "柳沃星", "谢涟", "谢政德",
    "沈晚宁", "周晏", "陆昭", "顾衡",
    "钟嘉嘉", "张耀祖", "周薄森", "吴伟", "江晨",
]


def _ok_given(g: str) -> bool:
    if not g or any(c in GIVEN_BAD for c in g):
        return False
    if g in BLOCK:
        return False
    # reject given names that are common content words
    if g in {
        "时间", "时候", "方面", "面前", "之后", "之前", "之间", "之中",
        "好看", "搞笑", "发烧", "释怀", "承认", "说话", "阻拦", "骂娘",
        "勿近", "更快", "置疑", "圈里", "手下", "还没", "他妈", "洋",
        "不良", "给你", "社死", "大洋",
    }:
        return False
    return True


def harvest_names(texts: list[str]) -> list[str]:
    surname_cls = "".join(sorted(SURNAMES))
    # Require left boundary + name + strong agent after
    pat = re.compile(
        LEFT_OK
        + "(?P<name>["
        + surname_cls
        + "][\u4e00-\u9fff]{1,2})"
        + "(?:"
        + TITLE_SUFFIX
        + ")?"
        + "(?="
        + AGENT_AFTER
        + ")"
    )
    cnt: Counter[str] = Counter()
    for t in texts:
        if not t:
            continue
        for m in pat.finditer(t):
            name = m.group("name")
            if name in BLOCK or not _ok_given(name[1:]):
                continue
            cnt[name] += 1

    names: set[str] = set()
    for n, c in cnt.items():
        if c >= 4 and n not in BLOCK:
            names.add(n)
        elif len(n) >= 3 and c >= 2 and n not in BLOCK:
            names.add(n)

    for s in SEED_NAMES:
        if s in BLOCK or len(s) < 2:
            continue
        names.add(s)
        base = re.sub(TITLE_SUFFIX + r"$", "", s)
        if base and base != s and base not in BLOCK and len(base) >= 2:
            names.add(base)

    # Drop anything that is a substring of a blocked common phrase
    # (except when the blocked phrase IS the name itself)
    drop = set()
    for n in names:
        for b in BLOCK:
            if len(b) > len(n) and n in b:
                drop.add(n)
                break
        # also drop ultra-generic 2-char that are mostly false positives
        if n in {"后人", "别人", "有人", "无人", "众人", "两人", "三人", "个人", "主人", "敌人"}:
            drop.add(n)
    names -= drop

    return sorted(names, key=lambda x: (-len(x), x))


def replace_names(text: str, names: list[str]) -> str:
    """Allowlist replace: longest names first. Titles glued to name → whole → {xx}."""
    if not text or not names:
        return text
    out = text
    for name in names:
        if name not in out:
            continue
        parts = re.split(r"(\{xx\})", out)
        rebuilt = []
        for part in parts:
            if part == "{xx}":
                rebuilt.append(part)
                continue
            # If name already includes title (韩局长), plain replace
            # Else: name+title suffix → {xx} (drop title into placeholder slot)
            if re.search(TITLE_SUFFIX + r"$", name):
                part = part.replace(name, "{xx}")
            else:
                part = re.sub(
                    re.escape(name) + "(?:" + TITLE_SUFFIX + ")?",
                    "{xx}",
                    part,
                )
            rebuilt.append(part)
        out = "".join(rebuilt)
    return out


def collect_human_texts(repl: dict, bank: dict) -> list[str]:
    texts: list[str] = []
    for p in repl.get("pairs", []):
        texts.append(p.get("human_expr", ""))
    for b in repl.get("buckets_summary", []):
        texts.extend(b.get("human_top") or [])
    for p in bank.get("replacement_pairs", []):
        texts.append(p.get("human_expr", ""))
    return texts


def apply(repl: dict, bank: dict, names: list[str]) -> dict:
    stats = {
        "pairs_human_expr": 0,
        "buckets_human_top": 0,
        "bank_human_expr": 0,
    }

    for p in repl.get("pairs", []):
        old = p.get("human_expr", "")
        new = replace_names(old, names)
        if new != old:
            p["human_expr"] = new
            stats["pairs_human_expr"] += 1

    for b in repl.get("buckets_summary", []):
        tops = b.get("human_top")
        if not tops:
            continue
        new_tops = []
        changed = False
        for t in tops:
            new = replace_names(t, names)
            if new != t:
                changed = True
                stats["buckets_human_top"] += 1
            new_tops.append(new)
        if changed:
            b["human_top"] = new_tops

    for p in bank.get("replacement_pairs", []):
        old = p.get("human_expr", "")
        new = replace_names(old, names)
        if new != old:
            p["human_expr"] = new
            stats["bank_human_expr"] += 1

    return stats


def sanity_check(repl: dict, bank: dict) -> list[str]:
    """Flag suspicious over-replacements."""
    bad_patterns = [
        r"一\{xx\}",  # likely 一段时间
        r"真\{xx\}",  # likely 真人吗
        r"年\{xx\}",
        r"\{xx\}说话",
        r"\{xx\}时候",
        r"住一\{xx\}",
    ]
    issues = []
    samples = []
    for p in repl.get("pairs", []):
        s = p.get("human_expr", "")
        samples.append(s)
    for b in repl.get("buckets_summary", []):
        samples.extend(b.get("human_top") or [])
    for p in bank.get("replacement_pairs", []):
        samples.append(p.get("human_expr", ""))
    for s in samples:
        for pat in bad_patterns:
            if re.search(pat, s):
                issues.append(s[:80])
                break
    return issues[:20]


def main() -> None:
    repl = json.loads(REPL_PATH.read_text(encoding="utf-8"))
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))

    texts = collect_human_texts(repl, bank)
    names = harvest_names(texts)
    print(f"lexicon size: {len(names)}")
    print("names:", ", ".join(names))

    stats = apply(repl, bank, names)
    print("stats:", stats)

    issues = sanity_check(repl, bank)
    if issues:
        print("SANITY ISSUES (first 20):")
        for i in issues:
            print(" ", i)
        raise SystemExit("Aborting write due to sanity issues — tighten lexicon")

    note = "human_expr/human_top 中人名已统一为 {xx}，去味时按书中角色回填"
    if note not in (repl.get("usage") or ""):
        repl["usage"] = (repl.get("usage") or "") + "；" + note

    meta = bank.get("meta") or {}
    meta["name_placeholder"] = "{xx}"
    meta["name_placeholder_note"] = (
        "仅 human_expr（及 replacements.buckets_summary.human_top）中的人名已换成 {xx}；"
        "去 AI 味选用人味句后，按本书 设定/角色 回填"
    )
    bank["meta"] = meta

    REPL_PATH.write_text(
        json.dumps(repl, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    BANK_PATH.write_text(
        json.dumps(bank, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    previews = []
    for p in repl["pairs"]:
        if "{xx}" in p.get("human_expr", ""):
            previews.append(("pair", p["ai_expr"][:30], p["human_expr"]))
            if len(previews) >= 8:
                break
    for b in repl.get("buckets_summary", []):
        for t in b.get("human_top") or []:
            if "{xx}" in t:
                previews.append(("top", "", t[:90]))
                if len(previews) >= 14:
                    break
        if len(previews) >= 14:
            break
    print("previews:")
    for kind, ai, hu in previews:
        print(f"  [{kind}] {ai} => {hu}")


if __name__ == "__main__":
    main()
