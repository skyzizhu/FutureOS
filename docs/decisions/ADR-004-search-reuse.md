# ADR-004：Sky Research Agent 搜索能力复用评估

状态：历史评估；搜索/抓取供应商选择已由 ADR-005 替代。日期：2026-11-01。

用户后续指定统一使用 DeepSeek Search/Fetch。下表保留原评估作为参考，不再计划移植 Tavily/DDGS、
trafilatura 或 Playwright 抓取链路；仍可参考缓存与观测思路。最新接入方式见 ADR-005。

参考仓库：[skyzizhu/sky-agent-mvp-stu](https://github.com/skyzizhu/sky-agent-mvp-stu)，
检查 commit `e82ad0d62fd4121c3f1ed01dca792f6701e127f1`，只读克隆在 .local/sky-agent-reference（不纳入交付或运行依赖）。
未安装该仓库依赖、执行其 start.sh、读取用户私有密钥或运行真实检索。

结论：可作为 SearchProvider / 抓取组件的来源。无需把整个深度研究内核移植进预测引擎。

| 现有组件 | 可复用内容 | FutureOS 接入要求 |
|---|---|---|
| common/tools.py:122 `_tavily_search` | Tavily 搜索请求与结果解析 | 配置注入替代全局 config；typed errors；限额/超时；保留 provider provenance |
| common/tools.py:140 `web_search` | Tavily → DDGS 降级、JSON 合法截断 | 输出强类型候选来源；不将“错误：...”字符串视为有效结果；显式记录降级原因 |
| common/tools.py:197 `fetch_url` | httpx + trafilatura 正文提取、SPA 检测 | 补 SSRF、DNS/IP/重定向检查、长度/类型限制、来源许可；正文是 untrusted data |
| common/tools.py:241 `fetch_js` | Playwright 渲染兜底 | 默认关闭；限 URL/资源/时间/并发，审计成本；不当作绕过站点权限的方法 |
| common/cache.py `SessionToolCache` | 查询去重、URL 缓存、域名失败感知 | cache key 增加 provider/as_of/region/授权范围；保留原始结果，不把提示语混入证据 |
| common/guardrails.py `Budget` | 用量记账和预算收尾思路 | 接入 ResearchRun 成本；超预算返回部分研究/失败，不能强制“完整成功” |
| common/observability.py | 执行流和事件思路 | 接入 FutureOS request/job/trace，脱敏并隔离用户 |

不可直接用作正式预测证据的原因：

1. web_search 只有 title/url/snippet；没有 published_at/available_at、指标 vintage 或可信历史快照。
   不得用检索时间补造发布时间，不得按当前搜索结果做可信历史回测。
2. 摘要可能只包含观点或转述；FutureOS 必须拆 Source / SourceVersion / EvidenceClaim，核实原文定位与独立来源簇。
3. fetch_url/fetch_js 只检查 HTTP(S) 前缀，follow_redirects 与浏览器导航没有阻止内网地址。
4. fuzzy query 缓存用词形相似度，可能把“增长/没有增长”等反向问题误合并；不能作为证据同源判断。
5. 工具同步阻塞且错误混合在字符串里；需独立适配器及受控执行器，不能直接阻塞 API event loop。
6. agent_core 的自由研究收尾、笔记记忆和多 worker 总结，不替代 FutureOS 的事实类型、as-of、独立 Critic、裁决与不可变发布。

建议 M1 实施：先把 web_search 输出当作 RawSearchHit（日期可未知），经元数据核实后转换 SourceV1；
无法核实日期/许可的候选不能进入受时间约束的证据视图。首轮先接一个合法 Provider，再加入抓取和降级。
M0 保留现有 SearchProvider 协议与 Mock，不对用户开启真实检索。

依赖：旧仓库混合了 openai/ddgs/trafilatura/httpx/mcp/playwright，范围较宽且无锁文件；
FutureOS 只引入实际抽取组件所需依赖并锁定。未找到独立 LICENSE；用户已说明该仓库为其编写，
当前只评估，不复制源码；将来实际引入时记录版权归属与第三方服务条款。

后续验证：缺失/伪造时间、同源转载、超时/429、错误文本、SSRF/重定向、注入内容、跨 as-of 缓存污染、
提供商切换、预算耗尽、用户隔离。它们属于真实接入的验收，不冒称 M0 已覆盖。
