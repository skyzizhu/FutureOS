# M3 实施与验收报告

2026-11-01。**M3 已实现，本机自动化验收通过；未进入 M4。**
用户明确授权跳过 M2 人工点测等待，继续 M3。独立人工评审仍未完成，不将编码代理的自检称为人工验收。

## 已交付

| 范围 | 行为与边界 |
|---|---|
| 五类独立审查 | Evidence / Historical / Causal / Scenario / TemporalAndResolution；检查引用、转载、口径、案例、反向路径、反证和时间泄漏 |
| 能力隔离 | Critic 仅接收 DTO，在无凭据的独立进程执行；可信模块加载后拒绝网络/文件访问/子进程；无数据库连接、修订和发布工具 |
| 独立查证 | 按原研究 cutoff 重新查询 M1，冻结独立输入；可发现晚入库但当时已知的反证；不传主引擎提示词、不自动联网 |
| 确定性裁决 | L0 通过、L1 附注保留结论、verified L2 定向复核、verified L3 阻断；pending 实质问题或审查缺项不可放行 |
| A/B 与差分 | A/B1/B2 分开冻结；B 由主引擎生成，保存输入、父链、问题和字段差分；可补充已核实案例，不改变目标/阈值/期限；最多两轮 |
| 发布闸门 | 只允许对应草稿的最新通过记录；证据或 Core 已改变须重新审查；数据库检查草稿、审查、裁决、hash、连续版本号和版本指针 |
| 不可变版本 | ForecastVersion 与审查/裁决/差分/评估记录追加写；旧版不可更新或删除；版本保存发布原因与完整性 hash |
| 评估框架 | 阈值/来源/单位/截止时间预登记；观测必须匹配 M1 固定口径；保留全部协议及解析历史，失败和缺数据不丢弃 |
| 管理工作台 | 选择草稿 → 五类审查 → 定向复核/发布 → 冻结协议 → 内部成绩单；仅管理员可用 |

只读审查为确定性规则实现，不是另一次付费 LLM 投票。语义事实真实性和通用因果推断仍未自动解决。
原始草稿的 `internal_unreviewed/publication_allowed=false` 保留生成时状态；后续裁决与发布状态由独立记录表达，不覆写原稿。

## 数据与接口

- `0005_m3`：新增5张表（critic_runs、adjudication_records、draft_revisions、evaluation_protocols、forecast_resolutions），扩展已有草稿和版本表。
- `0006_m3_gate_shape`：补充版本 cutoff/连续编号/初始指针约束。应用角色不是超级用户。
- 所有新增审查、复核、评估表及预测版本/草稿均有 UPDATE/DELETE 阻断触发器；世界目标只允许合法最新版本指针变化。
- 当前67个域 Schema；Pydantic → JSON Schema/OpenAPI → TypeScript，未另写一套 DTO。
- 管理接口 `/api/v1/admin/review`，包括 drafts/check/revise/publish、runs、versions/register、protocols/resolve、scoreboard。
- M0/M1/M2 路由、Worker 和离线重放保持可用；原生 PostgreSQL/Redis，无 Docker 要求。

数据库实际核对：[M3-database.json](evidence/M3-database.json)。
已有正式版本或 B 草稿时拒绝向 M2 降级，避免删除历史；见 [本地运行手册](../runbooks/local.md)。

## 自动化验收结果

| 验证 | 结果 |
|---|---|
| `make check` | Ruff/格式/ESLint、mypy 57个文件、tsc 通过；pytest **240 passed** |
| `make build` | Next.js 正式构建通过，包含研究、来源、审查与评估工作台 |
| `uv run --group local python -m scripts.local_stack --verify` | 原生 PostgreSQL 下 **240 passed**；Redis/API/Worker/幂等 smoke 通过；浏览器 **4 passed** |
| 合成审查题组 | **35/35**，包含合理竞争观点、未来来源/指标/vintage/案例、转载、假引用、口径、基线、因果跳跃、缺反证/失败路径等 |
| 数据库反例 | 未过审/错草稿/旧审查/伪造版本号/非法指针被拒绝；原 A 和正式旧版不能静默覆盖 |
| 两轮复核 | B1/B2 可独立审查；B2 仍有问题进入 research_only；补充核实案例可以解除相关阻断 |
| 评估反例 | 不允许改阈值或把 DEMO 登记为 forward；错误来源/统计期观测拒绝；缺数据不判对；成功/失败及基线误差都覆盖 |
| 独立包与凭据 | Core wheel 构建成功；客户端无服务器身份/供应商配置；真实 Key 不在交付文件或客户端，.env 仍为0600并被忽略 |
| 真实旧稿重放 | 首条 REAL 运行用归档 Core 离线重放，hash 一致，新增模型调用0次 |

