# 登录保护增量验收

2026-11-02；用户要求先做登录保护，并讨论正式管理员方案。范围是本地密码登录/注册保护，不包含管理员MFA实现、公网部署、支付或邮件接入。

## 改动

- 以数据库短事务串行准入，修复并发请求同时通过“先计数再写入”的窗口。新增0012_auth和auth_throttle_lock，auth_attempts新增source_hash；运行库75张表含alembic。
- 默认滚动15分钟：同一账号10次、同一连接来源30次、全实例60次。注册/登录共享，计数持久化，重启不能清零；到期重新开放，不永久封号。包括成功和失败的已准入请求，被拒请求不续期。
- 来源只认连接peer，HMAC后入库；应用不采纳X-Forwarded-For/X-Real-IP；项目Uvicorn命令禁用proxy headers。目前Next BFF共享loopback来源预算，不是公网真实客户端IP防护。
- 每进程最多2路scrypt计算，占满立即503 AUTH_BUSY，不排队等待；账号不存在也使用密码校验KDF路径，错误文案与密码错误一致。
- 429返回Retry-After，BFF保留数字等待头和no-store，登录UI显示等待秒数，不自动重试密码。注册重复账号409仍属原有行为，不宣称已经消除注册枚举。
- 配置项AUTH_WINDOW_SECONDS=900、AUTH_IDENTITY_ATTEMPTS=10、AUTH_SOURCE_ATTEMPTS=30、AUTH_GLOBAL_ATTEMPTS=60，均有取值范围校验，未改写现有私密.env。

## 验证

- `make check`：360 pytest全部通过；Ruff检查139文件、mypy87源文件、TS均通过。
- `make contracts`：108领域schema及OpenAPI/TS生成；`make build`和客户端服务端配置扫描通过。
- `make local-verify`：原生PostgreSQL/Redis下360 pytest及smoke通过。首次浏览器8/9通过，新测试误匹配Next内部空alert；将定位限定为实际限流提示后，单独重跑全部浏览器流程9/9通过。
- 新增7项安全测试：并发准入不超额、伪造转发IP不能换来源、跨账号全局预算、注册登录共享来源配额、持久计数与到期恢复、未知/存在账号同一错误/KDF校验入口、密码计算资源占满快速拒绝。
- 新增浏览器流程：经真实BFF触发429、数字Retry-After/no-store、未签发会话、界面等待文案。
- 升级后加密备份恢复：0012_auth、75表、快照摘要相同、50份旧私有报告可解密，演练库已删除。本次为新迁移兼容恢复；备份后删除重放的专项结果保留在M7原报告，没有混为本次新增删除。

证据：evidence/login-protection-{check,native,browser,build,contracts,client-bundle,restore}。

## 明确保留的工作

正式管理员仍使用演示认证，没有新增真实管理员账密或MFA。后续需受控创建账号、密码哈希、服务端角色/权限、第二因素强制会话闸门、恢复/重置与审计；TOTP共享密钥应加密，恢复码存哈希，Passkey保存公钥。
生产还需可信代理和边缘限流、HTTPS、安全Cookie、邮箱验证/找回、异常告警、容量测试及独立安全评审。
全局/来源预算可被攻击者消耗，产生暂时拒绝服务；本轮不是完整公网防撞库体系。未改变M7既有依赖、服务器补丁、许可和生产服务商阻断项。
细节及参考来源见 [ADR-019](../decisions/ADR-019-login-protection.md)。
