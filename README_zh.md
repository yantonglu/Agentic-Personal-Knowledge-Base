# Agentic Personal Knowledge Base

[![README](https://img.shields.io/badge/README-English-blue)](README.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个面向 Obsidian 的 agentic vault 架构，用于构建可自维护的个人知识库。

这个项目不只是一个文件夹模板。它为 AI Agent 定义了一套 rules-first 的操作系统：新文件从 inbox 进入，分类由显式类别规则驱动，笔记通过模板归一化，多格式源文件先转换再整理，索引由 Dataview 自动生成，最终由校验脚本检查结构和元数据。

## 设计亮点

很多 AI 辅助笔记工作流依赖一次性 prompt。少量文件时这可行，但随着 vault 增长，很容易变得不可控。这个骨架把 vault 本身设计成 Agent 的控制平面。

- **规则驱动路由：** `RULES.md` 和各类别 `README.md` 构成路由表。Agent 分类时读取明确条件，而不是凭上下文猜测。
- **安全兜底路径：** 不确定的文件留在 `00-Inbox/`，并标记为 `status: needs-review`，避免模糊判断污染知识库。
- **模板化归一：** `.templates/BASE_TEMPLATE.md` 和类别 `.TEMPLATE.md` 将原始内容整理成带 frontmatter、状态、标签、来源、备注和关联链接的稳定 Markdown。
- **多格式入库：** PDF、Office、HTML、CSV、JSON、EPUB、图片、音频和压缩包等源文件可先用 MarkItDown 转换，再由 Agent 清理和组织。
- **自动排版与索引：** Agent 维护笔记元数据，Dataview 根据 frontmatter 渲染索引，不再维护易漂移的手工目录表。
- **确定性维护：** `.kb-maintenance/validate_vault.py` 检查根文件、类别结构、模板、frontmatter、标签、附件链接、文件名和进度日志结构。
- **个性化上下文层：** `SOULS.md` 被设计成私有 vault 中的紧凑用户画像层，让 Agent 获得长期偏好和兴趣上下文，而不需要每次任务都重新遍历整个 vault。

## 工作流

```text
00-Inbox/
  -> Detect
  -> Read
  -> Classify
  -> Convert
  -> Format
  -> Move
  -> Dataview Index
  -> Validate
```

每一步职责清晰：

| Step | Responsibility |
| --- | --- |
| Detect | 发现 inbox 中的新文件并跳过系统文件 |
| Read | 在决策前完整读取源内容 |
| Classify | 根据类别规则路由文件 |
| Convert | 对非 Markdown 源文件使用 MarkItDown |
| Format | 应用基础模板和类别模板 |
| Move | 将笔记和附件放入稳定位置 |
| Index | 用 Dataview 查询 frontmatter，而不是手工编辑目录 |
| Validate | 运行确定性的结构和元数据校验 |

## 仓库结构

```text
.
├── README.md              # 英文 GitHub 介绍
├── README_zh.md           # 中文说明
├── AGENTS.md              # Agent 主入口
├── CLAUDE.md              # 指向 AGENTS.md 的软链接
├── GEMINI.md              # 指向 AGENTS.md 的软链接
├── RULES.md               # 路由、格式化和维护规则
├── CONTENTS.md            # Dataview 自动索引
├── SOULS.md               # 私有 vault 中的用户画像占位
├── .templates/            # 笔记模板
├── .kb-maintenance/       # 维护脚本
├── 01-Example/            # 合成示例分类
├── assets/                # 附件仓库
└── 00-Inbox/              # 待处理文件入口
```

`README.md` 是项目介绍。Agent 应从 `AGENTS.md` 开始读取，`RULES.md` 是详细操作规则。

## 快速开始

```bash
git clone <repository-url>
cd Agentic-Personal-Knowledge-Base
python3 .kb-maintenance/validate_vault.py --strict-tags --strict-names
```

预期输出：

```text
VALIDATION_STATUS=PASS
```

如需处理 PDF、Word、HTML 等多格式源文件，可选安装：

```bash
pip install "markitdown[all]"
```

如需在 Obsidian 中使用自动索引，请安装 Dataview 社区插件。

## 创建分类

仓库中的 `01-Example/` 展示了类别契约。普通类别结构如下：

```text
NN-CategoryName/
├── README.md
└── .TEMPLATE.md
```

类别 `README.md` 应包含 `Agent Classification Criteria` 小节。这个小节会把类别变成自动路由层。

## License

MIT
