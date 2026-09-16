# 去AI味场景档（article / novel / ecommerce）

> 蒸馏自 `refs/Chendestiny__humanizer-zh-plus`。网文正文默认 **novel**；设定集/作者说明用 **article**；带货/种草短文用 **ecommerce**。

| 档位 | 触发 | 规则差异 |
|------|------|----------|
| **article** | 文章、博客、汇报、设定说明 | 全部中文原生模式生效；标点按仓默认（无功能 `……`/`——` 清） |
| **novel**（默认网文） | 小说章节、人物对话 | 见下方 novel 裁决；情节钩子保留；对话不得净化成播报体 |
| **ecommerce** | 营销文案、带货稿 | 广告法极限词改写期替换（[adlaw-words.md](adlaw-words.md)）；种草 emoji/语气词/夸张由合规层管，不走通用禁令 |

## novel 档与本仓标点默认的冲突裁决

本仓文件模式默认：无功能的 `……` / `——` / `--` / 独立 `---` 由 `normalize-punctuation.js` 硬清（见 [deslop-process.md](deslop-process.md)）。

**裁决（网文）**：

1. **叙述层**：仍按仓默认——无功能破折号/省略号停顿改动作、短句、逗号或句号。
2. **对话引号内**：质问 `？`、爆发峰值少量 `！`、角色语气词**保留**；不因「去 AI」把台词改成书面播报体。
3. **对话内破折号**：本仓仍**不设全局对话破折号豁免**（与 humanizer-zh-plus novel 档原文不同）。需要保留时走本书 `设定/文风.md` 或书目录 `.deslop-whitelist`，不静默翻转全局默认。
4. **slop-gauge `--profile novel`**：对话引号内破折号在机械量表侧豁免计罚；这只影响分数，不授权 `normalize-punctuation.js` 跳过。

## ecommerce 档

- 改写期内按 [adlaw-words.md](adlaw-words.md) 替换极限词；原则是写具体事实/口径，不是换温和形容词。
- 跑 `python scripts/slop_gauge.py --profile ecommerce`，`adlaw` 计数应为 0。
- 不把带货规则套进小说正文。

## 选择顺序

1. 用户点名档位 → 用该档  
2. 输入是章节/正文路径 → **novel**  
3. 短篇旁路且明显带货 → **ecommerce**（见 [shortform-sidepath.md](shortform-sidepath.md)）  
4. 其余 → **article**
