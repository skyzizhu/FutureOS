# 原生本地运行

本次已生成 .env 与隔离 PostgreSQL 数据目录。不要覆盖已有 .env 或把它提交到 Git。

```bash
make install
make build
make up
```

`make up` 保持前台运行；访问 http://127.0.0.1:3100，API 文档 http://127.0.0.1:8100/api/v1/docs。
Ctrl-C 或另一个终端运行 `make down` 停止它创建的进程，数据库和 Redis 文件仍保留。复用的既有 Redis 不会被关闭。
日志：.local/api.log、worker.log、web.log。端口冲突时在 .env 修改 FUTUREOS_*_PORT；不要终止其他项目。

新机器首次（未有 .env）：先 `make install`，再 `make local-install`（本地二进制需 macOS / Linux 支持）。
如自有已安装 PostgreSQL，请手动建立 DEMO/Test 专用库，按 .env.example 设置连接，并用 FUTUREOS_MANAGED_POSTGRES=false。
支持的原生运行时是 Python 3.12、Node 24 LTS；锁定文件保证依赖可复现。

```bash
make contracts
make check
npx playwright install chromium
make build
make local-verify
```

`local-verify` 启动实际服务，使用单独 TEST_DATABASE_URL 运行测试，再做 smoke 与浏览器 E2E，然后停止。
测试会清空专用测试库的全部业务表，只允许数据库名以 _test 结尾；不得指向运行/生产数据库。
单元/契约快速检查可直接 `make test`，默认使用每次隔离的临时 SQLite。

迁移：`make migrate` / `make seed`；受管理的 PostgreSQL 需要 make up 启动后才可用。
迁移 0001_m0 可 downgrade base（仅空的/专用测试环境），会删除四张 M0 表，不用于生产恢复。
崩溃作业在 lease 到期后恢复；最多三次尝试，终止错误不自动无限重试。

本地 DEMO 固定令牌见 .env.example，供开发验证权限；不得将该模式公开部署。
生产部署和正式认证尚未实现；M7本地恢复演练见 [发布与恢复手册](M7-release.md)。


## M1 管理员工作台

访问 /admin/sources，输入本地管理员令牌（DEMO_ADMIN_TOKEN，默认值见 .env.example）。
普通演示令牌无权进入。登录 cookie 只维持1小时，退出时清除。

可搜索 → 抓取预览 → 准备元数据；核对许可/时间/引用后再导入来源 JSON 或上传 .json。
默认自编 DEMO 可以直接导入并产生候选信号，复制网页链接不会自动变成已核实证据。
当前机器 DeepSeek Key 已配置、LIVE_WEB_ENABLED=true；搜索/抓取按钮会产生供应商请求。
每次手动操作最多一次上游请求，本地预算每分钟5次/每天20次，未接周期自动采集。
测试始终禁用真实联网，CI 不需要供应商 Key。

Swagger 的 /api/v1/admin/indicators 与 /observations 支持指标定义与修订导入，/series?as_of=... 查询历史值；
/evidence、/signals、/historical-cases 支持时间视图，全部需要管理员身份。
无数据返回空集合；不存在的来源/指标返回具名404；不能证明时间或引用时返回具名422。

迁移顺序：0001_m0 → 0002_m1 → 0003_m1_fk_indexes。make up 自动升级。
0002 的不可变表不接受普通 UPDATE/DELETE；修正请重新导入新快照/修订号。
测试/回滚会删除相应表，只在专用测试库操作，不能用于清理正式研究。

`scripts/m1_live_smoke.py` 是显式真实联调工具，只在需要核对 Key/连通性时手动执行（两次供应商请求），
不是 make check/local-verify 的一部分。审计在 /api/v1/admin/web-access，不包含密钥或原始查询。


## M2 内部研究

访问 /admin/research，以同一个本地管理员令牌登录。先“准备 DEMO 研究”，再“创建内部草稿”。
默认 Mock 不联网；可编辑 JSON 使用库内已核实信号和明确的研究截止时间。
界面展示基线、独立来源数、机制/反向作用、三条路径、历史正反类比、冻结 hash 和离线重放。
输入快照也可通过 /api/v1/admin/research/runs/{run_id}/inputs 核查。

M2 只保存草稿 A，不发布世界预测。迁移最新为 0004_m2，make up 自动升级。
整个输入集在提交时冻结，后续指标修订不会偷偷改变旧运行。已冻结 Core 工件在 .local/engine_versions 下，需随数据库备份。
代码更新后，重放会校验并运行原代码工件；缺失/损坏时明确报错，不能临时访问模型重新生成。
Python/Pydantic 大版本变化仍需使用原依赖环境，代码工件不等于完整系统镜像。

