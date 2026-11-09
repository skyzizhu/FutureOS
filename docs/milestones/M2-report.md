# M2 验收报告

2026-11-01。**M2 实现与本机自动化验收通过，待用户验收；未进入 M3。**
部署继续采用原生 PostgreSQL、Redis、API、Worker 和 Web，无需 Docker。

## 本次交付

| 范围 | 当前行为 |
|---|---|
| 研究工作流 | M1 信号重新准入 → 互补融合 → 机制链 → 历史类比 → 竞争情景 → 基线/目标检查 → 内部原始草稿 A |
| 独立来源 | 核对事实、原文引用、来源簇和可用时间；至少两个支持信号、两个独立来源簇及完整必要能力才融合；转载不重复计数 |
| 机制与情景 | 两个具名机制模板，包含瓶颈、反向作用、基准/加速/受阻路径、反证和后续观察指标 |
| 历史类比 | 按机制标签选择当时可见的案例，保留成功/失败结果、前提、跨领域差异及不可迁移部分 |
| 数值对照 | 同口径至少三个统计期计算 last-value 持平基线；缺目标、指标或互补证据时降级为 hypothesis |
| 数据建模 | ResearchTopic、ResearchRun、WorldForecast、ForecastVersion 结构和 ForecastDraft；目标可跨运行复用 |
| 冻结与重放 | 冻结具体来源/主张/案例/指标版本及输入、提示词、代码 hash；保存原始叙述和草稿；离线重放不访问供应商 |
| 研究工作台 | 管理员登录、准备 DEMO、编辑 JSON、提交/轮询、阶段结果、历史记录、草稿详情及离线重放 |
| DeepSeek | 服务端有界 JSON 生成，独立开关、调用预留、用量审计、完成响应复用及不确定状态停止自动重试 |

Core 仍只依赖 Pydantic，不导入 HTTP、数据库、Worker 或 UI。独立 wheel 已构建并核对包含 M2 模块。
阶段支持全部生命周期枚举，复查间隔随阶段变化，并受目标期限约束；不提供经过校准的概率。

## 数据库、接口与发布限制

- 本地数据库已迁移到 `0004_m2`，新增10张研究、草稿及关联/调用表。
- 9张研究/草稿/关联表的 UPDATE/DELETE 被数据库触发器阻断；模型调用仅允许一次完成，完成后冻结。
- `forecast_versions` 的 INSERT 被数据库阻断；WorldForecast 当前正式版本必须为空，没有发布 API。
- 核对应用角色不是超级用户，**正式预测版本数量为0**：[数据库记录](evidence/M2-database.json)。
- Pydantic 为唯一契约来源，现有55个域 JSON Schema，并生成 OpenAPI/TypeScript。
- 管理员研究入口为 `/api/v1/admin/research`；提交返回202，使用幂等键，异步执行后轮询。

这些均是未经过 Critic 的内部草稿。`draft_forecast` 表示具备可检验目标的候选草稿，不代表已正式发布。
M3 的独立审查、裁决、A/B 差分和正式发布尚未实现。

## 实际验证

| 命令/检查 | 结果 |
|---|---|
| `make check` | Ruff、格式、ESLint 通过；mypy 51个文件通过；tsc 通过；pytest **173 passed** |
| `npm run build` | Next.js 正式构建通过，包含受保护的研究工作台 |
| `uv run --group local python -m scripts.local_stack --verify` | 原生 PostgreSQL 下 **173 passed**；API/Redis/Worker/幂等 smoke 通过；Playwright **3 passed** |
| `node scripts/verify_bundle.mjs` | 客户端 JS 无演示身份令牌或供应商 Key 配置 |
| 实际 Key 扫描 | 交付文件及客户端 JS 均无实际 Key；`.env` 被忽略且权限0600 |
| `uv build --package futureos-prediction-engine --out-dir .local/dist` | 独立 Python 包构建成功，含全部 M2 工作流模块 |
| 旧代码版本离线重放 | 原真实联调运行经归档 Core 重放，HTTP200、hash 一致、外部调用增加0次 |

