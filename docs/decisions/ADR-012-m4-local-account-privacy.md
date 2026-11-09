# ADR-012：M4 本地账号、会话与私有快照

状态：已采用。用户明确授权 M4；保持原生本地部署，不进入 M5。

注册只创建 user 角色，不允许客户端指定权限。邮箱为本地登录标识，不声称已验证，不发送验证/找回邮件。
密码采用随机盐 scrypt（N=2^17、r=8、p=1）；验证使用恒时比较，未知账号也运行一次 KDF。
每个进程最多两个并行 KDF；滚动15分钟每邮箱10次、全实例60次尝试，错误不记录密码或邮箱原文。
参考 [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)。

会话是32字节随机 opaque token，DB 只保存 SHA-256；默认168小时，支持注销与过期。
Web BFF 将 token 放进 HttpOnly/SameSite=Strict cookie，不返回到客户端 JSON、不放 localStorage。
本机 HTTP 使用 secure=false，BFF 的变更请求必须与 loopback Host 同源；仅用于 localhost/127.0.0.1。
API 私有请求使用 Bearer 鉴权，所有对象读取再次核对 user_id；静态 M0 演示身份不能使用 M4 私有接口。
即使管理员也不能越过私有报告 ownership。认证响应和私有 API/BFF 禁止缓存。

邮箱原文、当前选填画像、最小画像快照、报告正文、影响/建议和模拟收件人使用 AES-256-GCM 加密。
每次随机12字节 nonce，AAD 绑定对象类型/user_id/对象ID；登录邮箱索引用带用途前缀的 HMAC。
库内只保留关联需要的用户ID、行业代码、固定版本ID、时间和状态。
依据 [cryptography AEAD](https://cryptography.io/en/latest/hazmat/primitives/aead/)。

密钥首次使用时生成到 .local/private-profile.key，0600、Git 忽略，不进入 Web/供应商请求。
已有加密资料而密钥缺失时返回503并要求恢复备份，不能静默换钥后覆盖旧资料。
这是单机本地密钥管理，不是托管 KMS；必须与数据库分开备份该文件。服务所在机器的所有者仍可访问密钥。

画像只强制两级行业，其他字段选填；产品自定义行业目录不是官方统计标准。
只有 use_optional_fields=true 才把岗位/地区/目标/任务/预算复制进研究快照，否则只保留行业与显示设置。
撤回选填授权会取消尚未完成的报告并释放权益，已完成报告仍保留当时版本。
数据导出要求本人登录；本轮没有实现账号删除、邮箱验证、密码找回或公网部署认证。
