# 首页研究对话入口前置

2026-11-03。用户要求将首页“你也有想研究的问题吗？”的 chat 控件放到上面并更醒目。

- 首页入口移动到产品介绍之后、行业展示和公开报告列表之前，不再置于列表末尾。
- 增加 AI 研究对话标识、柔和渐变卡片、较大的输入区域及“开始研究”文字按钮，保留原有输入校验和对话跳转。
- 手机端采用上下布局，输入字号16px，按钮保持文字可读；适配浅色与深色。纯 CSS 与现有 SVG 图标，无新增图片、字体或动画库；移除该首页卡片的背景模糊。
- 行业详情页保留原有入口位置。研究、鉴权、数据库和演示能力边界不变。

`make check` 通过：Ruff/格式/ESLint、mypy 97 源文件、TypeScript、427 pytest。最终 `make build` 和原生 `make local-verify` 全部通过：427 pytest、22 浏览器流程（2.8分钟）与队列 smoke。既有 Starlette TestClient/httpx 弃用提示不影响结果。

在既有浏览器流程中增加入口位置及跳转检查：桌面、390px 手机首屏输入框可见；输入框在行业展示之前；输入问题后正确跳转到带行业与问题的 chat 页面。实际 in-app Browser 复核浅/深色卡片与窄屏视觉。截图 `evidence/home-chat-priority.png`、`evidence/home-chat-priority-dark.png`。

验收使用独立 _test 数据库与本地预览验证码，禁用真实 SMTP/Turnstile/DeepSeek 调用，正常配置保留。验收后恢复正常本地服务。完整日志在 `evidence/home-chat/`。

