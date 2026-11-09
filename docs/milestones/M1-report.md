# M1 验收报告

2026-11-01。**M1 实现及本机自动化验收通过，待用户验收；未进入 M2。**
M0 已由用户验收。用户授权继续 M1、配置 DeepSeek Key，并进行少量真实连通性验证。

## 本次交付

| 范围 | 实现与证据 |
|---|---|
| 来源/版本 | 稳定 URL 身份、追加写的 SourceVersion、保留文本 hash、许可/访问方式、公开/发生/可用/采集/修订时间 |
| 证据主张 | fact/opinion/hypothesis 分类；原文片段、定位、支持/反对/背景、人工核实者/说明/时间；引用不匹配时拒绝 |
| 来源去重 | URL 规范化、文本 hash、声明原文、近似转载分簇；DEMO/REAL 分离；三篇转载只计一个独立来源簇 |
| 指标/vintage | 定义版本化、统计期、发布时间、可用时间、来源版本 FK；修订追加，旧 as-of 不变 |
| 信号基础 | 已核实且时间有效的 fact → 确定性关键词候选；默认 unknown 阶段，可人工标记；12领域字典 |
| 历史案例 | 当时事件与事后结果分开存储，按 known_at/as_of 隔离；成功/失败合成夹具各一条 |
| DeepSeek | 管理员手动 Search/Fetch；Key 仅服务端；访问审计、每次一次上游请求、请求预算及错误处理 |
| 管理页面 | /admin/sources：主动管理员登录、搜索/抓取预览、JSON/文件导入、来源与信号查看、as-of 过滤、退出 |
| 向后兼容 | M0 DEMO 研究、任务幂等、Worker、用户隔离和 API 健康检查继续通过 |

目录继续遵循计划 7.2，未新增独立 Agent 集群或 M2–M6 业务表。
主要代码：services/prediction_engine/{contracts,ingestion,evidence,signal_detection}、infra/{db,evidence_repository,providers}、
apps/api/evidence.py、apps/web/app/admin/sources、迁移、契约生成物、测试与 fixtures/m1。

## 数据库与契约

已执行：

- `0002_m1`：新增11张 M1 表（来源簇/来源/版本/主张/指标/vintage/信号/关联/历史案例/案例事件/访问审计）。
- `0003_m1_fk_indexes`：补齐复合主键中非前导外键索引（含 M0 inbox 外键）。
- 本地演示库当前 revision：`0003_m1_fk_indexes`；应用角色不是超级用户。
- 8张来源、版本、证据、指标和历史表有 PostgreSQL UPDATE/DELETE 阻断触发器；SQLite 测试有等价约束。
- M0 数据保留；测试仅清理单独的 `_test` 库，覆盖 upgrade → downgrade → upgrade 和 ORM/迁移一致性。

原始核对：[数据库状态](evidence/M1-database.json)。

Pydantic 为唯一来源，当前 **43 个域 JSON Schema**，同步 OpenAPI / TypeScript：

```bash
make contracts
```

新增 SourceImport/SourceVersion/EvidenceClaim、Indicator/Observation、Signal、HistoricalCase 及 Web 预览契约。
统计期、published_at、available_at、ingested_at 不混用。未知时间保留 null，不能以搜索日期伪造历史快照。
普通导入不可更新旧版本；同修订号不同内容返回409，缺来源/时间证据不足返回具名404/422。

## 实际测试结果

| 命令 | 结果 |
|---|---|
| `make check` | Ruff/格式/ESLint 通过；mypy **40个源文件**通过；tsc 通过；pytest **131 passed** |
| `npm run build` | Next.js 正式构建通过，含管理员工作台、会话和受保护 BFF 路由 |
| `uv run --group local python -m scripts.local_stack --verify` | 真实 PostgreSQL 下 **131 passed**；API/Redis/Worker/readiness/幂等 smoke 通过；Playwright **2 passed** |
| `node scripts/verify_bundle.mjs` | 客户端 JS 无演示身份令牌或供应商 Key 配置 |
| 本地凭据扫描 | .env 为0600且被 Git 忽略；真实 Key 不存在于交付文件或客户端 JS |
| `uv build --package futureos-prediction-engine --out-dir .local/dist` | 独立包构建成功，确认含 M1 归一化/时间/信号规则 |