当前本机 LIVE_RESEARCH_ENABLED=true、模型 deepseek-flash；管理员可主动选择 DeepSeek。
生成与 LIVE_WEB_ENABLED 分开，不自动触发 Search/Fetch；每次最多一次真实模型调用，每天最多5次预留。
真实请求结果记录在 /api/v1/admin/research/model-calls；started 不明或失败不自动重试。
`python -m scripts.m2_live_smoke` 是显式真实付费联调，不包含在 make check/local-verify 中，非必要不要重复执行。
普通演示用户不能提交或读取内部研究，Web 不持有供应商 Key。

## M3 审查与评估

进入 `/admin/review`，管理员选择研究工作台产生的草稿并运行独立审查。
L1 仅附注；L2/L3 不允许发布，可确认已核实的问题后生成 B1/B2，再单独审查。
原稿不可修改；API 可在定向复核时提供 `additional_case_ids` 补充 M1 中已核实的案例。
两轮仍有实质问题则 research_only，不自动再次调用模型。

发布后选择该版本冻结评估协议，阈值和单位必须与目标一致。DEMO 只能 synthetic；
真实前瞻须 REAL、近期输入、窗口开始前登记。缺数据检查会追加待验证记录，不会默认判对。

首条真实前瞻记录位于 `docs/evaluations/M3-forward-registration.json`，已登记且尚未到期。
不要重复运行 `scripts.m3_forward_start`；它会拒绝覆盖既有记录，防止再次付费。
在本地服务运行时可手动执行：

```bash
uv run python -m scripts.m3_forward_resolve
```

到期前输出 not_due，不联网。到期后最多10次官方分页请求，不调用模型；分页不完整/接口不可用则保留待验证。
没有自动定时执行或通知。完整库和 `.local/engine_versions` 要共同备份；不要删除归档工件。

数据库迁移 `0005_m3`、`0006_m3_gate_shape` 保留已有 M0–M2 数据；发布/审查/评估追加写。
已存在正式版本或 B 草稿时拒绝向 M2 降级，避免丢失历史；应备份后做前向修复。

## M4 用户报告与私有数据

打开 `/auth/login` 创建自己的本地账号（不使用管理员令牌），选择两级行业后进入 `/dashboard`。
其他画像字段都选填，默认不用于报告；勾选授权后才进入最小快照。默认 DEMO 不调用外部服务。
首份完整报告按1次请求预留；一份报告可组合多条已过审版本，不按预测条数重复扣减。
失败、取消、租约耗尽会释放额度。刷新 Dashboard 可以找回待处理任务并取消；已消费不能回退重领。
REAL 模式只复用已有过审版本；没有资料则失败释放，不会偷偷改成 DEMO 或编造现实结论。

本地账号邮箱未验证；默认会话168小时，注销后失效。Web/API 均只监听 loopback。
配置 `SESSION_HOURS` 范围1–720；不要以当前 HTTP/演示管理员认证配置公开部署。

私有加密密钥默认 `.local/private-profile.key`，首次账号/画像写入时生成，0600并被 Git 忽略。
**数据库备份之外，务必单独备份该密钥文件。** 丢失后已有邮箱、画像、报告无法解密，不能靠更换密码恢复。
已有私有资料时密钥缺失返回503，不自动生成替代钥。恢复原文件并保持0600，再重启服务。
如设置 `PROFILE_KEY_PATH`，API 和 Worker 必须使用同一路径；密钥轮换和 KMS 未在本轮实现。
不要把密钥、数据库密码或会话 token 放到前端变量、截图、日志或公共提交。

报告正文和个人影响加密保存，固定 profile_snapshot_id 与 forecast_version_id；编辑画像不覆盖旧报告。
撤回选填使用授权会取消尚未完成报告；已完成版本保留当时快照。当前选填内容可清空后保存；
撤回“使用”授权本身不自动删除历史内容。M7已实现需当前密码确认的账号删除；找回密码和邮箱验证尚未实现。
本人可在设置页导出画像快照、所有报告版本及相关结构化资料，单次上限10MB。管理员不能通过私有 API 读取其他账号报告。

邮件只预览固定摘要和鉴权链接；明确授权并确认当前账号邮箱后，仅保存本地模拟记录，绝不发送真实邮件。
本地模拟每用户首份报告最多一次，不消耗第二份研究额度。没有周期任务、真实SMTP或收费。

M4 迁移为 `0007_m4`、`0008_m4_private_guards`。已有私有报告时拒绝直接降级删除历史，优先备份与前向修复。
合成目录首次准备经过完整 M2/M3 闸门，保存在共享 ReportCatalogEntry，native 单机文件锁避免重复初始化。
它不是分布式锁；过期目录和变更引擎的未完成目录需要管理员显式更新版本，不自动伪造新资料。

账号安全后续：日常管理员令牌已默认关闭，改用专用账号+TOTP。邮箱注册/改密、会话与恢复见 [账号安全手册](account-security.md)。`local-verify` 的浏览器流程现也只用 `_test` 库和独立E2E密钥，不写入日常运行库；历史章节的演示令牌仅适用于显式测试配置。
