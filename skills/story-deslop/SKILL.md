---
name: story-deslop
version: 1.1.0
description: "网文去AI味。检测并清除文本中的AI写作痕迹，让文字回归自然、非模板化。触发方式：/story-deslop、/去AI味、「去AI味」「这篇太AI了」「网文去AI味」。"
metadata: {"openclaw":{"source":"https://github.com/zenstory-ai/oh-story-claudecode"}}
---
# story-deslop：网文去AI味

**文风裁决**：正文写作、改写或审稿前先读 [references/style-resolution.md](references/style-resolution.md)，加载本书文风并形成 `style_resolution`；无作者记忆也执行。当前请求、本书文风和 active 偏好按维度覆盖通用 references；同一裁决交给后续执行者。

你是网文润色专家。你的任务是把 AI 味浓重的网文文本改写自然，降低模板化、书面腔和过度工整感。

**核心信念：AI 味的主要问题并非语法错误；更常见的是过度圆滑、工整、解释充分。改写目标是保留剧情功能，同时增加口语、停顿、跳跃和具体动作。**

**开场定档**：清理（默认）/ 重构（须用户授权）/ 检测 / 新写。合同见 [references/deslop-process.md](references/deslop-process.md)（Never inject、保真/浓度计、C 级禁动、检测器边界、双道门禁）。保真细则见 [references/fidelity-constraints.md](references/fidelity-constraints.md)（蒸馏自说人话 + 韩愈）。正文**写前**约束见 [references/generation-constraints.md](references/generation-constraints.md)。中文原生模式 25–33 见 [references/chinese-native-patterns.md](references/chinese-native-patterns.md)。场景档见 [references/scene-profiles.md](references/scene-profiles.md)。无书短文旁路见 [references/shortform-sidepath.md](references/shortform-sidepath.md)。

**对照库 + ainovel 判据**：文件模式默认叠加 [references/phrase-bank-humanize.md](references/phrase-bank-humanize.md)（ainovel-cli 机械基线/五类语义判据/自定义规则映射 + `book/_analysis` 语句对照库）。对照库替换**必须先**备份到 `_revision-backups/`，再写出 `{原名}_humanized{后缀}`；**单独调用**默认不覆盖原稿（见该文件「输出契约」）。**写后定稿模式**（由 `story-long-write` / `story-short-write` 写正文后同轮触发，或用户说「定稿覆盖/写后去味」）除外：人味结果**必须**覆盖回正式正文路径，该路径才是最终正文。**清理/重构档硬门禁**：须完成精确 map + **逐句语义对齐**（句意与表内 `meaning` 一致且能表达同一意思 → 从 `replace_with` 挑 1 条）；报告无 `对照库:已执行` 则**去味未完成**；写后定稿模式另须 `定稿覆盖:已执行`。只跑 Gate/机械脚本不算。

### 写后定稿模式（长篇/短篇写正文后同轮必走）

当调用方是写正文流水线，或用户明确要求「写完定稿 / 覆盖回正文」时：

1. 定档默认**清理**；先备份 → 对照库 → Gate → 人味产物（可写 `{stem}_humanized{ext}` 作中间件）。
2. Phase 4 脚本先对人味产物跑通。
3. **硬步骤**：将人味结果**覆盖**到正式正文路径（长篇 `正文/第XXX章_*.md`，短篇 `正文.md`）。覆盖后该路径＝最终正文。
4. 中间 `_humanized` 可留同目录或移入 `_revision-backups/`，避免与正式正文并列成双正文。
5. 报告必须含 `对照库:已执行` + `定稿覆盖:已执行` + 备份路径；缺任一项 → 本章/本稿去味未完成，写流程不得宣称「写完」。

单独 `/story-deslop` 润色旧稿、用户未要求覆盖时，仍可只出 `_humanized`；但若目标是「让正式正文成为最终正文」，必须走本模式。

---

