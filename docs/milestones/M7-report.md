# M7 本地工程验收报告

日期：2026-11-02。用户授权范围：安全、可靠性、质量/成本观测、恢复演练和一次受限真实研究验证。
结论：本机工程实施及下述自动化验收通过；M7生产发布条件未全部满足，保持 **NO-GO**。没有部署公网、真实收款或外发邮件。

## 实现与边界

- 当前账号导出包含历史画像快照、全部私人报告版本、建议/反馈、通知与额度等结构化记录，限制10MB；账号删除要求当前密码与明确确认。清除私有正文、登录标识/会话，取消未完成任务并释放预留；必要随机ID/财务审计及公开研究保留。
- 新增0011_m7、privacy_erasures，73张业务表。仅有owner删除登记时开放窄范围私有删除和精确快照清除；世界版本和财务审计不可变。恢复后的删除重放防止账号复活；普通DELETE不代表物理页/WAL/旧备份取证擦除。
- Fetch精确域名白名单、公网A/AAAA预检、拒绝混淆URL/凭据/内网IP/异常端口；固定DeepSeek HTTPS出口，无自动重定向。远程供应商DNS/跳转行为仍需生产出口控制。
- API在解析JSON前限制1MiB请求体；CSP/防嵌入/nosniff等响应头；模型/抓取内容作为文本。模型没有shell、邮件、支付或取数工具权限，结构化输出/引用/事实检查不能替代人工抗提示注入复核。
- 每账号待处理请求上限20，先处理幂等重放；Worker按用户→Job锁序与删除/撤权串行；Redis心跳故障时继续数据库轮询。修复管理员缩短监控冷却时间未同步既有截止时间的问题。
- `/admin/readiness`展示队列/租约、版本hash、来源许可、指标修订/过期复查、到期评估和恢复证据。没有有效真实效果样本就保留accuracy=null；production_ready始终false。
- 用户说明草案 `/help`、删除说明 `/privacy/deleted`；发布、支持、恢复及回滚手册见 [M7-release](../runbooks/M7-release.md)。

## 实测结果

| 命令/范围 | 实际结果 | 证据 |
| --- | --- | --- |
| `make check` | 353 pytest通过，Ruff、mypy、TS通过 | [check](evidence/M7-check.txt) |
| 最终 `make lint typecheck` | 137文件格式检查，87个mypy源文件，TS通过 | [static](evidence/M7-static.txt) |
| `make contracts` | 108 domain schemas及API/TS类型生成 | [contracts](evidence/M7-contracts.txt) |
| `make build` | Next生产构建通过，含help/readiness/删除页 | [build](evidence/M7-build.txt) |
| `make local-verify` | 原生PostgreSQL/Redis：353 pytest、smoke、8条浏览器流程通过 | [native](evidence/M7-native-stack.txt) |
| 队列/并发/故障 | 20任务上限，第21请求429；4线程处理，无重复完成事件；租约恢复及Redis中断回归 | tests/security/test_m7_boundaries.py及上述PG测试 |
| 安全/权限/隐私 | SSRF混淆及混合DNS、跨账号、重新验密删除、删除后旧链接失效、备份篡改/错钥/路径拒绝、HTML脚本未执行 | tests/security及浏览器privacy流程 |
| `make backup-drill`（升级密码库后） | 隔离库74张表含alembic；摘要相同；50份已有私人报告成功解密；重放1条备份后删除；演练库移除 | [restore](evidence/M7-restore-drill.json) |
| Core独立构建与离线重放 | wheel/sdist成功；选取原M3 REAL、本次REAL、最新Mock及incremental共4条重放hash一致，0联网 | [build](evidence/M7-engine-build.txt)、[replay](evidence/M7-offline-replay.json) |
| 密钥/客户端 | 504文件扫描无实际Key/密钥命中；私密文件0600且被Git忽略；客户端无服务端令牌/配置 | [secrets](evidence/M7-secrets.json)、[bundle](evidence/M7-client-bundle.txt) |
| 就绪快照 | 6项本地检查通过，生产仍为false | [readiness](evidence/M7-readiness.json)、[runtime](evidence/M7-runtime.json) |

测试只使用隔离测试库/合成账号；浏览器验收会在演示运行库追加DEMO记录，不代表清空运行库。
曾有一次浏览器套餐流程因既有DEMO监控冷却失败，已修复/回归；失败未扣最终额度。最终8条全通过。测试遗留的DEMO冷却0/日100策略已还原默认，未修改REAL策略。
旧历史Mock中存在缺失归档工件的运行，重放按设计拒绝，未替换原工件或联网补算；上表只对指定4条成功样本负责，不宣称全部历史运行均可恢复。

## 一次真实验证

本轮唯一新增DeepSeek模型调用，deepseek-flash，输入3126/输出511，共3637tokens；结果完成、独立Critic为annotate、离线重放一致。
使用此前已核实并冻结的公共资料，未宣称最新检索；保留内部草稿，没有创建新的公开版本，没有真人独立审核。
证据：[M7-real-validation.json](evidence/M7-real-validation.json)。原M3真实前瞻登记未改，窗口截止2026-12-01，仍not_due；本轮不是准确率/收益验证。

## 依赖、许可与剩余风险

cryptography从48.0.1升至50.0.2，Python复审未发现已知漏洞；运行时npm审计为0。
全npm审计仍有13个moderate依赖链条目，根因同一minimatch公告，位于开发工具链；high/critical为0。未以不兼容跨主版本覆盖或过时ESLint降级掩盖结果，发布前需完成兼容修复。详见[许可及成本审计](M7-licenses-costs.md)和[依赖审计](evidence/M7-dependency-audit.json)。

没有在已执行场景发现P0权限/计费缺陷；这不是独立渗透测试或零漏洞保证。
生产仍受以下条件阻断：独立研究/安全复核；正式认证、HTTPS、KMS/密钥轮换和告警通知；真实支付/邮件接入及条款验收；资料/二进制/模型许可及单价确认、原生服务器二进制CVE与补丁审计；容量/长期稳定性验证；正式支持、退款和保留期限政策。
备份只验证本机单次演练，未确定RPO/RTO；加密数据库包之外还须保存冻结Core工件、对应依赖和最新删除日志。

当前不需要新增数据库密码或Key。后续适合先进行人工试用与独立质量验收，再按明确发布范围补齐生产服务；不能直接放开现有本地开关上线。
