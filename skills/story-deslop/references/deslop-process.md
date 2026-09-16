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

## Protected spans（默认不动）

引语、代码块、表格、公式、法律/标准原文、他人 attributed 文本、用户明确要求保留的片段。周边可改衔接；内容需单独授权。

## 网文 C 级禁动（看着像 AI 也别乱碰）

下列**不是**自动删除目标；误杀会伤追读与因果：

- 强因果链、伏笔回收
- 短段密集追读、主角高在场、线性推进
- 必要心理独白
- 句内合理顿号列举

仲裁顺序：**用户样文/明确偏好 > C 级禁动 > Gate 硬改 > 软判信号**。

## good-writing 修补协议

先列**完整缺陷清单**，再从深层到表层修。无清单直接改，容易换成另一种 AI 指纹。

清理档：每章只挑 **2～5** 个结构/表达动作（症状可全报，大改要授权）。

## Detector boundaries

- 单工具、单百分比**不得**单独否决或驱动策略
- 对照须同检测器、相近字数、同体裁；**<3000 字片段只作方向性观察**
- 若工具对重复粘贴/无关文本稳定判「人写」、对完整小说草稿稳定判 AI → **弃用为 gate**
- Pattern ≠ 作者身份证明；正式文体/非母语易误报

结果可写入报告，不作唯一验收。去AI味治读感，不承诺过朱雀等分数。

## 标点策略（与本仓默认一致）

本仓默认：无功能的 `……` / `——` / `--` / 独立 `---` 在文件模式由 `normalize-punctuation.js` 硬清；功能性停顿经本书 `设定/文风.md` 或书目录 `.deslop-whitelist` 登记后保留。

> novel-write-produce 合并层曾默认保留功能性破折号/省略号。本仓仍以番茄样本与脚本默认为准；需要保留时走白名单/文风，不静默翻转全局默认。

## 对照库与 `_humanized` 落盘

文件模式默认叠加 [phrase-bank-humanize.md](phrase-bank-humanize.md)（ainovel-cli 机械/语义判据 + `book/_analysis` 对照库）。对照库替换结果写入 `{stem}_humanized{ext}`，**不覆盖原稿**（用户明确「原地改」除外）。Phase 4 脚本跑在人味产物上。

## 与 Gate / 脚本关系

1. 定档 → 文风 / `style_resolution` → 扫描（含 [scan-lexicon.md](scan-lexicon.md) 成簇）
2. 定级轻/中/重 → 选 Gate（见 `SKILL.md`）；加载 phrase-bank-humanize（文件模式默认）
3. 清除时遵守 Never inject、C 级禁动、删除比例；对照库优先 `ai_to_human_replacements.json` 的 `map`
4. 写入 `_humanized` 产物（默认）→ 文件模式收尾：`check-ai-patterns.js` → `check-degeneration.js` →（按策略）`normalize-punctuation.js`