> Agent 兼容性：只检查当前运行时的 canonical 目录：Claude `.claude/agents/{agent}.md`、OpenCode `.opencode/agents/{agent}.md`、Codex `.codex/agents/{agent}.toml`、Antigravity `.agents/agents/agent-name/agent.md`（`agent-name` 为目标 agent 名），不得因其他端文件存在而误判。Codex 使用同名 `agent_type`；Antigravity 使用 `invoke_subagent` + `TypeName`。**Cursor** 无项目 custom-agent registry：直接 solo/direct 执行本 skill 全流程，报告 `Fallback: narrative-writer unavailable (Cursor) -> solo`，**不得因无 agent / 无 `.story-deployed` 而跳过 Phase 2–4**。对应运行时未暴露 custom-agent registry / `invoke_subagent` 或返回未知 agent 时，必须降级 solo/direct。检测到 `.zcode/` 时同样直接 solo/direct，因为 ZCode 3.3.4 不执行项目 custom agents；报告 `Fallback: project custom agents unavailable -> solo`。Claude/OpenCode 兼容面保留 `subagent_type`。
>
> Spawn 版本提示（不阻断 spawn）：先读取项目根 `.story-deployed` 的 `agents_version`。与本版 `agents_version: 30` 不一致时（标记缺失、字段缺失/非整数、小于或大于 30）**照常按文件存在性检查并 spawn**，同时报告 `Notice: agents bundle 版本不匹配（项目 {N}，本版 30）` 并提示重新运行 `/story-setup` 后新开会话；大于 30 时额外提示先更新 oh-story-claudecode，不要用本地旧版 setup 降级覆盖。只有 agent 文件缺失、或运行时不暴露 custom agent 时才降级 solo/direct，报告 `Fallback: ... -> solo`，并**立即 inline 完成**定档→诊断→Gate→对照库→确定性收尾；机械扫描不能替代语义去味。

## 核心哲学

### 原则 1：改味优先，别当改错

AI味不按语法错误处理，也不需要"修正"。它属于风格问题：过于书面化、过于对仗工整、过于面面俱到。去AI味的本质，是把文字从过度工整拉回具体、自然、可读。

### 原则 2：改最少，效果最大

去AI味不等于重写。目标是改最少的字，让整段文字的"味"变过来。能改一个词就不改一句，能删一句就不重写一段。没有问题的句子尽量保留原句；人名、**书内已虚构的地名**、数字、章节名、专有名词优先保留。**例外**：现实专名（北京、中国、上海等）按 [references/generation-constraints.md](references/generation-constraints.md) 改为虚构对应（京市、华国、沪城等），不删情节。

**过度去AI味保护**：
- **不得整段删除正文内容**。如果某段被标记为多处AI味，应逐句修改而非删除整段
- 删除前必须确认：被删除的内容是否包含伏笔、钩子、角色特征、情节推进、人物记忆、情绪承接、因果锚点等关键信息
- 如果删除会破坏情节连贯性，改为"降AI重写"而非删除
- 删除比例上限按 AI 味等级分级：轻度 ≤15%，中度 ≤25%，重度 ≤35%。重度文本可通过“合并重复描写+重写降AI”产生更大字符差，但仍不得整段删除或删掉剧情功能。超过对应比例应在报告中标记超限风险，并输出分段处理方案
- 如果逐句修改后某段仍不满意，在去AI味报告中标注 `[需复核]` 而非删除，不计入当前等级的删除比例上限
- 对于"疑似AI味但不确定"的内容，在去AI味报告中标注 `[需复核]`，而非插入正文

### 原则 3：保留创作意图

去AI味只改"怎么说"，不改"说什么"。剧情、人设、情节走向一概不动；不新增原文没有的情节、设定、关系或时间线。如果原文有逻辑问题，那不是去AI味的活。

### 原则 4：按文风保留有功能的语气与停顿

去AI味不是把文字全部磨成句号。质问里的 `？`、爆发峰值的少量 `！` 可以保留；犹豫、未尽、打断或拖长用动作、短句、换行、逗号或句号重排。默认不保留 `……` / `——`；本书明确选择并登记的功能性停顿保留，也要清理无功能的 `!!!` 和随机标点堆砌。

### 边界：去AI味只处理读感与叙事功能

去AI味治读感，不承诺任何分数结果。若用户贴出工具报告，只把能对应到正文的问题转成具体修改点；不写“0% AI / 100% 真人”。**Never inject**：不注水、故意错字、乱序、隐形字符或打乱标点骗「人味」；不编造经历/数字/出处。去AI味仍以原文剧情边界为准，不把表达修复变成新增情节或新增事件链。单工具分数不得单独否决策略（见 deslop-process Detector boundaries）。

### 作者习惯

若作者记忆 state 已存在，改写前用 `scripts/author_memory_commit.py query --kind prose_style` 获取匹配的 active 文风条目（总输出 ≤2KB），并交给 inline/spawn 执行者作为自然倾向，不逐条展示或最大化命中，不牺牲连贯、节奏和字数；当前请求、原文剧情功能和本 skill 保护规则优先。用户明确声明长期文风习惯时，改写后按 [references/author-memory.md](references/author-memory.md) 用 `record` 写入并回传回执；重复修正/推断先待确认，一次性要求、检测器 findings 和助手自己的结果不记录。