证据：[检查](evidence/M3-check.txt) · [Web构建](evidence/M3-build.txt) · [原生全栈](evidence/M3-native-stack.txt) ·
[契约](evidence/M3-contracts.txt) · [Core构建](evidence/M3-engine-build.txt) ·
[客户端扫描](evidence/M3-client-bundle.txt) · [凭据扫描](evidence/M3-secrets-check.txt) ·
[重放](evidence/M3-real-replay.json)。

浏览器验证 M0/M1/M2 回归及 M3 审查→DEMO发布→协议冻结→缺数据待验证；截图已检查：
[审查工作台](evidence/M3-review.png)。
延续1项 Starlette TestClient 弃用提示，没有测试失败。GitHub Actions 已更新但未远程执行，仓库尚未创建 commit。

## 合成评估和 A/B 贡献

[35条题组结果](../evaluations/M3-synthetic-critic.json) 标记 synthetic/DEMO，保留每题预期、实际发现和裁决。
题目由代码作者逐项编写，**尚未独立人工评审**；该成绩只证明这些结构性故障能被检出。

另跑通持久化 A/B 实验：A 缺少一条晚入库的合成反证，裁决 targeted_research；
主引擎 B1 纳入已核实反证后为 annotate，实质问题由1项降为0项，A hash 保持不变。
新增外部模型调用0次，保存差分、审查 CPU 时间与两个草稿 ID。
[实验记录](../evaluations/M3-ab-contribution.json) 的 `prediction_accuracy_delta=null`，不声称提高预测准确率。

数字评估支持已登记点预测的 A/B 绝对误差及基线误差，但当前 M2 主引擎不产生数值点预测，
因此实际登记协议的 A/B 点误差保留 null；不能将“>=70”的阈值冒充点预测70。
持平基线对照与到期状态可计算；合成、历史和真实前瞻分别统计，不混算准确率。

## 首条真实前瞻

已从当前真实时间登记并冻结一条 REAL 记录，验证目标为：
**在2026-11-01 22:26:47 至2026-12-01 22:26:47（北京时间）的窗口内，microsoft/playwright 是否出现至少一次公开稳定发布。**

验证源为[官方 releases API](https://api.github.com/repos/microsoft/playwright/releases)，
排除 draft/prerelease，使用 published_at 和完整分页；请求失败或分页不完整则数据不可用，不能默认事件未发生。
这是范围很窄的公开发布里程碑，不证明 Agent 生产可靠性、就业影响或个人建议价值。

- 原始输入为当前读取的官方短引用和公开 release 元数据，按 observed_now 存档，未伪造历史可用时间。
- 文档功能标签是候选机制线索；类比只核实“发布/关闭”事件，不声称完整因果历史或可迁移成功率。
- 编码代理核对原文，不声称独立人工语义审查。
- 一次 `deepseek-flash` 生成成功：prompt3128、completion631、total3759 tokens；保留后端 fingerprint，不推断扣费金额。
- 五类独立审查后为 annotate，经同一发布闸门冻结版本和协议；当前 **not_due**，没有准确率成绩。
- 代码扩展后仍可用原归档 Core 离线重放，无需重新付费。

[登记记录](../evaluations/M3-forward-registration.json) · [联调输出](evidence/M3-forward-start.txt)。
到期观测命令 `uv run python -m scripts.m3_forward_resolve`：到期前不联网；到期后最多10次官方分页请求，不调用模型。
没有自动定时执行或通知（属于 M5），没有向外部人员发信或提供个人报告。

## 本机入口与限制

服务已启动：[审查与评估](http://127.0.0.1:3100/admin/review)、[研究工作台](http://127.0.0.1:3100/admin/research)。
管理员登录后可直接查看成绩单。默认研究方式仍为 Mock，无需再填写 Key。

- 五类审查以结构性、时间、口径检查为主，不是通用自动事实核查。实际语义争议需补充核实资料。
- 独立查证仅查询有范围/数量上限的本地库；没有自动全网反证调查。B 复核不自动重新调用付费模型。
- 历史时间截断不能排除基础模型未来知识；合成检出率不能当成预测准确率。
- 独立人工题组评审、真实样本到期结果、足够样本的校准和效果比较仍待后续验证。
- Critic 子进程是受控代码的能力隔离，不是用于运行任意敌对代码的 OS 沙箱。
- 当前为本地开发身份，尚无 M4 用户认证/画像/私有报告，也未提供生产环境加固或公开成绩页面。
- 备份须同时保留数据库、Core 代码工件、uv.lock 和兼容运行环境。

决策：[ADR-010](../decisions/ADR-010-m3-independent-review.md)、[ADR-011](../decisions/ADR-011-m3-preregistered-evaluation.md)。
