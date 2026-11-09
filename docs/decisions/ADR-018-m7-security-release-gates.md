# ADR-018：本地安全边界、观测与生产发布阻断

- 本机 API/Redis/Web 仍只绑定 loopback，Settings 拒绝 production/demo_mode=false 及真实邮件/真实支付开关。
- 固定 DeepSeek HTTPS 出口不跟随重定向、不信任代理环境；Fetch 仅允许服务器配置的精确域名，拒绝凭据/非公网IP/混淆URL/非常规端口，对A/AAAA全集做5秒DNS预检。
- 目标由供应商远程解析与导航；预检不能证明上游不会重定向或DNS重绑定，因此不把本地预检称为完整的供应商网络隔离。生产需服务商约束与出口控制。
- 大请求在JSON解析前按流累计限制；认证/私有/错误响应禁止缓存；Web增加nosniff、无referrer、禁止iframe和CSP。
- React保持文本渲染，不执行抓取内容或模型返回的HTML；Next内联启动脚本暂需unsafe-inline，未声称CSP替代输出编码。
- 模型仅一次JSON生成，没有shell、支付、邮件或抓取工具权限；个人资料不进入公共研究提示词。提示注入不能靠提示词彻底消除，事实/引用校验和独立人工复核继续必要。
- 显式研究请求限每用户待处理20项，幂等重放优先返回旧任务；M2/M6与外部调用另有预算。Redis中断时Worker继续DB轮询，心跳失败与可用性分别记录。
- /admin/readiness 只读汇总版本完整性、租约/积压、许可记录/指标修订/复查逾期、评估到期状态与备份证据；未经真实观察不填准确率。
- 生产发布状态保持false：独立人工质量评审、生产认证/HTTPS/KMS、真实支付/邮件服务商验收、真实单价/内容许可均不能由合成测试自动勾选。

依据：[DeepSeek Search/Fetch](https://api-docs.deepseek.com/zh-cn/guides/search/)、[OWASP SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)。
