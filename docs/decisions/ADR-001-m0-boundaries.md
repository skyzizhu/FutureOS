# ADR-001：单仓、单研究工作流与契约唯一来源

状态：已采用。日期：2026-11-01。

使用计划 7.2 路径，Python 3.12 + uv workspace，Next.js + TypeScript / npm workspaces；
实际兼容版本以 uv.lock/package-lock.json 为准。Core 是可独立构建的 setuptools 包，只依赖 Pydantic。
选择少量明确端口和确定性 Mock 工作流，避免 M0 建立独立 Agent 集群。

Pydantic 是唯一 DTO 来源。脚本导出 JSON Schema、OpenAPI，再生成 domain / API TS 声明。
不为尚未实现的产品路由生成虚假可调用 API。CI 重生成后检查 git diff。
版本化报告、Critic / 拐点 / 权益当前只提供契约，后续迁移按 18.7 顺序。

参考：[Next.js 安装](https://nextjs.org/docs/app/getting-started/installation)、
[uv 锁定](https://docs.astral.sh/uv/concepts/projects/sync/)。