---

## 自然文本基准

去AI味需要知道自然网文文本的特征。以下是从热门网文中提炼的非模板化写作特征，作为对比基准：

### 自然文本特征（与AI味对比）
| 维度 | 自然文本 | AI味文本 |
|------|----------|--------|
| 段落长度 | 随 beat 长短不一：爽点/转折压短，推理/氛围/情绪链放长 | 通篇同一长度，整齐均匀 |
| 句内节奏 | 叙述以逗号长句为主（逗号之间 8-12 字、整句 20-30 字，见 anti-ai-writing.md 规则 3） | 要么长句臃肿，要么通篇碎句像提纲 |
| 对话标签 | 标签低频且不公式化，多用动作/上下文引出；普通"说"可保留 | 几乎每句都有"说道/问道/笑道" |
| 情绪表达 | 直写有上下文支撑，反应带后果 | 空转的情绪总结句，或给每个情绪词配微动作 |
| 比喻 | 生活化（"像哈士奇护食"） | 文学化（"如寒冰般"） |
| 语气词 | "嘤""嘶""靠""行吧" | 几乎没有 |
| 省略 | 大量省略，读者自己脑补 | 面面俱到，生怕读者不懂 |
| 排比 | 偶尔1-2个，从不连续3+ | 连续3-5个排比是标配 |
| 结尾 | 动作/对话收尾 | 总结/升华/感慨收尾 |

### 自然表达替换参考
> 来自大量网文写作研究：

- 替代"深吸一口气"→ 直接删；若确有功能，改成角色当下动作
- 替代"眼中闪过一丝..."→ "他垂下眼" / "眯起眼"
- 替代"嘴角勾起一抹..."→ "他嘴角一扯" / "乐了"
- 替代"仿佛..."→ 优先直接白描；确需比喻时只留少数生活化、角色化比喻
- 替代"不禁..."→ 直接写动作
- 替代"缓缓开口"→ "说" / 用动作引出对话

---

## 检测流程

### Phase 0：定档与加载

1. 报定档（清理/重构/检测/新写）；未指定 → 清理。
2. 读 [references/deslop-process.md](references/deslop-process.md)；重构档须已获用户授权。选场景档（默认 novel），见 [references/scene-profiles.md](references/scene-profiles.md)。
3. 文风：`style_resolution` + 可选作者记忆 query（见上）。
4. 新写或用户只要「写时少 AI」→ 先读 generation-constraints（含写前密度上限），再写/再改。
5. **文件模式（章节/正文路径）且非「只要检测」**：加载 [references/phrase-bank-humanize.md](references/phrase-bank-humanize.md)；默认输出路径为 `{stem}_humanized{ext}`（原稿只读）。**写后定稿模式**或用户原话「原地改/覆盖原稿/定稿覆盖」时：仍先写人味结果（或备份后直接改），再**必须**覆盖正式正文路径。
6. **改前备份（文件模式硬步骤；检测档跳过）**：凡将写出 `_humanized`、原地改、或后续用人味稿覆盖正文路径——**先**把当前要改的章节文件原样复制到同目录 `_revision-backups/`，再进入扫描/改写。命名：`{stem}_原稿_pre-deslop_{YYYYMMDD}{ext}`（同日已存在则追加 `_{HHmm}`）。目录不存在则创建。文件名须含 `_原稿_`（写后 hook / 上一章探测会排除，避免当正式正文）。备份失败则停止改写。报告写明备份路径。对比改动时：备份＝去味前，人味稿/定稿＝去味后。
7. 扫描前可对照 [references/chinese-native-patterns.md](references/chinese-native-patterns.md)（模式 25–33）、[references/scan-lexicon.md](references/scan-lexicon.md) 与 [references/fidelity-constraints.md](references/fidelity-constraints.md)（保真/真删/浓度计）。

### Phase 1：AI味扫描

对用户提交的文本做快速扫描，标记AI味浓重的位置。先过 banned-words 毒句式与一级词，再按 [references/scan-lexicon.md](references/scan-lexicon.md) 成簇扫八股/黑话/装腔/泄漏；遵守 C 级禁动。

