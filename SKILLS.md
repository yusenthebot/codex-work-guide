# 高频 Skills 与功能

Skill 负责工作方法，Plugin 负责安装和分发，MCP 或 Connector 负责连接外部系统。名称和可用范围取决于本机安装与账户权限。

## 仓库附带

| Skill | 什么时候用 | 说明 |
| --- | --- | --- |
| `$agent-reach` | 调研网页、GitHub 或社交平台 | 仓库附带的是 Skill；平台 CLI、登录态和 cookies 需按上游文档配置 |
| `$shuorenhua` | 修改公开文章、汇报和说明文字 | 保留事实、术语、数字和责任归属，只处理表达 |
| `$llm-wiki` | 管理 Obsidian Markdown 知识库 | 支持 ingest、query 和 lint；每次来源录入必须包含本地图片和来源说明 |
| `$design-geist` | 设计网站、仪表盘和开发者工具 | 使用 Geist 字体、黑白灰配色和克制的组件规范 |
| `$academic-figures-drawer` | 制作、修改或审查论文框图与方法示意图 | 以 `.drawio` 为源文件，默认使用 Tabler outline；强制正交布线，并对线框碰撞、边框贴线、线线交叉和重叠执行全局零容忍检查 |
| `$nature-writing` | 规划或起草 Nature 风格论文与首次投稿材料 | 按论文类型、章节、语言和目标期刊加载对应规则 |

打开本仓库后，Codex 会从 `.agents/skills/` 发现这些 Skill。若没有出现，重新打开任务或重启 Codex。

`nature-shared` 是 `$nature-writing` 的内部依赖包，不作为独立工作流调用。它与主 Skill 一起保存在 `.agents/skills/`，确保仓库克隆后相对引用仍然有效。

## 常用扩展

| 能力 | 常见 Skill 或 Plugin | 适用工作 |
| --- | --- | --- |
| PDF | `$pdf` | 读取、制作和检查 PDF |
| Word | `$documents` | 起草、修改和审阅 `.docx` |
| 表格 | `$spreadsheets` | 分析数据，生成和检查工作簿 |
| 演示文稿 | `$presentations` | 制作或修改 PowerPoint |
| 浏览器 | `$playwright` 或浏览器控制 Skill | 操作需要真实页面交互的网站 |
| GitHub | GitHub Plugin | 查看仓库、Issue、PR 和 CI |
| 邮件与日历 | 对应 Plugin/Connector | 搜索、整理和起草；发送或改期前确认 |
| 长内容提炼 | `$cangjie-skill` | 把书籍、课程、播客或长视频中的方法整理成可复用 Skill |

当一项工作反复出现，先记录稳定步骤和验收标准，再创建团队 Skill。需要访问业务系统时配套 MCP；执行频率稳定后再设为 Automation。

## 调用方式

输入 `/skills` 浏览已安装 Skill，或在任务中直接写 `$skill-name`。关键任务建议明确指定，避免自动匹配到相近但不合适的流程。

使用外部 Plugin、MCP 或 Connector 前，确认数据会发送到哪个服务、使用什么账户、允许哪些写操作。
