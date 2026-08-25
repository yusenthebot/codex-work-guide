# Codex 工作指南

这是一份面向管理者和知识工作者的简明教程。目标是把调研、写作、资料整理和重复流程交给 Codex，同时保留人工判断和审批。

## 1. 从一个清楚的任务开始

先打开与任务有关的文件夹。Codex 可以读取其中的文档、执行工具、修改文件并检查结果。项目里的 `AGENTS.md` 用来保存长期规则，例如公司背景、文件结构、写作风格和操作边界。

一个可执行的任务通常包含六项：

```text
目标：最后要得到什么。
材料：先读取哪些文件、网页或历史资料。
要求：受众、格式、长度、时间范围和重点。
权限：哪些操作可以直接做，哪些必须先确认。
验证：如何核对事实、来源和文件结果。
交付：最终文件放在哪里，还要列出哪些未确认事项。
```

复杂任务先让 Codex 调查和规划。简单任务直接执行。

## 2. 常用命令

在输入框键入 `/` 可以查看当前环境支持的命令。

| 命令 | 用途 |
| --- | --- |
| `/plan` | 调查问题并制定执行方案 |
| `/goal` | 设置持续目标，适合长任务 |
| `/side` | 临时开启支线对话，不打断主任务 |
| `/skills` | 查看和选择已安装的 Skill |
| `/status` | 查看任务状态和上下文用量 |
| `/compact` | 压缩长对话，保留关键上下文 |
| `/model`、`/reasoning` | 根据任务难度调整模型和推理强度 |
| `/permissions` | 查看或调整执行权限 |
| `/mcp` | 查看已经连接的外部工具 |

可用命令会随环境和权限变化，以输入框中的列表为准。

## 3. 让长任务持续推进

多步骤工作可以先用 `/plan` 确认方向，再用 `/goal` 设置完成标准。执行过程中可以继续补充信息或纠正方向。需要临时讨论时用 `/side`，主任务仍保留原来的上下文。

长任务要写清三件事：完成标准、可自主执行的范围、必须暂停确认的情况。对外发送、发布、付款、删除资料和重大业务选择，默认要求人工确认。

## 4. Skills、Plugins 和 MCP

Skill 是一套可复用的工作方法。用 `/skills` 选择，或在任务中写 `$skill-name` 明确调用。Codex 也可以根据任务自动选择匹配的 Skill。

Plugin 用来分发 Skills 和连接器。MCP 让 Codex 访问外部工具与数据。可以简单理解为：Skill 规定怎么做，MCP 提供可以使用的系统。

本仓库附带六个可直接调用的 Skill，以及一个供 Nature Writing 使用的内部依赖包：

| Skill | 适用任务 |
| --- | --- |
| `$agent-reach` | 网页、GitHub 和社交平台调研；社区内容只作为讨论信号 |
| `$shuorenhua` | 清理文章里的模板感和 AI 腔，同时保护事实、数字和术语 |
| `$llm-wiki` | 维护 Codex + Obsidian 的 Markdown 知识库 |
| `$design-geist` | 为网站、仪表盘和开发者工具提供 Geist 风格的前端设计规范 |
| `$academic-figures-drawer` | 生成、审查和导出可编辑的论文框图与方法示意图；默认使用 Tabler outline 图标 |
| `$nature-writing` | 规划和起草 Nature 风格论文正文与首次投稿材料 |

`nature-shared` 随仓库一同提供，但只作为 `$nature-writing` 的共享规则和期刊格式依赖，不应单独调用。

其他高频能力通常以 Skill 或 Plugin 提供：PDF 阅读、Word 文档、表格分析、演示文稿、浏览器操作、邮件与日历、GitHub、长视频或书籍提炼。具体名称取决于本机安装情况，选择建议见 [SKILLS.md](SKILLS.md)。

重复出现的工作适合写成 Skill。流程稳定后再设置定时任务，避免把尚未验证的做法自动化。

## 5. 调研和写作

调研时要求 Codex 区分事实、来源主张、社区讨论和推断，并附原始链接。公开文章可以在事实核对后调用 `$shuorenhua`，减少商业黑话、空总结和模板化表达。

`$shuorenhua` 只负责表达，不负责事实校验。数字、日期、引用、产品名和责任归属应保持不变。

## 6. Codex + Obsidian + LLM Wiki

仓库中的 `obsidian-starter/` 是一个最小知识库模板。用 Obsidian 打开该目录即可浏览；Codex 负责写入和维护 Markdown。

```text
obsidian-starter/
├── AGENTS.md
├── inbox/
├── sources/
└── wiki/
    ├── index.md
    └── log.md
```

`sources/` 保存不改动的原始资料，`wiki/` 保存 Codex 整理的主题页，`index.md` 是知识目录，`log.md` 记录每次导入、查询和检查。

日常只需要三个动作：

- Ingest：读取一个新来源，更新相关页面、索引和日志。
- Query：根据 Wiki 回答问题，引用页面；有长期价值的结论写回 Wiki。
- Lint：检查矛盾、过时内容、断链和孤立页面。

先从少量高价值来源开始。索引和页面摘要足够使用时，不必急着增加向量数据库。

## 7. 自动化和安全边界

适合自动化的任务包括周期性行业简报、资料归档、知识库检查和项目状态汇总。定时任务可以明确调用 Skill。

不要把密钥写进 Prompt、Skill 或仓库。外部网页、邮件和文档都可能包含错误或恶意指令；让 Codex 把它们当作资料，而不是系统命令。任何对外动作都应有清楚的授权范围。

## 快速开始

1. 克隆仓库并在 Codex 中打开。
2. 阅读或修改根目录的 `AGENTS.md`。
3. 输入 `/skills`，确认六个可调用的仓库 Skill 已出现。
4. 从 [PROMPTS.md](PROMPTS.md) 选择一个模板开始；需要其他能力时查看 [SKILLS.md](SKILLS.md)。
5. 用 Obsidian 打开 `obsidian-starter/`，运行第一次 Ingest。

## 资料

- [OpenAI：Codex manual](https://developers.openai.com/codex/codex-manual.md)
- [OpenAI：Slash commands](https://developers.openai.com/codex/reference/slash-commands)
- [OpenAI：Agent Skills](https://developers.openai.com/codex/skills)
- [OpenAI：Automations](https://developers.openai.com/codex/app/automations)
- [Andrej Karpathy：LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

第三方 Skill 的来源和许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 前端设计规范

`$design-geist` 是一份前端设计规范，适合网站、仪表盘、开发者工具和文档站。它规定了 Geist 字体、黑白灰配色、间距、圆角、组件、图标和动效的使用方式，用于实现克制、清晰、偏工程感的界面。它不是 Vercel 官方设计文档。

## 科研框图

`$academic-figures-drawer` 以可编辑 `.drawio` 为源文件，输出 PNG、SVG 和 PDF，并通过尺寸、对齐、论文宽度截图与全局零重叠布线验收。所有语义连线必须使用明确的正交通道和垂直出入端口；检查器会自动审计技能卡、文字标签、容器边框以及线与线之间的交叉、贴边和重叠，任何问题都会直接阻止交付。科学逻辑优先使用 draw.io 原生矢量组件；需要图标时默认检索 MIT 许可的 Tabler outline，只保存实际使用的 SVG。Koboyo 仅在明确要求手绘风格时启用，不与 Tabler 混用。