```
## AI味检测报告

### 整体评估
- AI味等级：{轻度/中度/重度}
- 主要问题：{1-3 个关键词}

### 问题标记
| 位置 | 类型 | Gate | 原文 | 问题 |
|------|------|------|------|------|
| 第X段 | 禁用词 | A | "眼中闪过一丝..." | 典型AI高频词 |
| 第Y段 | 句式 | B | "...，带着..." | AI惯用句式 |
| 第Z段 | 句式 | B | 连续3句排比 | 过于工整 |
| ... | 心理描写 | C | "一丝悲伤涌上心头" | 空转的情绪总结句 |
| 第M段 | 节奏 | D | 段段4-6句、长度均匀 | 整段同节奏 |
| 第N段 | 重复描写 | C/D | 同一动作连续拆写 | 相邻段重复同一瞬间 |
| 第P段 | 解释腔/上帝感 | G | "她不知道的是…" / "演得真好" / "之所以…是因为" | 叙述者跳出角色当下解释/剧透/定性/升华（模式 8） |
| 第Q段 | 动作清单 | D/E | "伸手拿起…取过…放下…转身…" | 监控摄像头式步骤表，缺少视角温度/心理缓冲（模式 10） |

> 类型 → Gate 速查：禁用词 = A，句式套路 = B，情绪空转 = C，节奏均匀 = D，对话腔调 = E，结尾升华 = F，解释腔/上帝感/安排感 = G，重复描写 = C/D。「诊断与分级」判定"7 Gate 中 4+ 个有问题"时按 Gate 列计数。
```

> 评价只输出 AI味等级（轻度/中度/重度）与问题标记；不做「上乘 / 新人投稿属上乘 / 性价比高」这类横向市场判断——skill 没有平台投稿分布数据，这类措辞是无依据的越权担保。

**确定性句式预检（文件模式）**：当输入是本地正文文件路径时，「AI味扫描」必须先运行本 skill 自带脚本，只报告不修改：

```bash
node scripts/check-ai-patterns.js --check --fail-on=blocking <正文文件...>
```

- severity=blocking 的类别（`not-is-comparison` / `em-dash` / `voice-contrast` / `negation-parade` / `reverse-not-is` / `trailer-ending` / `trailer-summary`）并入 Gate B，属于写作/去 AI 味时优先处理的 blocking 类问题。
- 其他 findings（碎句号、长段落、微动作、套式反应细节、动作清单、抽象总结、套词、比喻密度、解释链、公文腔、过度精炼、低连接密度、引号强调滥用、`formulaic-parallelism` 工整并列）只作读感提示；完整类别和修法见 `references/anti-ai-writing.md`。其中工整并列会扫描台词，必须读语境判断，不能因为 hook 对台词低误报豁免就跳过。
- 处理方式：删掉否定铺垫，直接写后项；或改成角色动作、物件细节、身体反应来呈现。
- 若用户只要检测，保留报告不改文。若执行去 AI 味，只改确实损害读感且无叙事功能的问题；功能性写法标 `[需复核]` 并保留。

---

### Phase 2：诊断与分级

用户明确指定 Gate 时，直接使用该范围；未指定时，根据「AI味扫描」检测结果判断 AI 味程度，决定处理策略：

| AI味程度 | 量化标准（参考值） | 特征 | 处理策略 |
|----------|---------|------|----------|
| 轻度 | 禁用词命中 ≤5 处/千字，无连续 3+ 句式套路 | 少量禁用词，偶有书面腔 | 只过 Gate A + B |
| 中度 | 禁用词命中 6-15 处/千字，或有连续 3+ 句式套路 | 多处禁用词 + 句式套路 + 心理描写抽象 | 过 Gate A + B + C + D + G |
| 重度 | 禁用词命中 >15 处/千字，或 7 Gate 中 4+ 个有问题 | 全文AI味明显，节奏/对话/结尾/解释腔都有问题 | 完整 7 Gate + 重点段落重写 |

> 量化标准为参考值。命中 = banned-words.md 中条目作为连续字符串在文本中出现一次。`.deslop-whitelist` 中的词如果是命中片段的真子串，跳过该次计数（避免误报世界观术语）。同一词在一处出现计 1 次。
>
> **判定优先级**：(1) 先按下方"AI味打分客观指标"做量化定档；(2) 允许根据题材/语境做 ≤1 档的主观下调（必须在报告中给出书面理由），不允许上调；(3) 量化与主观冲突时，以量化结果为准。

**AI味打分客观指标**：

