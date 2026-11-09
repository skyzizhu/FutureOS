# M0 验收报告

日期：2026-11-01。结论：**M0 实现及本机自动化验收通过，待用户验收；未进入 M1。**

## 交付范围

| 验收项 | 结果 | 证据 |
|---|---|---|
| 统一 Monorepo / 模块依赖 | 通过 | apps、services/prediction_engine、workers、packages、infra、fixtures、tests、docs；独立 wheel 已构建 |
| 原生本地基础设施 | 通过 | 实际 PostgreSQL + Redis + API + Worker + Web；无需 Docker 或外部 API Key |
| 核心五对象 / 接口契约 | 通过 | 25 个 JSON Schema（含 DeepSeek 搜索/抓取补充）、OpenAPI、自动 TS 类型；重生成产物完全一致 |
| API / RBAC / ownership | 通过 | 健康检查、DEMO bearer 身份、管理员边界、跨用户 job 404、统一错误和请求日志 |
| Mock 研究任务 | 通过 | 202 → 持久化任务 → Worker → DEMO hypothesis；无正式预测、发信或扣费 |
| 幂等 / 重试 / 恢复 | 通过 | 同键同请求复用、不同输入 409、并发提交和领取、失败恢复、租约到期、最大次数 |
| 数据库首迁移 | 通过 | users/jobs/outbox_events/inbox_processed；真实 PostgreSQL upgrade → downgrade → upgrade |
| Web 壳与浏览器路径 | 通过 | 首页研究演示、认证占位、公共管理状态页；受保护统计通过后端管理员接口 |
| 检查链与 CI 配置 | 本机通过 | Ruff、ESLint、mypy、tsc、pytest、Next build、Playwright；远程 CI 尚未运行 |
| 既有搜索 Agent 评估 | 已完成 | ADR-004；只读评估，没有开启真实搜索或复制整个 Agent |

用户在实施中明确改为原生部署并最终选择 PostgreSQL，因此 Docker Compose 不作为本次交付或验收要求。
计划第 7.2 节目录边界不变；16 个 Core 子模块中尚未实现的能力只保留空包，不声称业务完成。

## 可操作成果

本机已配置 .env（0600）、项目内 PostgreSQL/Redis 安装及数据目录。启动：

```bash
make up
# Web: http://127.0.0.1:3100
# API: http://127.0.0.1:8100/api/v1/docs
# 停止：另一个终端 make down，或前台 Ctrl-C
```

首页点击“运行 DEMO 任务”，查看 queued/running/succeeded 与明显的 DEMO / hypothesis 标签。
不需要外部密钥。API 文档可用本地演示令牌验证 user/admin 权限，令牌见 .env.example。
Web 的代理身份只存在于服务端，已扫描客户端 JS 确认没有演示身份令牌或供应商密钥配置。

![M0 DEMO 验收画面](evidence/M0-demo.png)

## 实际执行与原始输出

| 命令 | 实际结果 |
|---|---|
| `uv sync --locked` / `npm ci`（依赖安装与锁文件） | 安装成功；本地服务另使用 `--group local` |
| `make contracts` / 重生成 hash 比较 | 23 个 schema + OpenAPI + TS；产物无漂移 |
| `make check` | Ruff / 格式检查 / ESLint 通过；mypy 34 个源文件通过；tsc 通过；pytest **49 passed** |
| `npm run build` | Next.js 正式构建通过，首页及 5 类页面/路由生成成功 |
| `node scripts/verify_bundle.mjs` | PASS：客户端无 DEMO 身份令牌或供应商 Key 配置 |
| `uv build --package futureos-prediction-engine --out-dir .local/dist` | 独立 sdist/wheel 成功，检查包含 contracts 和 workflow |
| `uv run --group local python -m scripts.local_stack --verify` | 实际 PostgreSQL：**49 passed**；readiness / 幂等 replay / Worker smoke 通过；心跳通过；Playwright **1 passed** |

原始输出：[检查](evidence/check.txt)、[构建](evidence/web-build.txt)、[本地全栈](evidence/native-stack.txt)、
[客户端扫描](evidence/client-bundle.txt)、[独立包构建](evidence/engine-build.txt)。
浏览器截图已人工查看，DEMO 标签、任务成功结果、布局均正常。
没有把“配置了 CI”写成“远程 CI 已通过”：当前没有推送或运行 GitHub Actions。

pytest 有 1 项 Starlette 对 httpx TestClient 的弃用提示，不影响本轮测试；后续升级时切换测试传输。
本机 Node 26.7.0（x64/Rosetta）构建有性能提示；建议新机器用 Node 24 LTS，CI 已使用 24。
Playwright 有 NO_COLOR/FORCE_COLOR 提示，不影响测试。未声称负载性能或生产 SLO 达标。

## 迁移与数据隔离

