# M5 本地运行与故障处理

- `make up`：启动原生 PostgreSQL、Redis、API、research worker、scheduler、Web；`make down` 停止本项目管理的进程。
- `SCHEDULER_ENABLED=false` 关闭全部自动监控；管理员“拐点监控”可单独暂停/恢复主题。关闭邮件订阅不影响它们。
- 默认扫描间隔30秒；主题检查300秒、重大复查冷却6小时、滚动24小时最多12个监控任务。管理员可通过策略 API 调整。
- `/admin/monitor` 只显示已发布主题和复查任务；T0/T1 静默记录，不创建新版报告或邮件。
- 添加 DEMO 反证仅对 DEMO 可用。真实资料先在 M1 工作台导入并核实；当前不做自动联网检索。
- 实质复查须经独立 Critic；审查阻断时保留旧世界版本、报告增加观察提示。技术失败回滚，不产生“已完成”通知。
- `MONITOR_COOLDOWN` 等待冷却；`MONITOR_DAILY_BUDGET` 检查触发数量后调整策略，不反复人工提交。
- `MONITOR_ENGINE_CHANGED` 输入已冻结但部署代码变化，保留失败记录，核对工件后根据新输入/显式管理员操作重新复查，不篡改旧运行。
- `REPORT_REFRESH_BASE_CHANGED` 表示另一更新已先提交；旧任务不能覆盖新版。下一轮调度按当前世界版本追赶，也可在最新报告页免费复查。
- `REPORT_CONSENT_WITHDRAWN` 停止使用旧可选画像；更新授权后以新最小画像重新请求。密钥丢失必须恢复备份，不能换钥掩盖旧数据不可读。
- Job 状态、attempts、lease 和 error_code 保存在数据库；Outbox 与完成结果同事务，Redis 重启不会删除任务。定位日志只记录错误类与代码位置，不包含邮箱、画像或供应商凭据。
- 邮件偏好与本地投递在 `/notifications`。未授权、已退订、已退信抑制、冷却/周限触发时不投递。
- 退信回调需服务器私有 `BOUNCE_WEBHOOK_SECRET`，请求头 `X-Webhook-Signature` 为原始请求体 HMAC-SHA256 hex；event_id 去重。未配置时返回503，错误签名403。
- `delivered_local` 只表示本地 transport 已接受，外部发送为0。真实 SMTP 不接入当前 DEMO Worker，不能把本地接受率当作真实送达率。
- 外部邮件已开始但结果不确定时不得自动重发；当前本地 transport 不存在网络不确定性。启用真实传输前需补齐供应商幂等/不确定性核对流程。
- M5 migration `0009_m5` 支持空数据升级/降级；已有监控、通知或报告更新的实例先备份并使用前向修复，不用降级删除审计。私有数据库备份必须同时保存 `.local/private-profile.key`。