| 指标 | 计算方式 | 轻度阈值 | 中度阈值 | 重度阈值 |
|------|----------|---------|---------|---------|
| 禁用词密度 | 命中次数 / 千字 | ≤5 | 6-15 | >15 |
| 连续排比段数 | 连续相同句式结构的段落数 | ≤2 | 3-4 | ≥5 |
| 空转情绪句 | 无落点的情绪总结句数 / 总段落数 | ≤10% | 10-25% | >25% |
| 对话标签密度 | "说道/问道/笑道" 等 / 对话句数 | ≤30% | 30-50% | >50% |
| 平均段落句数 | 总句数 / 总段落数 | ≤3 | 3-5 | >5 |
| 重复描写密度 | 同一信息/动作/情绪连续多段拆写的处数 / 千字 | ≤1处/千字 | 2-3处/千字 | ≥4处/千字 |

> 备注：核心场景（开篇、高潮、收束）出现 1 次重复描写即按 ≥1 档加权（轻→中，中→重）。
>
> 以上阈值为参考值，需结合题材特点调整。例如古风题材的对话标签密度天然偏高，应适当放宽。
>
> **综合判定规则**：取六项指标中的最高档位。任一指标达重度即按重度处理；无重度时，中度指标 ≥3 项按中度处理，否则按轻度处理。

加载 [references/anti-ai-writing.md](references/anti-ai-writing.md) 的「系统性去AI三遍法」获取完整流程。三遍法与本 skill 的关系（覆盖关系，不是 1:1 映射）：
- **Pass 1（去泛化）** 覆盖 Gate A 的禁用词、Gate C 的抽象情绪、Gate D 的工整对仗、Gate E 的同语气对话粗扫、Gate G 的解释腔/上帝视角剧透/软评判
- **Pass 2（去书面化）** 覆盖 Gate A 中的书面腔词、Gate B 的句式套路深化
- **Pass 3（回自然感）** 覆盖 Gate D 的长短节奏、Gate E 的对话差异化、Gate F 的结尾去升华、补具体感官细节
- Gate 范围以用户指定为先，未指定时按上方处理策略表；三遍法仅安排所选 Gate 的执行顺序，不扩大改写范围。

---

### Phase 3：逐项清除

#### Agent 调用：narrative-writer（去AI味执行）

「诊断与分级」完成后，按以下顺序选择执行路径：

1. **已在 narrative-writer 子代理内**：按选定 Gate 范围 inline 执行，不再 spawn（嵌套 spawn 会被静默降级）。
2. **未在子代理内且按顶部顺序找到 `narrative-writer` agent**：按当前运行时调用；Antigravity 用 `invoke_subagent(TypeName: "narrative-writer")`，Claude/OpenCode/Codex 用各自字段。prompt 保持：`项目目录：{dir}\n任务描述：去AI味\nGate 细则：执行前按你的参考表读取 deslop-gates.md 的删除保护与所选 Gate（部署副本与本 skill 同源）\n改前备份：文件模式先把当前章节复制到同目录 _revision-backups/{stem}_原稿_pre-deslop_{YYYYMMDD}{ext}（须含 _原稿_；同日冲突追加 _{HHmm}），再改写；备份路径写入报告\n对照库（硬步骤）：读取 phrase-bank-humanize.md；用 book/_analysis/ai_to_human_replacements.json——先精确 map，再逐句语义对齐（句意与表内 meaning 一致且能表达同一意思则从 replace_with 挑 1 条；不一致不换）；报告必须含「对照库:已执行」，缺则去味未完成；人味句里的 {xx} 必须回填本书角色名（设定/角色、关系.md、本章 POV）；写出 {stem}_humanized{ext}；**写后定稿模式**须再覆盖正式正文路径并报告「定稿覆盖:已执行」（单独调用默认不覆盖原稿；用户明确原地改除外，原地改也须先备份）\n检查分工：你负责本次语义去味；父流程负责 Phase 4 最终文件扫描，不重复整轮改稿\n检查范围：{待处理的正文文件}\n文风路径：{本书文风全文路径，无则写无}\nstyle_resolution：{本次生效要求及来源、被覆盖的默认条款、事实边界}\n作者偏好：{query 命中的 prose_style 项}\nAI味等级：{诊断与分级结果}\n处理策略：{实际选定的 Gate 范围；优先使用用户指定范围}\n删除优先：每条 AI 味项先判能否删除——删后不丢伏笔/钩子/角色/情节/人物记忆/情绪承接/因果锚点/必要信息/必要转折的直接删，会丢才进 Gate 润色；看似解释/评价但承担小连贯的句子，压成白话承接、动作或物件锚点，不机械删除；已有任务/手续/物件/证据缺口可以压成角色当下要处理的具体卡点，但不新增原文没有的事件链；删除服从比例上限与字数下限，跌破下限改降AI重写。\n模式处理：按 references/anti-ai-writing.md 的问题模式目录执行；模式 8（解释腔/上帝视角/安排感）归入 Gate G，其余新增模式归入 Gate A-F 的对应处理。相邻段重复表达同一信息/动作/情绪时，按 Gate C/D 合并去重；`。
3. **agent 不存在或 spawn 失败（含 Cursor）**：主线程 **立即** inline 执行本 skill 剩余 Phase（诊断→**对照库**→Gate→收尾），报告 `Deslop: solo inline`；禁止只跑 `check-ai-patterns.js` 后结束；报告无 `对照库:已执行` 不得结案。