- Alembic：`0001_m0`，已对本地 PostgreSQL 演示库执行，当前 revision 确认 `0001_m0`。
- 专用库：`futureos_m0_demo` / `futureos_m0_test`。应用角色 `futureos_local`，已验证不是超级用户。
- 测试库独立，测试清理前检查库名以 `_test` 结尾；快速测试使用临时 SQLite。
- DEMO 用户种子三种身份，重复执行不增加重复身份。
- 不存在 M1 证据/信号、M2 预测、M3 审查、M4 报告和 M6 计费业务表；不以 DTO 冻结替代后续 DB 不可变约束。
- 用户变更部署方案后，已清理本次创建的 MariaDB 两个测试/演示库及专用账号，未改动既有业务库。
- PostgreSQL 数据在 `.local/postgres-demo`，Redis 在 `.local/redis-demo.rdb`，默认不启动系统自启服务。

本地实际版本：PostgreSQL 16.2、Redis **6.2.14**；FastAPI 0.162.0、Pydantic 2.14.2、SQLAlchemy 2.0.55、Alembic 1.20.1、Next.js 16.4.3。
完整依赖以 uv.lock / package-lock.json 为准。便携数据库构建限本地隔离 DEMO；线上使用已维护更新的服务版本。

## Provider 差异与尚未实现项

LLM/Search/Fetch/Data/Email/Payment/Storage 七类端口及 Mock 已提供。
LLM 固定合成输出，Search 返回 example.invalid，Data 返回 DEMO_DATA；Email 只接受 example.invalid 收件人且不发网络请求，
Payment 只使用 DEMO 地址和测试签名、不建立权益，Storage 是内存 Mock。当前演示不调用真实供应商；DeepSeek 适配器已通过离线 HTTP 测试。
超时/有限重试/实例速率间隔/熔断可测试；全局供应商预算、分布式限流、完整消息总线和通知在后续阶段实现。

基础鉴权为本地 DEMO 固定身份，不是生产注册/会话。非 DEMO 或 production 配置会拒绝启动。
未实现真实来源导入、时间 vintage 查询、预测生成、独立 Critic、裁决、版本发布、个人报告、权益扣费、邮件和真实支付。
**没有真实前瞻预测证据，预测准确率尚不能判断。**

用户后续指定搜索与抓取统一采用 DeepSeek。Search/Fetch 适配器及 Mock HTTP 测试已实现，
保留未知时间和 unverified 标记、不支持伪历史 as-of、不启用真实调用。
详见 [ADR-005](../decisions/ADR-005-deepseek-web.md)。原 Sky 仓库仅保留缓存/观测思路参考。

## 决策与后续前提

- ADR-001：单仓、独立 Core 与契约唯一来源。
- ADR-002：用户选择原生 PostgreSQL/Redis，替代 Docker。
- ADR-003：持久化作业 / DEMO 权限和有限 Provider 调用策略。
- ADR-004：Sky 搜索 Agent 历史复用评估。
- ADR-005：用户指定 DeepSeek Search/Fetch；当前适配器离线验证，M0 保持 Mock。

变更文件包含代码、锁文件、迁移、CI、契约生成物、测试、启动脚本和文档；本仓库初始为空，尚未创建 commit。
M0 用户验收前停止。进入 M1 后再建立 Source/SourceVersion/EvidenceClaim/Indicator/ObservationVintage/Signal 及 as-of 导入查询，
优先处理同源去重、来源许可、统计发布时间和历史视图不变性；真实 Provider 接入需独立验收。

## 2026-11-01 补充：DeepSeek Search / Fetch

按用户后续要求，搜索与抓取供应商统一改为 DeepSeek；原 Tavily/DDGS/本机抓取方案不再作为接入计划。
新增 `DeepSeekWebProvider`、`FetchProvider`、`MockFetchProvider`、`SearchHitV1`、`FetchedPageV1`。
JSON Schema / TS 契约已更新为 **25** 个；HTTPX 从测试依赖提升为服务端运行依赖。
未知发布时间保留 null，所有命中/抓取正文为 unverified；不虚构 available_at、不将排名当作概率、
不通过实时检索冒充历史 as-of。适配器不会自动启用；仅提供 `.env.example` 的服务端 Key 占位。

本轮实际执行：

- `npm run contracts`：25 个 JSON Schema 及 TS 类型重新生成。
- `make check`：Ruff / ESLint / mypy（35 个源文件）/ tsc 通过；**90 passed**。
- `uv run --group local python -m scripts.local_stack --verify`：真实 PostgreSQL 下 **90 passed**，
  健康检查 / 幂等 replay / Worker / 心跳通过，浏览器 E2E **1 passed**。
- `node scripts/verify_bundle.mjs`：客户端无 DEMO 身份令牌或供应商 Key 配置，已加入 DEEPSEEK_API_KEY 检查。

输出：[本轮检查](evidence/deepseek-check.txt)、[本轮本地全栈](evidence/deepseek-native-stack.txt)、
[本轮客户端扫描](evidence/deepseek-client-bundle.txt)。上文 49 项测试是更换供应商前的基线记录。

DeepSeek 的接口测试全部使用 httpx.MockTransport，不读取真实 Key、不访问供应商、不产生请求费用。
尚未进行真实接口的授权、余额、联网质量或历史证据验收。生产认证和真实研究仍未启用；本次未进入 M1。
决策及官方依据见 [ADR-005](../decisions/ADR-005-deepseek-web.md)。
