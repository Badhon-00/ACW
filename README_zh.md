# Awesome Claude Skills — 中文版

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Apache License 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

> 精选的实用 Claude Skills（技能）、资源和工具集合，用于在 **Claude.ai**、**Claude Code** 和 **Claude API** 中定制 Claude AI 的工作流程。

[English](./README.md) | [한국어](./README_ko.md) | **简体中文**

---

## 📖 目录

- [什么是 Claude Skill？](#什么是-claude-skill)
- [快速开始](#快速开始)
- [技能分类](#技能分类)
  - [📄 文档处理](#-文档处理)
  - [💻 开发与代码工具](#-开发与代码工具)
  - [📊 数据与分析](#-数据与分析)
  - [📢 商业与营销](#-商业与营销)
  - [✍️ 沟通与写作](#️-沟通与写作)
  - [🎨 创意与媒体](#-创意与媒体)
  - [⚡ 生产力与组织](#-生产力与组织)
  - [🤝 协作与项目管理](#-协作与项目管理)
  - [🔒 安全与系统](#-安全与系统)
  - [🔌 应用自动化（Composio）](#-应用自动化composio)
- [如何贡献](#如何贡献)
- [许可证](#许可证)

---

## 什么是 Claude Skill？

Claude **Skill（技能）** 是可定制的工作流程，能教会 Claude 如何根据你的具体需求执行特定任务。每个 Skill 是一个包含 `SKILL.md` 文件的文件夹，其中包含角色设定、标准化操作流程（SOP）以及外部工具权限的定义。

**核心公式：Skill = 角色设定 + 标准化流程 + 工具权限**

### Skill 文件夹结构

```
skill-name/
├── SKILL.md          # 必需：YAML 前置元数据 + Markdown 指令说明
├── scripts/          # 可选：辅助脚本（Python、Bash 等）
├── references/       # 可选：参考资料文件
├── templates/        # 可选：文档模板
└── assets/           # 可选：资源文件
```

### 在何处使用

| 平台 | 使用方法 |
|------|----------|
| **Claude.ai** | 点击聊天界面中的 🧩 技能图标，从市场添加或上传自定义技能 |
| **Claude Code** | 将技能文件夹放入 `~/.config/claude-code/skills/` 或项目中的 `.claude/skills/` |
| **Claude API** | 在 API 调用中通过 `skills=["skill-id"]` 参数传递 |

---

## 快速开始

### 安装 Connect 插件（连接 500+ 应用）

```bash
# 1. 安装插件
claude --plugin-dir ./connect-apps-plugin

# 2. 运行设置
/connect-apps:setup

# 3. 重启 Claude
exit
claude
```

获取免费 API 密钥：[dashboard.composio.dev](https://dashboard.composio.dev)

### 手动安装单个 Skill（Claude Code）

```bash
# 克隆仓库
git clone https://github.com/ComposioHQ/awesome-claude-skills.git

# 复制技能文件夹到 Claude Code 技能目录
mkdir -p ~/.config/claude-code/skills/
cp -r skill-name ~/.config/claude-code/skills/

# 启动 Claude Code
claude
```

### 使用 npm 安装

```bash
npx skills add https://github.com/ComposioHQ/awesome-claude-skills --skill skill-name
```

---

## 技能分类

本仓库包含 **100+ 个技能**，分为以下类别。每个技能都配有详细的 `SKILL.md` 文件，包含完整的设置和使用说明。

### 📄 文档处理

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **docx** | 创建、编辑、分析 Word 文档，支持修订标记、批注和格式设置 | Anthropic |
| **pdf** | 提取文本、表格、元数据，合并和注释 PDF 文件 | Anthropic |
| **pptx** | 读取、生成和调整幻灯片、布局和模板 | Anthropic |
| **xlsx** | 电子表格操作：公式、图表、数据转换 | Anthropic |
| **Markdown to EPUB Converter** | 将 Markdown 文档和聊天摘要转换为专业的 EPUB 电子书文件 | [@smerchek](https://github.com/smerchek) |
| **Master Claude for Legal** | 法律团队技能包：NDA 分类、多方版本差异对比、引用验证、会议简报。含 10 份参考文档和 3 个律所模板 | [@sboghossian](https://github.com/sboghossian) |

### 💻 开发与代码工具

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **artifacts-builder** | 使用 React、Tailwind CSS 和 shadcn/ui 创建复杂的 claude.ai HTML 构件 | Anthropic |
| **aws-skills** | AWS 开发：CDK 最佳实践、成本优化、无服务器/事件驱动架构 | @zxkane |
| **Changelog Generator** | 从 git 提交自动生成面向用户的变更日志和发布说明 | ComposioHQ |
| **Claude Code Terminal Title** | 为每个 Claude Code 终端窗口动态设置描述性标题 | @bluzername |
| **D3.js Visualization** | 教 Claude 生成 D3 图表和交互式数据可视化 | @chrisvoncsefalvay |
| **FFUF Web Fuzzing** | 集成 ffuf 网络模糊测试工具，用于漏洞分析 | @jthack |
| **iOS Simulator** | 使 Claude 能够与 iOS 模拟器交互，用于测试和调试 iOS 应用 | @conorluddy |
| **jules** | 将编码任务委派给 Google Jules AI 代理进行异步处理 | @sanjay3290 |
| **LangSmith Fetch** | 从 LangSmith Studio 获取追踪信息，调试 LangChain/LangGraph 代理 | @OthmanAdi |
| **MCP Builder** | 指导创建高质量的 MCP 服务器，用于将外部 API 与 LLM 集成 | ComposioHQ |
| **Playwright Browser Automation** | 通过 Playwright 实现浏览器自动化，用于测试和验证 Web 应用 | @lackeyjb |
| **prompt-engineering** | 教授提示工程技术，包括 Anthropic 最佳实践 | NeoLabHQ |
| **pypict-claude-skill** | 使用 PICT 成对组合测试方法设计测试用例 | @omkamal |
| **software-architecture** | 实现整洁架构、SOLID 原则和设计最佳实践 | NeoLabHQ |
| **subagent-driven-development** | 派遣独立子代理，带代码审查检查点的开发流程 | NeoLabHQ |
| **test-driven-development** | 在编写实现代码之前执行 TDD 工作流程 | @obra/superpowers |
| **using-git-worktrees** | 创建隔离的 git worktree，带安全性验证 | @obra/superpowers |
| **Webapp Testing** | 使用 Playwright 测试本地 Web 应用，进行 UI 验证和截图 | ComposioHQ |
| **great_cto** | 7 个专业子代理协调完整 SDLC 流程，支持 13 个合规框架 | @avelikiy |
| **agnix** | AI 代理配置检查工具——156 条规则，自动修复，LSP 支持 | 社区 |
| **claude-starter** | 生产就绪的配置模板，含 40 个自动激活技能，覆盖 8 个领域 | 社区 |
| **spartan-ai-toolkit** | 工程工作流命令：质量门禁、TDD 强制、原子提交 | 社区 |
| **Playwright Skill** | 结构化 SKILL.md，含测试自动化工作流，兼容 MCP | 社区 |
| **debug-skill** | 真正的调试器——断点、单步执行、变量检查、堆栈跟踪 | 社区 |

### 📊 数据与分析

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **CSV Data Summarizer** | 自动分析 CSV 文件并生成全面的数据洞察与可视化 | @coffeefuelbump |
| **deep-research** | 使用 Gemini Deep Research 代理进行自主多步骤研究 | @sanjay3290 |
| **postgres** | 对 PostgreSQL 执行安全的只读 SQL 查询，支持多连接 | @sanjay3290 |
| **mysql** | 对 MySQL 数据库执行安全的只读 SQL 查询 | 社区 |
| **mssql** | 对 Microsoft SQL Server 数据库执行安全的只读 SQL 查询 | 社区 |
| **root-cause-tracing** | 追踪执行深处的错误，找到原始触发原因 | @obra/superpowers |
| **recursive-research** | 跨领域的博士级递归研究，含来源分层和磁盘检查点 | @Anjos2 |
| **notebooklm** | 查询和管理 Google NotebookLM 笔记本 | 社区 |
| **kaggle-skill** | 完整 Kaggle 集成：竞赛报告、数据集下载、笔记本执行 | 社区 |
| **claude-ecom** | 从订单 CSV 生成完整电商业务分析报告 | 社区 |
| **gh-star-history** | 可视化并比较 GitHub 星标历史，支持交互式图表 | 社区 |
| **coinpaprika-api** | 加密市场数据：12,000+ 币种，350+ 交易所，OHLCV 历史价格 | 社区 |
| **x-twitter-scraper** | X/Twitter 数据提取：推文搜索、用户查询、参与度指标 | 社区 |
| **chainaware-behavioral-prediction** | 钱包行为预测、欺诈检测、Rug Pull 检测 | 社区 |

### 📢 商业与营销

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **Brand Build Skills** | 59 项技能库：品牌、设计、内容、SEO、开发、运营、增长、研究 | @rampstackco |
| **Brand Guidelines** | 应用 Anthropic 官方品牌色和字体，确保视觉一致性 | ComposioHQ |
| **Competitive Ads Extractor** | 提取和分析竞争对手广告，了解其信息和创意策略 | ComposioHQ |
| **Domain Name Brainstormer** | 生成创意域名并检查 .com/.io/.dev/.ai 等 TLD 的可用性 | ComposioHQ |
| **Internal Comms** | 撰写内部沟通文档：全员更新、新闻简报、FAQ、状态报告 | ComposioHQ |
| **Lead Research Assistant** | 通过分析产品和目标公司识别和筛选高质量潜在客户 | ComposioHQ |
| **copywriting** | 专业转化文案撰写，使用经过验证的框架 | 社区 |
| **seo-audit** | 网站技术和页面 SEO 审查 | 社区 |
| **ai-seo** | AI 搜索引擎优化，提升在 AI 搜索结果中的可见度 | 社区 |
| **programmatic-seo** | 大规模 SEO 页面生成 | 社区 |
| **content-strategy** | 内容策划和话题研究 | 社区 |
| **cold-email** | B2B 外联邮件序列创建和优化 | 社区 |
| **ad-creative** | 广告标题和创意生成 | 社区 |
| **ab-test-setup** | A/B 测试和营销实验规划 | 社区 |
| **pricing-strategy** | SaaS 和产品定价与变现策略 | 社区 |
| **launch-strategy** | 产品发布规划和市场进入策略 | 社区 |
| **social-content** | 跨平台社交媒体内容创作 | 社区 |
| **lead-magnets** | 创建和优化引流磁石 | 社区 |
| **referral-program** | 推荐和联盟计划设计 | 社区 |
| **sales-enablement** | B2B 销售资料和演示文稿制作 | 社区 |
| **analytics-tracking** | 分析工具设置和测量实施 | 社区 |
| **marketing-psychology** | 行为科学在营销文案和 UX 中的应用 | 社区 |
| **@clawfu/mcp-skills** | 169 个专家来源的营销技能（MCP 服务器） | @clawfu |
| **devmarketing-skills** | 33 个开发者营销技能：HN 策略、教程、Reddit、开发者 SEO | 社区 |

### ✍️ 沟通与写作

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **article-extractor** | 从 URL 提取文章内容，清理格式，生成结构化摘要 | ComposioHQ |
| **brainstorming** | 结构化头脑风暴：发散思考、聚类分析、优先级排序 | ComposioHQ |
| **Content Research Writer** | 深度内容研究：搜集资料、交叉验证、生成结构化长文 | ComposioHQ |
| **Meeting Insights Analyzer** | 分析会议记录的行为模式：冲突规避、发言比例、填充词、领导风格 | ComposioHQ |
| **Twitter Algorithm Optimizer** | 优化 Twitter 内容策略，提升算法推荐效果 | ComposioHQ |

### 🎨 创意与媒体

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **Canvas Design** | 在 PNG 和 PDF 中创建精美视觉艺术作品，适用于海报、设计和静态作品 | ComposioHQ |
| **imagen** | 使用 Google Gemini 图像生成 API 生成 UI 原型、图标和插图 | @sanjay3290 |
| **Image Enhancer** | 提升图片和截图的分辨率、锐度和清晰度 | ComposioHQ |
| **Slack GIF Creator** | 创建针对 Slack 优化的动画 GIF，含大小验证 | ComposioHQ |
| **Theme Factory** | 为幻灯片、文档、报告和 HTML 落地页应用专业主题 | ComposioHQ |
| **Video Downloader** | 从 YouTube 等平台下载视频供离线观看或存档 | ComposioHQ |
| **youtube-transcript** | 获取 YouTube 视频转录文本并准备摘要 | — |
| **swiftui-design-skill** | SwiftUI 前端设计技能，支持 Claude Code/Cursor/Codex/OpenCode | @wholiver |
| **Pixelbin-Media-Generation** | 通过 85+ API 生成和编辑图片与视频 | — |

### ⚡ 生产力与组织

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **File Organizer** | 智能整理文件，识别重复项，优化组织结构 | ComposioHQ |
| **Invoice Organizer** | 自动整理发票和收据，用于税务申报准备 | ComposioHQ |
| **kaizen** | 应用持续改进方法，基于日本 Kaizen 理念和精益方法论 | — |
| **n8n-skills** | 使 AI 助手能够直接理解和操作 n8n 工作流 | @haunchen |
| **Raffle Winner Picker** | 从列表或表格中随机抽选获奖者，使用加密安全的随机算法 | ComposioHQ |
| **solo-skills** | 7 个双语（英文+中文）技能：独立开发者必备——发布推文、客户邮件、决策框架、事后复盘 | — |
| **Tailored Resume Generator** | 分析职位描述并生成定制简历，最大化面试机会 | ComposioHQ |
| **ship-learn-next** | 帮助迭代确定下一个构建或学习目标 | michalparkola |
| **tapestry** | 关联和汇总相关文档，构建知识网络 | michalparkola |

### 🤝 协作与项目管理

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **git-pushing** | 自动化 Git 操作和仓库交互 | mhattingpete |
| **google-workspace-skills** | Google Workspace 集成套件：Gmail、日历、Chat、文档、表格、幻灯片和云端硬盘 | @sanjay3290 |
| **outline** | 在 Outline Wiki 实例中搜索、阅读、创建和管理文档 | @sanjay3290 |
| **review-implementing** | 评估代码实现计划并确保与规范一致 | mhattingpete |
| **test-fixing** | 检测失败的测试并提出补丁或修复方案 | mhattingpete |

### 🔒 安全与系统

| 技能名称 | 描述 | 作者 |
|---------|------|------|
| **computer-forensics** | 数字取证分析和调查技术 | mhattingpete |
| **file-deletion** | 安全文件删除和数据清除方法 | mhattingpete |
| **metadata-extraction** | 提取和分析文件元数据，用于取证目的 | mhattingpete |
| **threat-hunting-with-sigma-rules** | 使用 Sigma 检测规则进行威胁狩猎和安全事件分析 | @jthack |

### 🔌 应用自动化（Composio）

通过 Composio 集成了 **78 个 SaaS 应用** 的自动化工作流，涵盖以下领域：

| 类别 | 应用 |
|------|------|
| **CRM** | Salesforce、HubSpot、Pipedrive、Zoho |
| **项目管理** | Jira、Linear、Notion、Asana、Monday、Trello |
| **沟通** | Slack、Discord、Teams |
| **邮箱** | Gmail、Outlook |
| **代码与 DevOps** | GitHub、GitLab、Vercel、Sentry、Datadog、Supabase |
| **存储** | Google Drive、Dropbox、Box |
| **电子表格** | Airtable、Google Sheets |
| **日历** | Calendly、Google Calendar |

> 查看完整列表请访问 [Composio 集成页面](https://composio.dev/integrations)

---

## 如何贡献

我们欢迎所有贡献！请遵循以下步骤：

1. **基于真实用例** — 你的技能应解决一个实际问题
2. **检查是否重复** — 查看已有技能，避免重复
3. **遵循技能模板** — 使用标准的 `SKILL.md` 结构（YAML 前置元数据 + Markdown 指令）
4. **跨平台测试** — 在 Claude.ai、Claude Code 和 Claude API 上验证
5. **提交清晰的 PR** — 在 Pull Request 中详细描述你的技能和用例

### 提交 PR 的规范

- PR 标题应简洁明了，例如：`docs: add Chinese README translation`
- 如果引用相关 Issue，请在 PR 描述中添加 `Closes #issue-number`
- 确保所有链接有效，格式正确

### 行为准则

本项目采用贡献者契约行为准则。所有参与者都应保持尊重和包容的沟通方式。

---

## 许可证

本项目采用 **Apache License 2.0** 许可证。详情请参阅 [LICENSE](./LICENSE) 文件。

> 注意：本仓库中的个别技能可能拥有独立的许可证。使用前请检查各技能文件夹中的特定许可信息。

---

**由 [ComposioHQ](https://github.com/ComposioHQ) 维护 · 🌟 如果这个项目对你有帮助，请给它一个星标！**