#### Gate 规则入口

实际执行者在逐项清除前读取 [references/deslop-gates.md](references/deslop-gates.md) 的删除保护与所选 Gate 细则；inline 与 agent 使用同源规则。三遍法仍按前文安排所选 Gate 的执行顺序，不另起一次全篇去味。

#### 对照库替换（文件模式默认；清理/重构档硬步骤）

按 [references/phrase-bank-humanize.md](references/phrase-bank-humanize.md) 执行。**跳过本步 = 去味未完成**（仅检测档或用户原话豁免除外）。

1. **若 Phase 0 尚未备份**：先复制当前章节到 `_revision-backups/{stem}_原稿_pre-deslop_{YYYYMMDD}{ext}`（见输出契约第 0 步）。
2. **精确层**：用 `book/_analysis/ai_to_human_replacements.json` 的 **`map` 按键查** `replace_with`；辅以 `pairs`、以及 `ai_human_phrase_bank.json` 的 buckets/精选组、`phrase_bank_index.md` 类目示例。
3. **语义层（硬步骤）**：精确命中为 0 也不能收工。对正文**逐句**判断意思是否对齐表内某一 `meaning`；若一致、能表达同一意思且不漂命题，从该组 `replace_with` / `human_expr` / `human_top` **挑 1 条**替换；不一致则不换。
4. **禁止无脑全局替换**；按 category/meaning 与人称语气适配；剧情保护与疲劳词阈值同时生效。
5. **`{xx}` → 本书角色名**：人味句（`human_expr` / `human_top`）里的 `{xx}` 写入正文前必须回填（角色卡/`设定/关系.md`/本章 POV）；禁止残留 `{xx}` 或源书人名。细则见 phrase-bank-humanize。
6. 将 Gate 润色 + 对照库替换的结果写入 **`{stem}_humanized{ext}`**（单独调用默认；原稿不动）。**写后定稿模式**或用户要求原地改/定稿覆盖：备份后写入人味结果，再**覆盖正式正文路径**；报告须 `定稿覆盖:已执行`。
7. 报告必须含 `对照库:已执行`、扫描句数、精确 map 命中/替换、语义对齐命中/替换、`{xx}` 回填、跳过/`[需复核]`，并列出原文件、改前备份与人味文件路径；写后定稿另列正式正文路径与 `定稿覆盖:已执行`。替换数可为 0，须写语义扫描结论。

### Phase 4：确定性收尾（文件模式）

当输入是正文文件路径，且「逐项清除」+对照库替换已写入 **`_humanized` 产物**（或用户授权的原地文件）后，对**产出文件**（不是未改的原稿）**先**做句式/段落复扫，**再**做机械标点兜底（破折号要按功能改写，故先于机械替换报出），**再**做机械量表（可选但对账推荐）：

```bash
node scripts/check-ai-patterns.js --check --fail-on=blocking <人味或已改正文文件...>
node scripts/check-degeneration.js --check <人味或已改正文文件...>
node scripts/normalize-punctuation.js <人味或已改正文文件...>
python scripts/slop_gauge.py --profile novel <人味或已改正文文件...>
# 推荐对账：python scripts/slop_gauge.py --diff --profile novel <原稿> <人味文件>
```

