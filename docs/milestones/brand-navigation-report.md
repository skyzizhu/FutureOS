# FutureOS 品牌与顶部导航

- 网站名统一为 FutureOS，副标题为「预见行业趋势，做更好的决定」。品牌标志将字母 F、向上的趋势线和星点组合为 SVG，同一资源用于页首、页尾和浏览器图标。
- 顶部保留悬浮胶囊。桌面居中显示发现、行业、预测对话和我的，统一图标风格，当前页有可见的高亮和无障碍语义。预测对话使用原有聊天入口。
- 手机将主导航呈现在两列菜单中，同时提供搜索和登录或通知入口。账号和手机导航支持键盘打开、Escape 关闭并恢复焦点、点击外部关闭。减少动态效果模式停用导航过渡。
- 视觉检查覆盖桌面浅色、390px 和 320px 手机深色。自动化检查包含 360px 品牌与右侧操作区边界、当前页语义、搜索聚焦、手机菜单关闭和账号菜单焦点恢复。

## 验收

- `make check` 通过，Ruff、ESLint、TypeScript、mypy 106 个源文件和 465 项 pytest。
- `make build` 通过，最终构建预渲染 16 个静态页面。
- 首次 `make local-verify` 的 465 项 PostgreSQL 回归和任务冒烟通过。公开导航、360px 排版与键盘测试通过，账号菜单断言需要限定在页首，避免与个人中心正文的同名入口冲突。修正测试定位后重跑浏览器验收。
- 修正测试定位后 `npm run lint` 通过，`PYTEST_ADDOPTS='-k test_worker_research_persists_private_progress_and_result' make local-verify` 通过，包含 1 项原生专项和完整 22 条 Playwright 流程。
- `make up` 已恢复本地服务，首页和标志资源返回 HTTP 200。