证据：[检查](evidence/M2-check.txt) · [Web构建](evidence/M2-build.txt) ·
[原生全栈](evidence/M2-native-stack.txt) · [客户端扫描](evidence/M2-client-bundle.txt) ·
[凭据扫描](evidence/M2-secrets-check.txt) · [Core构建](evidence/M2-engine-build.txt) ·
[归档重放](evidence/M2-archived-live-replay.json)。

测试覆盖互补融合、转载不融合、反证保留、缺目标/数据降级、未来资料与未来统计期拒绝、六种阶段、
指标新修订不改变旧草稿、数据库不可变/禁止发布、权限与幂等、模型响应校验、超时/不确定调用恢复、
完成响应复用、代码变更后的归档重放及工件损坏拒绝。
浏览器覆盖 M0、M1 和 M2；旧 M1 测试的空库时间假设已调整，允许 M2 合成资料共存。
截图已查看：[研究工作台](evidence/M2-research.png)。

延续1项 Starlette TestClient 弃用提示；没有测试失败。GitHub Actions 已更新，但未推送执行，
不声称远程 CI 通过；仓库尚未创建 commit。

## DeepSeek 实际联调

本阶段只执行了一次有界真实模型生成，输入为自编 DEMO 资料：

- 模型 `deepseek-flash`，运行成功，生成内部草稿 A，始终标记 DEMO。
- prompt 1342、completion 432、合计1774 tokens；保存供应商 fingerprint，不推断实际扣费金额。
- 当时离线重放 hash 一致；随后更新 Core 后，再用已归档的原 Core 重放，hash 仍一致。
- 第二次验证没有重新调用模型；脱敏记录：[联调](evidence/M2-deepseek-live.json)、[跨版本重放](evidence/M2-archived-live-replay.json)。

该联调验证连接、结构化输出、持久化和重放，不证明预测准确率，也未重新验证后续提示词版本的真实模型输出。
最新提示词及流程通过 Mock、模拟 HTTP、契约和原生全栈测试。
本机 `LIVE_RESEARCH_ENABLED=true`，仅管理员手动选择 DeepSeek 时调用；页面默认仍为 Mock。
每管理员滚动24小时最多5次模型调用，最多4096输出 tokens，90秒超时，无自动付费重试。
Search/Fetch 沿用 M1 的独立接口与配额。默认配置和 CI 的真实研究开关关闭。

## 本机验收路径

服务已启动，访问 [研究草稿工作台](http://127.0.0.1:3100/admin/research)。

1. 用本机 `DEMO_ADMIN_TOKEN` 登录，默认值见 `.env.example`。
2. 点击“准备 DEMO 研究”，保持 Mock，点击“创建内部草稿”。
3. 检查独立来源、三类情景、历史正反案例、基线60、验证目标以及“未审查 · 禁止正式发布”。
4. 点击“离线重放草稿”，应显示 hash 一致、联网调用0次。

停止用 `make down`；重启用 `make up`。无需在网页输入模型 Key。
运行与备份步骤见 [本地手册](../runbooks/local.md)。

## 已知边界

- 当前只有两个机制模板，能力标签和证据核实依赖人工记录，尚不具备通用因果发现或独立事实审查能力。
- 反证来自库内有范围和数量上限的查询，不能视为已经穷尽所有反对证据。
- 历史时间截断不能排除基础模型训练中的未来知识；没有真实前瞻成绩，准确率不能判断。
- 基线为最多24期的持平对照，不是预测校准、置信区间或经过验证的概率模型。
- 需共同备份数据库、`.local/engine_versions`、`uv.lock` 和兼容 Python 环境；源码归档不保证任意依赖升级兼容。
- `started` 调用状态不明时停止自动重试，需人工核对供应商和任务状态；尚无人工处理界面。
- 身份认证为本地开发方式，公开部署与生产加固仍属后续范围。

决策：[ADR-008](../decisions/ADR-008-m2-frozen-research.md)、[ADR-009](../decisions/ADR-009-m2-deepseek-generation.md)。
本轮停止在 M2，等待用户验收后再进入 M3。