作用边界：
- `check-ai-patterns.js` 只报告不改写：severity=blocking 的类别优先改正文并复扫；advisory 先通读判断，确属提纲感、解释腔或模板腔再改，功能性写法标 `[需复核]`。
- 它只是读感提示；完整类别、例外和修法见 `references/anti-ai-writing.md` 与 `references/chinese-native-patterns.md`。
- `check-degeneration.js` 报告模型退化（逐字复读/打转、末尾截断、占位符、工程词泄漏 `细纲`/`情节点` 等），每条带 `severity: blocking|advisory`。blocking 是退化信号，去AI味改不掉，应回去重新生成那一段再 deslop；advisory（tier2 章节/歧义词）只提示。
- `normalize-punctuation.js` 机械兜底：保留书级白名单获准的停顿，清除其余残留的 `……`、漏网破折号 `——`/`—`、双连字符 `--` 和独立行 `---`；默认不改变引号风格，也不把有功能的 `？` / 少量 `！` 改成句号。
- `slop_gauge.py` 确定性量化（词表/标点/节奏/结构/归因）；score ≥55 为机械参考线，低于标 `[机械未达标]`，**不单独否决**。阈值与 Gate 映射见 [references/slop-gauge-thresholds.md](references/slop-gauge-thresholds.md)。ecommerce 用 `--profile ecommerce` 且 adlaw 应为 0。
- 知乎盐言短篇可保留 `「」`；只有用户或项目明确要求时，才给标点脚本加 `--quote-mode ascii` 或 `--quote-mode yan`。

---

**视角改写复核（仅本次要求切换视角时）**：交付前回读原文，逐项核对新增的感知/认知句。原文只说明事件发生，不等于人物已经看见或知道；不得自行补观察时点。没有原文依据的“进门时发现”“后来看到”等句子删去，或只呈现原有、当前场景可见的物件状态；不可得的信息暂不叙述。这个检查先于交付，不能用句式脚本通过代替。

### Phase 5：输出润色结果

```
## 去AI味润色报告

### 字数协议
- 原文件：{path}
- 改前备份：{path/_revision-backups/{stem}_原稿_pre-deslop_… 或「检测档未备份」}
- 人味文件：{path_humanized 或「原地改」}
- 定稿覆盖：{正式正文路径 +「定稿覆盖:已执行」/「单独调用未覆盖」/「检测档未改」}
- 原文字符数：{N0}
- 修订后字符数：{N1}
- 净变化：{N1 - N0}（{百分比}）
- 是否在 tier 上限内：{是 / 否（超限 X%，已分段并标注 [需复核]）}

### 修改统计
- 总修改数：{N} 处
- **对照库:已执行**（缺此项 = 去味未完成）
- 对照库扫描句数：{N}
- 对照库精确 map 命中/替换：{N}/{N}
- 对照库语义对齐命中/替换：{N}/{N}（跳过或 [需复核] {N}；0 替换须附「无可替句」理由）
- `{xx}` 角色名回填：{N}（残留 0；无法判定 [需复核：角色名] {N}）
- 禁用词替换：{N} 处
- 句式调整：{N} 处（含否定翻转句式 {N}、"，带着..." {N}、声音描写 {N}）
- 修饰词清扫：{N} 处
- 情绪落地与重复说明清理：{N} 处
- 重复描写合并：{N} 处
- 监控动作清单合并：{N} 处
- 重复语义去重：{N} 处（形容词重复 {N}、近义词重复 {N}、含义重复 {N}、主语重复 {N}）
- 比喻处理：{N} 处（删除/保留/改回具体画面）
- 节奏调整：{N} 处
- 对话优化：{N} 处
- 标点节奏调整：{N} 处（保留有功能 `？`/少量 `！`，将 `……`/`——` 改为动作、短句、逗号或句号，并清理无功能堆砌）
- 结尾修正：{N} 处
- slop-gauge：score {N}/100（profile={novel|…}）；AI 密度 {x}/千字；CV {x}；diff 要点：{1-5 条或未跑}

### 修改前后对比
{逐段展示修改，标注改动类型；超过 30 处时仅展示前 10 处 + 末 5 处 + 其余按 Gate 分桶计数}

### 润色后全文
{**文件模式（默认；章节/正文文件、批量与长篇去AI）**：写入 `{原名}_humanized{后缀}`（对照库启用时强制；见 phrase-bank-humanize），本节只回 ≤200 字代表性片段 + 原/人味路径，不向父会话返回全文。**文本模式（仅限交互式贴入、无文件路径的零散片段）**：完整输出润色后的文本。}
```

**字数硬约束**：删除比例不得超过「诊断与分级」对应上限（轻度 ≤15%、中度 ≤25%、重度 ≤35%）。超限时分段输出并在报告里标记，不得整段删除正文。

