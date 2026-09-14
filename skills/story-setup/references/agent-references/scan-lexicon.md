# 扩展扫描词表（成簇）

**扫描器用，禁止盲替换。** 成簇、伤阅读再修；故意保留记入报告 `[需复核]`。

完整一级/二级禁用词与毒句式仍以 [banned-words.md](banned-words.md) 为准。本文件补齐公文/黑话/装腔/EN/泄漏等 banned-words 未收录的扫描簇（来自 novel-write-produce `anti-ai-lexicon`）。

## 扫描层级

| Tier | 含义 | 处理 |
|------|------|------|
| 1A | 极强 AI 标记 / 泄漏 markup | 命中即处理 |
| 1B | 高频套话 | 成簇或同段多命中再处理 |
| 2 | 语境依赖 | 需结构信号 |
| 3 | 弱信号 | 仅与其它弱信号叠加时处理 |

## ZH · 开场 / 共识（1B）

在当今时代、随着…的发展、在这个…的时代、众所周知、不言而喻、毋庸置疑、在…浪潮中、当我们谈论…的时候

## ZH · 连接 / 八股（1B）

不可否认、值得注意的是、需要指出的是、总而言之、综上所述、概括而言、换言之、换句话说、基于以上、在此基础上、接下来让我们、再者、一方面…另一方面…、不仅如此、更重要的是、从某种意义上说、客观来讲、坦白说、本质上

## ZH · 程度 / 虚壳（2–3）

非常、十分、极其、相当、特别、格外、真的、确实、的确、实在、一种、某种、一定的、相应的、一定程度上、值得关注的是、必须承认、让我们正视、需要明白的是

> 短文旁路：每千字「非常/十分/其实/进行/一种」合计倾向 ≤3（见 story-deslop `shortform-sidepath.md`）。小说按成簇与密度，不硬套千字配额。

## ZH · 名词化（1B）

进行优化、做出选择、实现突破、采取措施、起到作用、加以改进、给予支持、提供保障、开展工作、完成交付

## ZH · 排比 / 升华 / 黑话（1B）

是…，是…，更是…；既要…又要…还要…；这，就是…的力量；唯有…方能…；让我们一起；迈向新征程  
赋能、底层逻辑、闭环、抓手、共鸣、沉淀（空用）、跑通、复盘、拉齐、收敛、发散、辐射、引爆、撬动、加持、颗粒度、心智、链路、漏斗、增长飞轮、信息差、认知差、势位、深度链接

> 「底层逻辑」等若出现在**题材设定/力量体系**专名语境，按白名单或 C 级禁动保留，不因本表误删。

## ZH · 翻译腔 / 书面壳（2）

这是一个…的事情；「的」字堆叠；其/该/此（空指）；予以；对于…而言；就…来说；在…方面；当…时（机械前置）

## ZH · 假范围（1B）

从 X 到 Y（X/Y 并非真实尺度或清单时）

## ZH · 抒情装腔（2 · 给抽象概念穿衣时）

安放、抵达、微光、褶皱、滚烫、剥开

## EN · common slop（1B）

delve, tapestry, landscape(抽象), pivotal, underscore, crucial, vibrant, nestled, testament, furthermore, moreover, in conclusion, it's important to note, unlock, elevate, foster, leverage, seamless, robust, cutting-edge, game-changer, harness, multifaceted, at the end of the day, Let's dive in, Here's the thing, Not X but Y（机械时）

## EN · structure tells（2）

Binary contrast stacks; dramatic one-line graf spam; rhetorical setup→list→moral; inanimate agency; Wh- opener streaks; meta-joiners

## EN · P0 leakage（1A · 立即删 markup）

`citeturn`、`contentReference`、`oai_citation`、`utm_source=chatgpt` 等聊天泄漏标记——**删标记，不编造引用**。

## How to apply

1. 先扫 [banned-words.md](banned-words.md) 一级/二级与毒句式。
2. 再按本表 Tier 检索；计簇，单次弱命中常可留。
3. 小说用场景化改写；短文用直陈/具体事实。
4. 故意保留记入报告。
