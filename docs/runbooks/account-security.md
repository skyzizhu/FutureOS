# 本地账号与管理员安全操作

当前仅loopback本地运行。不要将本机演示部署直接暴露公网；既有M7发布阻断项仍适用。

## 首位管理员

1. `make build`、`make up` 启动后，另一个终端运行 `make admin-bootstrap`。
2. 在本机查看 `.local/admin-bootstrap.token`，不要把内容发到聊天、Git或截图。凭证15分钟过期，已有管理员时不能再生成。
3. 打开 http://127.0.0.1:3100/admin/login，选择“初始化管理员”，填写凭证、专用管理员邮箱和自己设定的密码。
4. 在认证器App中手动添加页面展示的密钥，填写6位动态码完成绑定。密码通过但尚未绑定时没有管理权限。
5. 将一次显示的10个恢复码保存到可信密码管理器，再进入管理台。不要截图公开密钥、URI或恢复码。

管理员使用独立账号；已普通注册的同一邮箱不会被直接提权。当前控制初始化不代表该邮箱已经通过邮件验证。
新增管理员在 `/admin/security` 由owner创建，首次密码登录也必须绑定认证器。建议维护至少两个受控owner以支持恢复。
普通登录入口为 `/auth/login`；管理员入口为 `/admin/login`，两者cookie分离。

## 账号与权限维护

`/account/security` 查看本人会话、单个注销、需密码确认的全部注销；邮箱改密入口同页。
`/admin/security` 查看管理会话、权限和安全审计。viewer不能写入；operator负责研究操作；reviewer负责审查与发布；owner管理账号和权限。
修改/停用会撤销目标旧会话。最后一个启用owner不能降权/停用。超过5分钟的敏感操作需用新的TOTP确认；同一动态码不能重复使用。
遗失认证器时，用密码登录后在第二因素处输入一个恢复码，重新绑定并保存新恢复码。owner可以重置其他管理员，不能通过该接口跳过本人的第二因素。
若唯一owner同时失去密码、邮箱和恢复能力，停止服务并走受控主机/备份恢复，不临时开放HTTP免认证入口。正式运营前应制定独立身份核验和紧急恢复制度。

## 邮箱验证码联调

默认AUTH_MAIL_TRANSPORT=local_preview：页面明确未发信。验证码只在本机DB加密预览，不在HTTP响应返回。
开发时根据发码响应challenge_id执行 `uv run python -m scripts.auth_mail_preview <challenge_id>`；这个CLI要求本机密钥和本地预览模式。
真实接入需要在私密.env配置：

- AUTH_MAIL_TRANSPORT=smtp
- SMTP_HOST、SMTP_PORT（465 SSL或587 STARTTLS）、SMTP_USERNAME、SMTP_PASSWORD（通常是授权码）、SMTP_FROM。

改完重启服务。先测试指定本人邮箱的注册/改密/超时/错误/重发，验证收件箱、垃圾箱、发件域名SPF/DKIM/DMARC及供应商配额。
不自动切换报告邮件，不发送营销邮件。SMTP失败保留审计，不自动重试未知投递；等待60秒后重发会让旧码失效。
4位码5分钟，5次/条；跨重发每日5次错误；每邮箱用途最多3次/15分钟、10次/日。不要靠重发绕过猜码预算。

## Turnstile

需要用户自己的Cloudflare账号/域名配置，提供public sitekey、server secret及允许的主机名。
.env：TURNSTILE_ENABLED=true、TURNSTILE_SITE_KEY、TURNSTILE_SECRET_KEY、TURNSTILE_HOSTNAMES=["实际网站域名"]。
本地联调允许localhost/127.0.0.1，生产不沿用开发测试密钥。secret只在API侧；sitekey可公开。
验证token超时、重复使用、错误hostname/action及供应商中断时应拒绝；不能只看前端“验证成功”。
当前未配置真实凭据，真实服务可达性及目标用户地区的可用性还需联调，不能声称已启用。

## 验收、备份与升级

`make check`、`make build`、`make local-verify`。--verify在PostgreSQL `_test`库跑测试并重置浏览器数据；E2E用`.local/e2e/private-profile.key`，不初始化运行库管理员。
本机DEMO管理员令牌默认关闭。仅自动验收/CI的独立测试配置DEMO_ADMIN_ENABLED=true；不要把该配置写入日常.env。
备份现包含认证状态指纹并验证邮箱/MFA密钥解密。历史备份先校验原快照，再仅对演练库升级当前迁移、重放删除记录，最后移除演练库。
业务密钥、备份传输密钥、删除日志、冻结Core工件仍需分别保管，参考M7恢复手册。
0013_security有管理员或审计后拒绝降级；0014_email有猜码计数后拒绝丢弃预算。使用备份/前向修复，不能通过降级清除安全状态。
