# slop-gauge 机械量表阈值

> 蒸馏自 `refs/Chendestiny__slop-gauge`。测量，不判断，不改写。与 stop-slop 五维观感组成双道门禁的**机械侧**。  
> **Detector boundaries 仍有效**：单工具分数不得单独否决策略；朱雀等黑盒永不进交付判断。

## 调用

```bash
# 单文件（网文默认 novel）
python scripts/slop_gauge.py --profile novel <人味或已改正文>

# 改写前后对账（推荐写入润色报告）
python scripts/slop_gauge.py --diff --profile novel <原稿> <人味文件>

# 带货稿
python scripts/slop_gauge.py --profile ecommerce <文件>
```

词表：`data/ai_words_zh.txt`（含 `-- adlaw` 段）。脚本路径相对于本 skill 目录。

## 参考线

| 项 | 阈值 | 语义 |
|----|------|------|
| 合成 score | **≥55 / 100** | 机械参考线；低于 → 报告标 `[机械未达标]`，**不单独否决**清理策略 |
| 句长 CV | ≥0.25 视为节奏良；novel 约 <0.22 起罚 | 对齐 Gate D |
| 连续等长 | max_equal_run ≥4 | 对齐 Gate D |
| 破折号密度 | >1 / 千字起罚；novel 对话引号内豁免计罚 | 见 [scene-profiles.md](scene-profiles.md) |
| ecommerce adlaw | 计数应为 **0** | 对齐 [adlaw-words.md](adlaw-words.md) |

## 指标族 → Gate 映射

| 族 | 指标 | 主要 Gate |
|----|------|-----------|
| 词汇 | ai_density（加权/千字） | A |
| 标点 | em / bold / exclaim | E（对话）/ 标点策略 |
| 节奏 | cv / max_equal_run | D |
| 结构 | triads / judgment_triads / negation_contrast | B |
| 结构 | stamp_open / lift_end / from_to_jumps | F / B |
| 归因 | vague_attribution | G |
| 合规 | adlaw | ecommerce 专用 |

## 与 stop-slop 观感评分

| 层级 | 工具 | 参考门槛 | 用途 |
|------|------|----------|------|
| 机械 | slop-gauge | score ≥55 | Phase 4 可选/推荐；diff 3–5 项数字变化可进报告 |
| 观感 | stop-slop 五维（Directness/Rhythm/Trust/Authenticity/Density） | ≥35/50 | Agent 自评参考，**不得替代 Gate** |
| 主定级 | story-deslop 禁用词/千字 + 六指标 | 轻/中/重 | **保留为主定级** |

## 边界

- 只测中文为主文本；词表抓不到的痕迹测不到；90+ ≠ 过朱雀。
- 数字只回答「有没有这些痕迹」；交付仍看读感、剧情边界与 Never inject。
