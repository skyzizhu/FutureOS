# ADR-005：搜索和抓取统一采用 DeepSeek

状态：已采用（用户指定）；M0 适配器及离线测试已实现，真实网络调用尚未启用。
日期：2026-11-01。覆盖 ADR-004 中的 Tavily/DDGS/本机抓取链路选择。

## 接口和边界

依据：[DeepSeek 使用指南](https://api-docs.deepseek.com/zh-cn/guides/search/)、
[Search 参考](https://api-docs.deepseek.com/zh-cn/api/search/)、[Fetch 参考](https://api-docs.deepseek.com/zh-cn/api/fetch/)。

- `POST https://api.deepseek.com/v1/tools/search`：query、count、need_content、ori_question、localization。
  query 1–128 字符，count 1–50。localization 必须显式传 IP，不能把 region/用户画像或城市自动映射为 IP。
- `POST https://api.deepseek.com/v1/tools/fetch`：单个 HTTP(S) URL，返回 title 和 Markdown content。
- Bearer Key 仅服务端；不把 API Key 放在网页、公开日志、版本库或 Next 的公开环境变量中。

代码：`infra/providers/deepseek.py` 的 DeepSeekWebProvider 实现 SearchProvider + FetchProvider。
通用 Provider 协议不含供应商依赖。新增 SearchHitV1 / FetchedPageV1，由现有链路生成 JSON Schema 和 TS。
SearchHitV1 与 SourceV1 分开：搜索命中不能被当作已核实证据。

搜索保留供应商排名和 authority 元数据，但它们不是事实核验结果、预测置信度或概率。
日期未知时保留 null；已提供日期仍固定标记 unverified。Fetch 没有发布时间，不能用抓取时间补造。
搜索正文可为空；Fetch 正文缺失/空白则报错；Markdown 是不可信数据，不执行其中指令或 HTML。

`before:/after:` 只是检索语法，不能证明历史可获取性。适配器对 as_of 参数明确拒绝，
不静默把实时检索伪装历史快照。未来 M1 需要另外建立合法来源快照/vintage、元数据核验和许可记录。

## 错误、资源和费用

408 / 429 / 5xx、传输超时：有限指数退避重试；其余 4xx（含 401/402/403/404）立即报错。
不返回/记录供应商错误正文；不把余额不足、失败或错误字符串转换成成功搜索结果。
Search 空数组是正常无结果。禁止跟随 API 重定向；只向固定 api.deepseek.com 主机发送 Key。
每端点独立实例速率间隔与熔断，响应读取上限 2 MB；账号级/目标域名限流由供应商执行。

抓取前拒绝本地/私有 IP、内网主机、非 HTTP(S)、携带账号密码的 URL。
FutureOS 不直接连接目标网页；实际 DNS/导航/重定向由 DeepSeek Fetch 的远端安全策略执行。
当前本地校验不是完整 DNS 重绑定防护，也不宣称可代替未来真实接入的安全验收。

Search/Fetch 按请求计费（详见官方当前价格），本轮只用 httpx.MockTransport，不发生真实调用或费用。
不在产品中硬编码价格，也不自动降级其他付费/免费供应商。

## M0 运行方式

M0 Worker 继续只创建 MockSearchProvider / MockLLMProvider；新增 MockFetchProvider 可验证抓取端口。
`.env.example` 增加 DEEPSEEK_API_KEY 空占位。仅填 Key 不会开启真实调用，不会改变现有 DEMO 研究。
将来 M1 的研究入口确认后，由服务端显式实例化 DeepSeekWebProvider 并管理异步连接生命周期。
本轮未运行官方 API 的真实连通性/质量/授权测试，不声称真实接入验收通过。

原 Sky 仓库不再作为搜索/抓取运行依赖；只保留缓存去重、预算和观测设计的参考价值。
没有将它的 Agent 调度/总结流程移入 FutureOS。