[检查输出](evidence/M1-check.txt) · [构建](evidence/M1-build.txt) · [PostgreSQL全栈](evidence/M1-native-stack.txt) ·
[客户端扫描](evidence/M1-client-bundle.txt) · [凭据扫描](evidence/M1-secrets-check.txt) · [独立包构建](evidence/M1-engine-build.txt)。

当前测试失败0。浏览器测试覆盖普通令牌拒绝、管理员登录、导入、早期时间无来源、晚期时间可见、退出；
实际修复了 Next 内部 localhost 与浏览器 Host 不一致导致的本地同源检查问题。
截图已查看，表单、DEMO 标记、来源时间和候选来源数正常：

![M1 来源工作台](evidence/M1-workbench.png)

延续已知提示：Starlette 的 httpx TestClient 有1项弃用提示；本机 Node/Rosetta 和 Playwright 颜色环境有提示，均未造成失败。
GitHub Actions 已更新但未推送/执行，不声称远程 CI 已通过；本仓库尚未创建 commit。

## DeepSeek 真实验证

使用用户授权的本地 Key，仅执行：

1. Search：**HTTP 200**，返回1条命中。
2. Fetch：**HTTP 200**，返回正文预览（2000字符上限）。
3. 将官方 PostgreSQL 文档的链接和元数据导入：**HTTP 200**。

数据库审计确认 Search/Fetch 各一次 HTTP 尝试，没有自动重试。
[脱敏真实联调记录](evidence/M1-deepseek-live.json) 不包含密钥、正文或原始响应。
正文没有被自动保存为已核实事实；该真实来源为 metadata_only / observed_now，不产生真实信号或历史证据声明。
实际金额以 DeepSeek 账单为准，不自行声称扣费金额。未调用 LLM、邮件、支付或周期自动采集。

`.env` 已配置 `DEEPSEEK_API_KEY` 和 `LIVE_WEB_ENABLED=true`。真实按钮只允许管理员手动触发；
每管理员每分钟5次、滚动24小时20次，审计在 `/api/v1/admin/web-access`。
测试强制禁用真实网络，CI 不需要 Key。

## 用户操作路径

```bash
make up
# 已有本地配置；make up 会自动执行迁移和幂等种子初始化。
# 另一个终端 make down，或前台 Ctrl-C 停止。
```

打开 [来源工作台](http://127.0.0.1:3100/admin/sources)，使用本地管理员令牌（DEMO_ADMIN_TOKEN，默认见 .env.example）。
无需在页面输入 DeepSeek Key。默认 DEMO JSON 可直接导入；实际检索先看预览、确认许可和时间，再导入。
指标定义/修订/series 查询、证据和历史案例查询可在 [API文档](http://127.0.0.1:8100/api/v1/docs) 使用。
完整命令见 [本地运行手册](../runbooks/local.md)。

## 限制与下阶段前提

- 证据“verified”目前是带原文引用、定位和说明的人工核实记录，不是独立 Critic 或自动事实核查结论。
- 历史可用时间依赖人工提供的可复核归档/发布依据；实时 Search 的日期过滤不能替代历史快照。
- 转载匹配为保守启发式，只检查最近1000个同标签版本；不保证识别全部改写/转载。管理员可注明原文链接。
- 管理列表当前有上限（来源/信号200、证据500等），不是全网采集平台；指标 series 按统计期选版本。
- historical_cases 夹具是合成资料，后台没有持续采集真实招聘/统计数据库；需要具体合法来源和授权后再增加 Connector。
- 来源许可是保留范围与人工说明记录，不代表自动完成版权/访问许可审计。Fetch 预览不会自动入证据库。
- 认证仍为本地开发身份，不适合公开部署；正式认证在 M4，生产安全/稳定性按 M7 验收。
- 后续导入归档可以补全历史资料；研究输入集冻结须在 M2 按具体版本/hash 完成，不能把查询结果误称不可变研究运行。
- **尚无真实前瞻预测证据，预测准确率尚不能判断。**

决策：[ADR-006](../decisions/ADR-006-m1-evidence-temporal.md)、[ADR-007](../decisions/ADR-007-m1-live-web.md)。
停止在 M1。用户验收后，M2 才开始信号融合、机制/历史类比、竞争假设与可检验预测草稿；发布闸门仍须等待 M3。
