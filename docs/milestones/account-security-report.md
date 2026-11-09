# 账号、管理员与邮箱验证增量验收

2026-11-02。用户授权补齐管理员账密、权限、双重认证、会话和邮箱验证码流程，并询问第三方动态验证。
结论：下述本地实现与自动化验收通过；真实SMTP、Turnstile配置及公网部署没有完成，保持生产发布阻断。

## 已完成

| 能力 | 当前实现 |
| --- | --- |
| 账号存储 | 加密邮箱、带随机盐scrypt密码摘要、启用状态与邮箱验证时间；新注册不能自选管理员角色 |
| 邮箱注册 | 先发码，再提交邮箱/验证码/挑战ID/密码；验证通过才在同一事务建号 |
| 邮箱改密/找回 | 独立用途4位验证码；成功撤销所有用户/管理会话及待完成登录挑战，不移除管理员MFA |
| 验证码保护 | 5分钟；每条5次；重发60秒；3次/15分钟、10次/日；每邮箱用途每日5次错误，重发不清零；摘要绑定邮箱/用途/挑战 |
| 管理员初始化 | 本机CLI生成15分钟一次性能力，0600，仅DB摘要；首位owner创建后关闭bootstrap；无默认真实管理员密码 |
| 管理员第二因素 | 密码只换待认证挑战；TOTP通过后才发管理会话。6位/30秒、加密密钥、数据库拒绝重放；一次显示10个恢复码，恢复后强制重绑 |
| 权限 | owner/reviewer/operator/viewer，服务端每次检查；只有owner管理账号/权限，敏感操作需5分钟内TOTP确认，不能停用/降权最后一名启用owner |
| 账号停用与变更 | 撤销目标旧会话和挑战；密码单独或普通用户会话不能读取管理接口；历史演示管理员令牌默认关闭 |
| 会话管理 | 用户/管理会话分离；默认管理会话30分钟；本人可查看概括设备标签、单个注销、需密码的全部注销；不返回token/摘要/完整UA/IP |
| 审计与提示 | 追加写认证/恢复/权限/改密/注销事件；owner读取；近期失败>=5时管理台提示，未外发告警 |
| 防机器人 | Turnstile widget与服务端校验、hostname/action/过期/重复token检查；注册/找回发码触发，同邮箱连续3次失败后登录触发；供应商失败不放行 |
| 备份 | 新认证状态指纹；恢复后验证邮箱和TOTP密钥；旧快照先比对原指纹，再仅对隔离库升级/重放删除，最后移除演练库 |

普通用户入口 `/auth/login`、`/account/security`；管理员入口 `/admin/login`、`/admin/security`。
TOTP采用兼容认证器的手动密钥/导入URI绑定，本轮没有增加QR图片生成；恢复码和密钥不进入截图/日志。
日常运行库尚未创建真实管理员（runtime_admins=0），需要用户自己选择账号密码并在自己的认证器中绑定；测试管理员仅存在独立测试库。
旧M4账号保持未验证标记，不伪造邮箱归属，原登录保留；新注册必须走验证码；邮箱改密可完成归属验证。

## 实际验收

| 命令/范围 | 结果 | 证据 |
| --- | --- | --- |
| `make check` | 396 pytest通过；Ruff149文件、mypy91源文件、TS通过 | [check](evidence/account-security-check.txt) |
| `make contracts` | 123领域schema及OpenAPI/TS生成 | [contracts](evidence/account-security-contracts.txt) |
| `make build` | Next生产构建通过 | [build](evidence/account-security-build.txt) |
| `make local-verify` | 真实PostgreSQL/Redis：396 pytest、smoke、11条浏览器流程通过 | [native](evidence/account-security-native.txt) |
| 新安全专项 | 邮箱绑定/用途/到期/重发/猜码预算；并发建号；改密撤销；会话越权；无MFA不发权限；动态码并发重放；恢复重绑；权限/停用/最后owner；过期step-up；验证码SMTP TLS Mock；Turnstile主机/用途/重复/中断 | tests/security/test_account_security.py |
| MFA恢复演练 | 新0014_email备份81表；6份报告、6个邮箱、2份认证器密钥校验成功；认证指纹一致、演练库已移除 | [auth restore](evidence/account-security-auth-restore.json) |
| 日常运行库隔离恢复 | 50份已有报告、32个邮箱可解密；新认证指纹一致；源库不覆盖 | [runtime restore](evidence/account-security-runtime-restore.json) |
| 历史备份 | 0011_m7原74表快照摘要匹配；隔离升级到0014_email，50份报告/27个邮箱可读，重放1条备份后删除 | [historical](evidence/account-security-historical-restore.json) |
| Core工件及历史重放 | wheel/sdist成功；原REAL前瞻、本轮M7内部REAL、Mock、incremental共4条离线hash相同，0联网 | [engine](evidence/account-security-engine-build.txt)、[replay](evidence/account-security-replay.json) |
| 密钥/前端 | 585个文件扫描无实际Key/业务密钥/TOTP密钥/初始化能力命中；私密文件0600并被Git忽略；客户端无服务端令牌或供应商配置 | [secrets](evidence/account-security-secrets.json)、[bundle](evidence/account-security-client-bundle.txt) |
| 依赖审计 | 新增PyOTP2.10.0，Python复审未发现已知漏洞；JS锁文件未变，M7记录的开发工具minimatch中危风险仍开放 | [dependency](evidence/account-security-dependencies.json) |

历史备份没有新认证指纹字段，因此该项为false，不冒充已验证旧认证摘要；其加密包校验、原报告/世界版本指纹及恢复后密钥检查真实通过。
浏览器现在也只用专用`_test`库和独立`.local/e2e`密钥，验收会清空测试库全部业务表，不改日常管理员、登录配额或真实资料。
历史M3–M7截图保留，新管理员登录页截图见 [admin login](evidence/account-security-admin-login.png)。
日常服务恢复到原配置：demo_admin_enabled=false、auth_mail_transport=local_preview、turnstile_enabled=false。
未增加真实模型、搜索、支付或邮件调用；真实前瞻尚未到期，不推断准确率。

## 待用户配置与生产验收

1. 真实SMTP：主机、端口、账号/授权码、发件地址；SPF/DKIM/DMARC、指定本人收件箱/失败/垃圾箱/配额/重发联调。当前SMTP仅Mock验证，没有实际投递证明。
2. Turnstile：sitekey、secret、允许的实际域名；真实服务可达性、目标用户地区体验和错误情形联调。当前未配置，不能称为已启用第三方反机器人。
3. 本人初始化管理员、绑定认证器和妥善保管恢复码；真实手机绑定由用户操作，自动化使用标准TOTP测试客户端。
4. HTTPS、安全Cookie、可信代理/边缘限流、外部告警、独立安全/质量复核、服务器二进制补丁及已有许可/依赖阻断项；支付仍是沙盒。

4位码按用户要求，熵有限，严格锁定也存在暂时拒绝服务取舍，生产策略需复核。本轮不声称完全消除账号枚举：注册409和真实同步SMTP投递的时序差异仍需生产流程/队列设计审查。
设备标签可伪造，只作本人排查线索，不是设备身份认证。MFA恢复/重置、审计保留期限、紧急主机恢复和长时间容量测试仍需运营制度和独立验收。

部署/初始化/配置步骤见 [操作手册](../runbooks/account-security.md)，设计见 [ADR-020](../decisions/ADR-020-account-admin-security.md)。
