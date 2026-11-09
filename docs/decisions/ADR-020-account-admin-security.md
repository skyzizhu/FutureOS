# ADR-020：账号验证、管理员双重认证与权限

2026-11-02 用户授权完成账号/管理员安全，并明确注册和修改密码使用4位邮箱验证码；邮件配置后再真实联调。
本轮保持原生本地、支付关闭、报告邮件关闭；生产设置仍被拒绝。认证功能可在本地验收，不等于公网发布批准。

## 账号及邮箱证明

新注册必须先请求register用途验证码，再以邮箱/挑战ID/验证码/密码提交；证明消费与建号在同一事务内，验证前没有账号。
修改/找回密码使用独立password_reset用途；改密成功撤销全部用户/管理会话及待完成管理员挑战，MFA绑定仍保留。
旧M4账号不自动标为邮箱已验证，保留原登录；通过邮箱改密可确认归属。管理员由受控初始化创建，不能由普通注册选择角色。

4位数字为用户明确要求，含前导0；代码用安全随机数生成，5分钟过期，单条最多5次尝试、成功单次消费。
邮箱/用途/挑战ID都进入服务器HMAC摘要，不能换邮箱或跨用途使用；DB不存可离线枚举的裸SHA-256四位码。
重发至少60秒，最多3次/15分钟、10次/24小时；旧码失效。每邮箱/用途24小时合计最多5次错误，重发不重置猜码预算。
短码熵有限；严格锁定也可能被恶意消耗造成暂时拒绝服务。正式业务应复核短码长度、限额、恢复和反滥用策略，不声称通过独立安全认证。

SMTP模式仅保存摘要，发送采用SMTP_SSL(465)或强制STARTTLS、默认受信证书验证，不提供明文SMTP回退；结果不明不自动重发。
默认local_preview只在DB保存加密预览，可由持有本机密钥的CLI读取；没有HTTP预览/固定验证码/测试后门。
SMTP和报告订阅投递是独立开关：AUTH_MAIL_TRANSPORT不启用LIVE_EMAIL_ENABLED。真实配置/投递尚未验收。
不存在的找回账号返回相同响应形状但不发送邮件；注册重复标识仍有原有409语义，不声称完全消除枚举。

## 管理员和第二因素

首次所有者由本机CLI生成15分钟随机一次性初始化能力，DB只存摘要，文件0600；已有管理员后关闭初始化。
账号存随机盐scrypt摘要，邮箱加密；管理员需独立账号，不能公开自助提升现有普通用户权限。
密码通过后只发5分钟、高熵、最多5次尝试的待认证挑战，不能作为Bearer读取管理数据。
PyOTP TOTP：6位、30秒、±1步窗口；数据库串行锁+last_counter拒绝重放，密钥按用户AAD用AES-GCM加密。
绑定成功一次显示10个80bit恢复码，只存域分离HMAC摘要。恢复码使用后全部旧会话/旧恢复码失效，必须重绑新认证器后才能获会话。
所有者可在最近5分钟TOTP确认后重置其他管理员MFA；本人走恢复码，不提供免第二因素登录入口。

管理会话默认30分钟；DB记录kind=admin和mfa_verified_at，每次管理API同时检查角色、启用状态、MFA状态、会话有效期及权限组。
权限组：owner全部；reviewer读取+审查/发布；operator读取+来源/指标/信号/研究/监控写入；viewer只读。security管理仅owner。
敏感权限变更在串行后重新检查所有者和MFA新鲜度，变更/停用立即撤销目标会话及挑战；最后一名启用owner不可停用或降权。
所有角色可重新确认本人TOTP、轮换本人恢复码。MFA未绑定、只持密码、普通会话和自选角色都不能访问管理接口。

DEMO_ADMIN_ENABLED默认false；历史演示令牌仅自动化验收显式开启，不允许管理正式安全设置。生产仍被独立发布闸门阻止。
正常Web仅服务端持会话opaque token，浏览器JS不接收管理access_token；HttpOnly/SameSite=Strict，本地HTTP secure=false待HTTPS部署调整。

## 会话、审计与反机器人

会话列表返回随机public_id、类型、创建/到期时间和概括的浏览器/系统标签，不返回token及其摘要或完整UA/IP。
可撤销本人单个会话；注销全部需当前密码。设备标签是展示线索，可被UA伪造，不作为身份凭证。
认证失败/权限变化/恢复/改密/注销写追加审计，只有owner可读取；只保留随机账号ID和操作元数据，不存密码、验证码或密钥。
管理页15分钟失败事件>=5时提示，尚无邮件/外部告警通道。公网可信代理/边缘限流/独立安全评审仍待部署。

Turnstile默认关闭，缺密钥不能启用。注册与找回的发码需挑战；登录同一邮箱最近一次成功后累计3次失败触发挑战。
API验证固定HTTPS Siteverify端点，核对success、hostname白名单、action、5分钟签发时限，并在DB拒绝重复token；校验前有数据库准入预算，服务失败不放行。
客户端widget本身不授予权限；仅公开sitekey，secret不交给Web进程或bundle。不信任用户传来的转发IP头。

依据：[PyOTP](https://pyauth.github.io/pyotp/)、[OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)、[OWASP MFA](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)、[Turnstile服务端校验](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)。
