# 优质信源分级表

> 与 wenxuan-research/wenxuan-learn 共用。AI 抓取信息时按本表判断信源等级，决定是否进入弹药包/数据库。
> 最后更新：2026-06-13（基于文轩「AIHOT 信源池」15 条筛选）

---

## 三级分类

### A 类 · 一手信源（必查 + 多源验证）

> 凡是涉及数字、版本、特性、价格、时间线的声明，**必须**能交叉印证 2 个 A 类信源才能进入弹药包。

| 子类 | 说明 | 例子 |
|------|------|------|
| **官方博客/Doc** | 厂商/团队第一人称 | Cloudflare Blog, OpenAI Blog, Anthropic Blog |
| **GitHub 仓库/Doc** | 代码、README、CHANGELOG | hermes-desktop, langchain, cursor |
| **arXiv/PDF 论文** | 学术成果 | 2606.13473v1 (MaxProof) |
| **产品本体** | 用户在跑的版本本身 | 自己跑一遍 Claude Code、Cursor |

### B 类 · 权威媒体/优质博客（需交叉验证）

> 至少 1 个 B 类 + 1 个 A 类才能采信。仅 B 类孤证**不直接进入弹药包**，须进事实核查剔除清单标注「未交叉验证」。

| 子类 | 说明 | 例子 |
|------|------|------|
| **科技垂直媒体** | 深度长文、专业视角 | The Verge, Ars Technica, TechCrunch, VentureBeat, MarkTechPost |
| **领域 KOL 博客** | 大佬自己写的 | lilianweng.blog, Shunyu Yao 博客 |
| **政策法规** | 法规监管一手 | Dataguidance |

### C 类 · 社区/社媒信号（只作辅证，不可作唯一出处）

> 仅作"行业热度"信号源，**不能**作为数据/事实/版本号的唯一依据。引用时必须配 A 或 B 类信源。

| 子类 | 说明 | 例子 |
|------|------|------|
| **Reddit/Quora/知乎** | 用户真实讨论 | r/MachineLearning, r/LocalLLaMA |
| **官方推特/X 账号** | 厂商发布入口 | @ClaudeDevs, KreaAI, Odyssey, ViggleAI |
| **Newsletter** | 二手聚合 | The Rundown AI, TLDR AI |
| **YouTube/TikTok** | 视频内容 | 头部频道 |

---

## 使用准则（避免幻觉）

### 准则 1：A 类是「事实必查」

凡是产品功能/版本号/官方政策/数据/价格，**必须**找到 A 类信源（GitHub 仓库 commit、官方文档、官方博客）。找不到的，**直接写进事实核查剔除清单**，不进入弹药包。

### 准则 2：B 类是「事实可查」

知名媒体如 TechCrunch、The Verge、Ars Technica 可信度高，但**单一 B 类孤证不构成事实**。必须配合 A 类或另一个独立 B 类交叉验证。

### 准则 3：C 类只作「热度信号」

Reddit 高频讨论、X 账号发布、YouTube 爆款视频——这些**只能证明事情有人关心**，**不能证明事情是真的**。引用时必须配 A/B 类。

### 准则 4：避免「中间人重译」

很多 B 类内容是从官方推特/Newsletter 转译的。看到 B 类文章时，问一句"它原始信源是什么？"——是 A 类就提升权重，是 C 类就降级处理。

---

## 同类误判辨认（三件套）

> 高质量信源也常被同名不同物混淆。AI 每次抓到候选信源时，必须做三件套辨认：

| 辨认 | 检查什么 | 例 |
|------|---------|-----|
| **同名账号** | GitHub 用户/推特账号/微信公众号是同一个人吗？ | "lilianweng" 是 lilianweng.blog 作者本人，但同名推特号可能是冒名 |
| **同名仓库** | 同一项目名在不同平台可能是不同项目 | "hermes" 在 npm/python/公司产品里是不同东西 |
| **同名公司** | 同一公司名在不同子领域可能是不同实体 | "Cloudflare" 母公司 vs 旗下 Workers 产品线 |

如果辨认不通过 → 进事实核查剔除清单，标注「同名词未消歧」。

---

## AIHOT 信源池（文轩指定，共 15 条）

> 来自文轩提供的 AIHOT 信源整理。本表是"信源候选池"，AI 实际引用时仍需走上面三级分类 + 三件套辨认。

### A 类（5 条）
1. **Cloudflare Blog** (卡兹克 2026-05-13) — Workers AI / AI 推理 / Edge 计算的一手案例
2. **hermes-desktop** (sunweihu 2026-05-19) — 开源地址 https://www.sunweihu.com/
3. **lilianweng 博客** (lilianweng 2026-05-19) — 大佬博客
4. **Shunyu Yao 博客** (Rapheal 2026-05-19) — 大佬博客
5. **X: @ClaudeDevs** (AIHOT N°001) — Claude 团队官方开发者账号

### B 类（7 条）
6. **The Verge** (Eagle 2026-05-21) — 科技/科学/艺术交叉，深度分析
7. **TechCrunch** (Eagle 2026-05-21) — 硅谷创投圈动态
8. **Ars Technica** (Eagle 2026-05-21) — 硬核科技媒体，深度评测
9. **VentureBeat** (nam 2026-05-15) — 前沿科技 + 企业数字化
10. **MarkTechPost** (Eagle 2026-05-21) — ML/DL/GenAI 论文摘要 + 工具评测
11. **Artificial Intelligence News** (Eagle 2026-05-21) — 商业应用 + 领导力思维
12. **Dataguidance** (周星星 2026-05-19) — 全球 AI 政策法规

### C 类（3 条）
13. **KreaAI 官方推特** (Likewindy 2026-05-13) — Krea 2 模型发布
14. **Odyssey 官方推特** (Likewindy 2026-05-21) — Agora-1 世界模型
15. **ViggleAI 官方推特** (Likewindy 2026-05-15) — PINOC 模型

> 提示：AIHOT N°008、N°010、N°015 等序号是 AIHOT 平台的内部编号，本表保留作为 ID 标识。
