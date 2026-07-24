# Lanverse

Lanverse AI 短剧制作平台统一仓库。

项目规范初始化自 [`StephenQiu30/stephen-codex`](https://github.com/StephenQiu30/stephen-codex)。Git 根目录已经统一到本目录，当前仅保留治理文件和正式文档，尚未生成业务代码。设计接受后，应用按根目录 `backend/`、`frontend/`、`deploy/` 组织；首发技术基线见 [`TCR-001`](docs/requirement/TCR-001-平台技术栈与总体架构约束需求规格说明书.md)，总体方案见 [`ARCH-001`](docs/design/ARCH-001-AI短剧制作平台总体架构设计.md)，模块职责与服务协作见 [`ARCH-007`](docs/design/ARCH-007-业务模块边界与服务协作设计.md)。实现需先接受 Design/PRD 并形成可执行 Plan，完成后再按 [`AGENTS.md`](AGENTS.md) 回填 Acceptance。

## 接受后的目标目录

```text
Lanverse/
├── backend/   # NestJS API、Temporal Workflow/Worker、AI 与媒体适配
├── frontend/  # Next.js Web 创作、审片与运营工作台
├── deploy/    # 环境、IaC、部署和观测配置
└── docs/      # Requirement、Design、PRD、Plan、Acceptance 与 Operations
```

API 与 Worker 同属 `backend/`，但独立构建、部署和扩缩；当前不会在 Design 被接受并形成可执行 Plan 前创建空应用目录。