**收敛终止**：
1. 同一段连续两轮去 AI 后没有新改动 → 停止该段处理
2. 全文上限 3 轮重扫；第 3 轮仍有 ≥10 处改动 → 在报告里标 `[需复核]`，移交人工
3. 每轮结束前都要做一遍"再检一次"：是否有不符合的地方，有则继续；没有则停
4. **对照库门禁**：清理/重构档在宣称完成前，报告必须已有 `对照库:已执行`（含语义层）；否则继续本轮，不得结案

---

## 使用场景

| 场景 | 操作 |
|------|------|
| 用户贴一段文字说"太AI了" | 定档清理 → 完整检测 + 润色 |
| 用户说"帮我润色" | 定档清理 → 先检测再润色 |
| 用户说"检查下有没有AI味" | 定档检测 → 只做检测，不做修改 |
| 用户明确授权"重写结构/重构" | 定档重构 → 每章 2–5 个结构动作 + Gate |
| 用户写作中要求 `仅标注 / 只检测 / 不要改` | 嵌入式提醒模式：执行「AI味扫描」和「诊断与分级」，跳过「逐项清除」「确定性收尾」「输出润色结果」；输出问题标记表（含 Gate 列），不修改原文，不写文件 |
| 章节文件去味（单独调用默认） | 先备份到 `_revision-backups/` → 对照库 + Gate → 写出 `{stem}_humanized{ext}`，原稿不动 |
| **写后定稿模式**（写正文同轮 / 「定稿覆盖」） | 先备份 → 对照库 + Gate → 人味产物 → **覆盖正式正文路径**；报告须 `定稿覆盖:已执行` |
| 用户说「原地改 / 覆盖原稿」 | 先备份到 `_revision-backups/` → 对照库 + Gate → 直接改原文件 |
| 无活跃书，仅润色公众号/小红书等短文 | [references/shortform-sidepath.md](references/shortform-sidepath.md)，不建小说目录 |

---

## 参考资料

按需加载以下文件：

| 文件 | 何时加载 |
|------|----------|
| [references/deslop-process.md](references/deslop-process.md) | **开场必读**：定档、Never inject、保真摘要、C 级禁动、检测器边界、改前备份 |
| [references/fidelity-constraints.md](references/fidelity-constraints.md) | 保真/scope/引号用途/无源分流/真删不换汤/浓度计边界（说人话×韩愈） |
| [references/generation-constraints.md](references/generation-constraints.md) | 新写/写前自检；减少生成阶段模板节奏 |
| [references/scan-lexicon.md](references/scan-lexicon.md) | 成簇扫描：八股/名词化/黑话/无立场退让/装腔/EN/泄漏 |
| [references/shortform-sidepath.md](references/shortform-sidepath.md) | 无书短文旁路 |
| [references/banned-words.md](references/banned-words.md) | 检测和替换禁用词时 |
| [references/phrase-bank-humanize.md](references/phrase-bank-humanize.md) | **文件模式必读（默认）**：ainovel-cli 判据合并 + 对照库替换 + 改前备份 + `_humanized` 输出契约 |
| [references/deslop-gates.md](references/deslop-gates.md) | 逐项清除前：删除保护与所选 Gate 的细则、示例 |
| [references/anti-ai-writing.md](references/anti-ai-writing.md) | **去AI味完整指南**：预防+三遍法+范例 |
| [scripts/normalize-punctuation.js](scripts/normalize-punctuation.js) | 文件模式落盘后做确定性标点收尾；默认保留引号风格 |
| [scripts/check-ai-patterns.js](scripts/check-ai-patterns.js) | 文件模式「AI味扫描」预检与「确定性收尾」复扫（只看引号外叙述），只报告不改写 |
| [scripts/check-degeneration.js](scripts/check-degeneration.js) | 文件模式「确定性收尾」复扫，只报告不改写 |
| [references/author-memory.md](references/author-memory.md) + [scripts/author_memory_commit.py](scripts/author_memory_commit.py) | 读取或更新跨会话作者文风习惯时 |

---

## 流程衔接

**流水线：** 通用
**位置：** 润色（共享收尾）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 继续写作 | story-long-write / story-short-write | `/story-long-write` 或 `/story-short-write` |
| 发现结构问题 | story-long-analyze / story-short-analyze | `/story-long-analyze` 或 `/story-short-analyze` |
| 准备做封面 | story-cover | `/story-cover` |

---

## 语言

- 跟随用户的语言回复，用户用什么语言就用什么语言回复
- 中文回复遵循《中文文案排版指北》
