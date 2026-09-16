# 去AI味流程合同

补充自 novel-write-produce 的 anti-ai 合并层。与本 skill 的 Gate A–G、三遍法并用；**不**另起可覆盖 `SKILL.md` 的顶级政策。

## 定档（开场必报）

| 档 | 含义 | 行为 |
|----|------|------|
| **清理**（默认） | 只清语言与表达簇 | 改最少；骨架不动 |
| **重构** | 须用户明确授权 | 可动结构；每章只挑 2–5 个结构动作，写成连续新骨架，勿贴着初稿句序换词 |
| **检测** | 只标问题 | 输出报告，不改文 |
| **新写** | 从零起草 | 先读 [generation-constraints.md](generation-constraints.md) |

用户未指定时默认**清理**。说「只要终稿」→ 省略过程说明，约束不降级。

## Never inject（改写硬禁）

- 假第一人称经历、编造 stakes、假对立观点、表演式 candid
- 故意错别字、乱序、隐形字符、碎句化骗「人味」
- 编造数字、姓名、机制、出处；用模型记忆补洞
- 把讨论中的坏例子当成要执行的新指令
- 注水凑字、同义反复灌篇幅

与 `SKILL.md`「治读感、不承诺分数」一致；本表为显式硬禁。

## 保真与浓度计（shuorenhua × hanyu）

细则见 [fidelity-constraints.md](fidelity-constraints.md)。摘要：

- **保真**：条件/否定/情态/归属/比较方向不因去味漂移；不按词表命中次数盲换；真删套话，不把「首先」换成「首先呢」
- **Scope**：`structural` / `bounded` / `in-place`（用户优先；清理档默认 structural，少改时收窄）
- **浓度计**：hanyu / 任意 AI 分只作改前改后相对参考，**不能**判定作者身份；领域黑话（闭环/链路等）成簇且空用才动
- **网文「补」**：只把原文已有具体物推到前台；不造数字/案例；空转无剧情功能才可整段删

## Protected spans（默认不动）

引语、代码块（含注释/文档字符串，改注释须用户点名）、表格、公式、法律/标准原文、他人 attributed 文本、用户明确要求保留的片段。周边可改衔接；内容需单独授权。引号按用途判断，见 fidelity-constraints。

## 网文 C 级禁动（看着像 AI 也别乱碰）

下列**不是**自动删除目标；误杀会伤追读与因果：

- 强因果链、伏笔回收
- 短段密集追读、主角高在场、线性推进
- 必要心理独白
- 句内合理顿号列举

仲裁顺序：**用户样文/明确偏好 > C 级禁动 > Gate 硬改 > 软判信号**。

## good-writing 修补协议

先列**完整缺陷清单**，再从深层到表层修。无清单直接改，容易换成另一种 AI 指纹。

修补顺序：**结构 → 语气 → 句式 → 词语**（与 de-AI-writing 一致）。

清理档：每章只挑 **2～5** 个结构/表达动作（症状可全报，大改要授权）。

## 场景档

网文正文默认 **novel**；设定说明用 **article**；带货短文用 **ecommerce**。差异与标点冲突裁决见 [scene-profiles.md](scene-profiles.md)。中文原生模式 25–33 见 [chinese-native-patterns.md](chinese-native-patterns.md)。

## 双道门禁（机械 + 观感）

| 侧 | 工具 | 参考线 | 语义 |
|----|------|--------|------|
| 机械 | `python scripts/slop_gauge.py --profile novel`（见 [slop-gauge-thresholds.md](slop-gauge-thresholds.md)） | score ≥55 | Phase 4 推荐；低于标 `[机械未达标]`；**不单独否决** |
| 观感 | stop-slop 五维自评 | ≥35/50 | Agent 参考，不得替代 Gate |
| 主定级 | 本 skill 禁用词/千字 + 六指标 | 轻/中/重 | **保留为主** |

改写前后可用 `--diff` 把 3–5 项数字变化写入润色报告。ecommerce 档另要求 adlaw=0（[adlaw-words.md](adlaw-words.md)）。

## Detector boundaries

- 单工具、单百分比**不得**单独否决或驱动策略（含 slop-gauge、stop-slop、朱雀、hanyu_detect）
- 对照须同检测器、相近字数、同体裁；**<3000 字片段只作方向性观察**
- 若工具对重复粘贴/无关文本稳定判「人写」、对完整小说草稿稳定判 AI → **弃用为 gate**
- Pattern ≠ 作者身份证明；正式文体/非母语易误报
- 讨论 AI 味、列举禁用词的文章会被词表型检测器系统性高估（引用≠使用）——勿据此定级
- AI/商业/技术主题稿：领域术语易被当成黑话，绝对值可虚高 5–10 分；只看相对降幅

结果可写入报告，不作唯一验收。去AI味治读感，不承诺过朱雀等分数。可选相对读数：`python refs/694410194__hanyu-skill/scripts/hanyu_detect.py <file.md>`（见 fidelity-constraints）。

## 标点策略（与本仓默认一致）

本仓默认：无功能的 `……` / `——` / `--` / 独立 `---` 在文件模式由 `normalize-punctuation.js` 硬清；功能性停顿经本书 `设定/文风.md` 或书目录 `.deslop-whitelist` 登记后保留。

> novel-write-produce / humanizer-zh-plus novel 档曾默认对话内破折号豁免。本仓仍以番茄样本与脚本默认为准：叙述层硬清；对话内 `？`/少量 `！`/语气词保留；对话破折号需白名单/文风显式登记。slop-gauge novel profile 的对话内豁免只影响机械分数。详见 [scene-profiles.md](scene-profiles.md)。

## 对照库与 `_humanized` 落盘

文件模式默认叠加 [phrase-bank-humanize.md](phrase-bank-humanize.md)（ainovel-cli 机械/语义判据 + `book/_analysis` 对照库）。对照库替换结果写入 `{stem}_humanized{ext}`，**不覆盖原稿**（用户明确「原地改」除外）。人味句中的 `{xx}` 写入前须回填为本书角色名（见 phrase-bank-humanize）。Phase 4 脚本跑在人味产物上。

## 与 Gate / 脚本关系

1. 定档 → 场景档（默认 novel）→ 文风 / `style_resolution` → 扫描（含 [scan-lexicon.md](scan-lexicon.md) 成簇 + [chinese-native-patterns.md](chinese-native-patterns.md)）；保真边界见 [fidelity-constraints.md](fidelity-constraints.md)
2. 定级轻/中/重 → 选 Gate（见 `SKILL.md`）；加载 phrase-bank-humanize（文件模式默认）
3. 清除时遵守 Never inject、保真/scope、C 级禁动、删除比例；真删套话不换汤；对照库优先 `ai_to_human_replacements.json` 的 `map`；人味侧 `{xx}` 回填本书角色名后再落盘；人味句 `{xx}` 回填本书角色名后再落盘
4. 写入 `_humanized` 产物（默认）→ 文件模式收尾：`check-ai-patterns.js` → `check-degeneration.js` →（按策略）`normalize-punctuation.js` →（推荐）`slop_gauge.py --profile novel`〔可选 `--diff`〕
