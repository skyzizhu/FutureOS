# FutureOS · M7

个人未来预测 Agent：M0–M6 本地流程已完成；M7 增加安全回归、个人数据删除与完整版本导出、加密备份恢复演练及上线就绪观测。
研究演示仍为 **DEMO 合成假设**；管理员可以手动检索真实资料，二者严格区分。
已登记一条尚未到期的真实前瞻发布里程碑；真实预测准确率尚不能判断，商业计费尚未实现。

本轮范围见 [M7 计划](docs/milestones/M7-plan.md)；验收见 [M7 报告](docs/milestones/M7-report.md)。
[M0 报告](docs/milestones/M0-report.md) 保留历史记录。
正式规格为 IMPLEMENTATION_PLAN.md v1.3；用户指定原生本地部署和 PostgreSQL，覆盖文档中的 Docker 交付项。

```bash
make install
# 当前机器已初始化 PostgreSQL / .env。新机器且无 .env 时再执行 make local-install。
make build
make up
```

访问 [Web](http://127.0.0.1:3100)、[API 文档](http://127.0.0.1:8100/api/v1/docs)。
Mock 路径无需外部 Key；管理员真实搜索/抓取需服务端 DeepSeek Key。无需 Docker、邮箱或支付账号。Ctrl-C 关闭本次服务，数据保留。
原生 PostgreSQL、Redis 作为本机进程运行；未修改既有业务 MySQL 数据。

实际模型配置和凭据保存在本机 `.env`，配置项参见 `.env.example`。本地数据在 `.local/`，验收产物和真实前瞻运行登记也保留在生成它们的工作区。

```bash
make contracts        # 生成 JSON Schema / OpenAPI / TS
make check            # lint + typecheck + tests
make build
npx playwright install chromium
make local-verify     # 真实 PostgreSQL/Redis 全栈验收及浏览器 E2E
```

- [注册/登录](http://127.0.0.1:3100/auth/login) · [我的报告](http://127.0.0.1:3100/dashboard) · [画像与隐私](http://127.0.0.1:3100/settings)
- [审查与评估](http://127.0.0.1:3100/admin/review)（需管理员令牌）
- [研究草稿工作台](http://127.0.0.1:3100/admin/research)（需管理员令牌）
- [来源工作台](http://127.0.0.1:3100/admin/sources)（需管理员令牌）
- [架构和依赖边界](docs/architecture.md)
- [本地运行与恢复](docs/runbooks/local.md)
- [契约说明](docs/schemas/README.md)
- [DeepSeek 搜索与抓取方案](docs/decisions/ADR-005-deepseek-web.md)
- [Sky 搜索 Agent 历史复用评估](docs/decisions/ADR-004-search-reuse.md)
- [架构决策](docs/decisions/)

核心目录：apps/web、apps/api、services/prediction_engine、workers、packages/contracts、infra、fixtures、tests、docs。
当前处于 M7 本地工程验收，生产发布仍阻断。发布仍必须通过独立审查；DEMO 与真实前瞻分别记录，尚无真实准确率结论。

M4 仅需两级行业即可生成首份 DEMO 报告；选填内容默认不使用。一份完整报告消耗一次免费权益，失败释放。
私有正文加密，首次生成的 `.local/private-profile.key` 必须单独备份。邮件仅预览与本地模拟，不实际外发。


M5 管理入口 `/admin/monitor`；本人通知与邮件订阅 `/notifications`。原主题重要变化复查免费，报告页可查看固定旧版与变更说明。默认只监控已经接入本地库的已核实资料；不会自动付费联网搜索。邮件默认关闭，仅本地模拟投递；真实 SMTP 尚未启用。后台 scheduler 每30秒扫描到期主题，默认每主题300秒检查。


M6 入口 `/billing`（套餐与账单）、`/research`（新主题与周期授权）、`/admin/costs`（管理员复用与计量）。`SANDBOX_COMMERCE_ENABLED` 默认关闭，本地本轮显式开启；真实支付保持关闭，金额仅为合成流程示例。首次免费额度与套餐额度独立，旧主题更新免费，新主题/已授权周期完整服务使用1份套餐额度，成功才消费。当前定制研究只执行 DEMO，不自动开启真实模型或收款。

M7：`/settings` 导出及需密码确认的本人数据删除；`/admin/readiness` 查看质量、队列、许可与恢复证据；`/help` 为本地用户说明草案。`make backup-drill` 演练加密备份与隔离恢复。详见 [发布与恢复手册](docs/runbooks/M7-release.md)、[许可与成本审计](docs/milestones/M7-licenses-costs.md)。

M7 后续登录保护：已增加数据库原子准入、账号/来源/实例三层滚动限流、KDF繁忙快速拒绝及等待提示。默认900秒内10/30/60次；本地BFF共享来源预算。见 [增量验收](docs/milestones/login-protection-report.md)。正式管理员账号、TOTP、恢复码、权限与邮箱验证已在后续增量中实现，见下文。

账号安全增量：新注册和修改密码需4位邮箱验证码；默认只做本地邮件预览，真实SMTP/Turnstile待配置验收。管理员改为专用账号、TOTP与恢复码，演示管理员令牌默认关闭。启动后执行 `make admin-bootstrap`，打开 `/admin/login` 初始化；`/admin/security` 管理权限与审计，`/account/security` 管理本人会话。见 [操作手册](docs/runbooks/account-security.md) 和 [验收报告](docs/milestones/account-security-report.md)。
