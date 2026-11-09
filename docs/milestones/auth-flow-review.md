# 注册、登录及安全检查交互优化

2026-11-02。用户反馈：密码不能显示，未发码乱填后无明显反馈，注册点击反复触发Cloudflare，并要求整体优化节点。
使用Product Design audit/get-context工作流；保留已有Web绿色/米白设计。未更改验证码强度、权限、MFA、计费或真实供应商开关。

## 本轮截图审查

以下截图由本次in-app Browser实际捕获并逐张查看；浏览器视口较窄，采用表单所在视野截图，未把它们称作整页或桌面全尺寸验收。

1. **进入表单，原状态有明显阻力**：[01-before](evidence/auth-flow/01-before.png)。邮箱/密码在前，验证码操作与入口状态关系不清，密码无显示控件；页面进入就加载Cloudflare，用户尚未发码已产生安全检查。
2. **未发码直接提交，原反馈不明显**：[02-before-submit](evidence/auth-flow/02-before-submit.png)。页面确实显示“请先发送并填写邮箱验证码”，但位于次要切换操作之后，没有字段定位或醒目的样式；提交后原安全组件被清除/重建。不是后端允许了无验证码注册。
3. **进入新表单，已改善**：[03-after-start](evidence/auth-flow/03-after-start.png)。顺序为邮箱/发码→验证码→密码，步骤可见；未发码的验证码输入禁用并解释下一步；可显示密码；未挂载安全检查组件。
4. **未发码提交，已改善**：[04-after-feedback](evidence/auth-flow/04-after-feedback.png)。顶部和字段旁显示明确错误，焦点移到发送按钮，验证码保持禁用；没有重新进行Cloudflare检查。

![原提交反馈](evidence/auth-flow/02-before-submit.png)
![优化后的明确反馈](evidence/auth-flow/04-after-feedback.png)

优点保留：服务端原本已强制验证邮箱证明；错误验证码不能建号，其他用户私有资料和管理权限也没有通过UI放行。
可访问性改进：控件标签、aria-invalid/describedby、错误role=alert、发送成功role=status、首错定位、可键盘操作的密码显示开关；倒计时不每秒播报。
截图不能证明完整WCAG符合性、实际收信或真实Cloudflare挑战成功；这些分别依靠自动化回归、既有SMTP联调和用户本人实测，本轮没有发送真实邮件或代用户完成真实验证码挑战。

## 实施

- 密码显示/隐藏组件用于注册、普通登录、密码修改和管理员登录；隐藏为默认，切换操作不清空内容、不提交表单。
- 局部校验使用统一可见反馈，不依赖浏览器原生浮层；邮箱格式、未发码、4位码、验证码过期、密码长度先在本地检查，不为无效操作请求Cloudflare或后端。
- 发码成功后启用验证码输入并聚焦，显示有效期、重发倒计时；更换邮箱使旧证明失效。冷却时间按邮箱/用途保存，切换模式不会绕过同邮箱冷却。
- 提交中防止重复操作，安全检查可取消，网络/供应商失败可明确重试。安全检查期间不将整个区域标为忙而吞掉辅助技术状态提示。
- 注册/找回仅在有效发码动作时按需挂载Cloudflare，完成一次立即继续请求并移除组件；输入、错误码提交、本地错误和普通点击不消耗或刷新证明。
- 普通/管理员密码登录先正常请求；只有服务器返回HUMAN_VERIFICATION_REQUIRED才进行一次安全检查并重试一次。不能由客户端决定绕过服务端要求。
- Cloudflare使用interaction-only、简体中文、禁用自动失败重试和过期刷新；只有必须交互时显示挑战。不把单次token缓存成“永久免验证”。
- 不重用已消费token：实际重新发码仍获取新的证明。令牌由供应商规定单次、5分钟有效，后端host/action/时限/重放检查保留。

官方依据：[外观/执行模式](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/widget-configurations/)、[单次token及过期](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)、[简体中文](https://developers.cloudflare.com/turnstile/reference/supported-languages/)。

## 回归范围

新增浏览器用例覆盖：

1. 无邮箱证明的显著提示/自动定位、密码显示切换、无请求/无安全组件。
2. 一次安全检查只发一次验证码；修改密码输入/错误验证码提交不重启安全组件。
3. 正常登录零组件，服务端风险响应才触发一个检查。
4. 安全检查失败或取消后停止，必须用户主动重试。
5. 邮箱码过期/更换邮箱，不自动发码或自动反复验证。
6. 375px宽度、键盘提交、邮箱/短密码错误，不额外消耗token。
7. 管理员按需检查与密码显示，随后进入MFA第二因素。

UI专项模拟Cloudflare SDK和认证响应来检查生命周期，未在真实后端接受测试token。完整服务验收使用独立_test库、私有E2E密钥和本地预览邮件。
本轮发现原SMTP单测隐式继承已配置的465端口，已明确固定其STARTTLS fixture为587，并加强--verify环境隔离：去除真实SMTP/Turnstile/DeepSeek凭据、关闭真实调用。日常.env未因此改变。

最终命令和结果见同目录证据auth-flow-*.txt；真实供应商联调与生产发布限制仍沿用账号安全报告。

最终结果：`make check` 396通过；最终 `make lint typecheck` Ruff149文件/mypy91源文件/TS通过；`make build` 通过；`make local-verify` PostgreSQL396通过+18条浏览器流程通过（其中7条为本轮新增）。客户端服务端配置扫描通过。未修改DB迁移或接口契约。日常SMTP/Turnstile配置保留。
