# 检索手册

目标：把"我要查什么"变成可执行的检索动作，并且分得清材料的证据角色。**本文件全部是动作，不含任何关于具体概念的结论。**

## 四层检索词（每层都要跑，缺一层就片面）

以概念 `X` 为例，中文检索词直接用 `X` 的中文译法或行业俗称。

### 第一层 原始（拿规格和原文）

```text
X official documentation
X spec specification RFC
X design doc architecture
X release notes changelog
X 官方文档 规范
X 白皮书 技术报告
```

学术型概念必查 arXiv：

```text
curl -s "https://export.arxiv.org/api/query?search_query=all:%22X%22&max_results=20&sortBy=relevance"
```

返回 XML，取 title / summary / published / id，关键论文再用 `https://arxiv.org/abs/<id>` 读细节。也查 `X site:arxiv.org`、`X survey paper`、`X systematic review`。

### 第二层 独立（第三方视角）

```text
X independent benchmark
X third-party evaluation comparison
X reproduced results
X independent audit security review
X 实测 对比 评测
X 第三方测试
```

优先找**能复现方法**的材料：测试环境、样本、版本、时间、测了几次。只有结论没有方法的，降级。

### 第三层 反方（必须有）

```text
X criticism problems limitations
X does not work when
X failed production case study
X why we moved away from X
X alternative to X limitations
X controversy debate
X 缺点 坑 踩坑 局限性
X 为什么放弃
```

反方材料的最佳来源是**迁移叙事**：「我们用 X 做了一年，然后换掉了」这类文章的信息密度远高于测评。

### 第四层 实测（用户自己的数据）

```text
X pricing usage limits
X free tier rate limits
X community bug reports
X github issues open problems
X reddit experience
```

实测只能由用户在真实环境里做：写入条件（设备/版本/任务/次数/价格档位）后再看结果。AI 不得代填数字。

## 信源分级：角色而不是排名

| 级别 | 典型来源 | 优势 | 已知偏差 |
|---|---|---|---|
| 官方 | 官方文档、发布博客、论文原作者、财报 | 规格与设计意图准确 | 有商业与叙事立场，只讲成功案例 |
| 独立第三方 | 独立测评、复现实验、行业分析 | 有方法可核 | 可能有流量动机，样本小 |
| 社区与开发者 | GitHub Issues、Reddit、HN、知乎、X | 真实失败模式、边界情况 | 无统计代表性，情绪化 |
| 本人实测 | 用户在自己的任务上跑 | 最贴近自身场景 | 样本量小，不可外推 |

规则：**同一事实至少两个不同级别来源**才算稳；只有一级来源时，标「单源，待交叉」。

## 检索纪律

- 每轮搜完立刻把**新的**信息落卡，不重复搬运。
- 关键词要换角度：中文 -> 英文、术语 -> 口语、品类 -> 竞品名、正面 -> 负面。
- 至少 20 轮有意义检索再判断"查够了"；查够的标准是**能并列写出双方最强的论证**，不是"我觉得明白了"。
- 遇到付费墙/登录墙：记录"未能读原文"，只依据可见部分，不含推测。
- 时间敏感材料看发布日期，旧数据当现状是最常见的错误之一。

## 中文源怎么用

中文源适合快速建立术语表、找到国内落地场景与真实踩坑，但不适合当唯一证据链。

```text
X 是什么 原理 通俗解释
X 落地 实践 案例
X 踩坑 经验
X 对比 选型
```

术语对照很关键：中文俗称和英文原名不一致时，两套都搜，否则会漏掉原始来源。

## 不可比检测（横向比较前必做）

在把两个方案放同一张表之前，逐条确认：任务是否相同、版本是否相同、硬件是否相同、时间是否相同、价格档位是否相同、样本是否相同。

任一条不一致，就在表里写「不可比」并注明差异。**把不可比的数据做成排名，是本流程最危险的一步。**

