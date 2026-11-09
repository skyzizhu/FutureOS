# ADR-019：本地密码登录并发限流和资源保护

2026-11-02 用户要求先做登录保护；正式管理员账号/角色细分/MFA另行实施。本轮不解除生产阻断，不变更现有演示管理员认证。

沿用随机盐scrypt和恒时比较，未知账号同样经过密码KDF路径。密码计算每进程最多2路；占满立即503 AUTH_BUSY并Retry-After=2，不让请求无限排队等待内存密集KDF。

auth_attempts 增加source_hash，新增单行auth_throttle_lock。每次准入在短事务内通过INSERT ON CONFLICT + UPDATE获取数据库行写锁，查询/写入计数后提交，再做KDF，保证跨连接/进程检查不能并发越过上限。SQLite写锁用于本地测试，PostgreSQL行为由原生测试覆盖；计数不依赖Redis或进程内存。

默认滚动900秒：账号10次、连接来源30次、实例60次，注册和登录共享。成功、失败和已准入但KDF繁忙的请求均计数；被限流请求不延长已有窗口。身份规范化后HMAC索引，来源另外用域分离HMAC，不保存原始邮箱/IP。新尝试时清理过期计数；空闲期间记录可能保留至下一次尝试，不承诺定时物理擦除。
限流返回统一AUTH_RATE_LIMITED及Retry-After秒数，不披露是哪一维命中。账号错误/不存在均401同文案；注册重复标识仍保留既有409语义，尚未实现消除注册枚举。

来源只认ASGI连接peer，忽略应用层X-Forwarded-For/X-Real-IP；项目Uvicorn启动命令显式--no-proxy-headers，防止框架提前信任伪造header。
当前Next BFF请求都由loopback发出，因此来源配额是BFF整体预算，**不是公网真实客户端IP限流**。未来生产需配置可信反向代理、受保护的客户端身份传递及边缘限流，不能直接转发任意客户端header。

API/BFF错误禁止缓存，BFF透传数字Retry-After，UI给等待提示且不自动重发密码。临时限制不是永久封号；攻击者仍可消耗账号/实例预算导致暂时拒绝服务。公网需边缘流量防护、容量和异常告警，不能称为完整撞库防护或生产认证。

正式管理员后续设计：库内账号+盐化密码哈希+服务端角色/权限；TOTP密钥加密或Passkey公钥；恢复码只存哈希；只有完成第二因素的短期会话才能通过管理权限。管理员创建应走受控初始化/授权流程，不能普通注册自选admin或手工直接写明文密码。MFA绑定/重置/恢复也必须有审计和重新认证。

依据：[OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)、[OWASP MFA](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)。
