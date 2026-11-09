# ADR-009：M2 单次结构化生成与成本恢复边界

状态：已采用。2026-11-01。

依据：[Chat Completions](https://api-docs.deepseek.com/zh-cn/api/create-chat-completion/)、
[模型信息](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)。

默认 Mock 使用固定、可重放的研究叙述，不调用外部服务，只允许 DEMO 输入。
DeepSeek 使用独立 LIVE_RESEARCH_ENABLED 开关，默认配置关闭；当前本机已为管理员手动启用。
默认模型 deepseek-flash，可通过 DEEPSEEK_RESEARCH_MODEL 配置，不改变独立 Search/Fetch 的接口选择。
M2 始终不自动搜索、发信或调用支付。

/chat/completions 使用 JSON 输出和明确的 JSON Schema 提示、非思考模式、最多4096输出 tokens、
输入文本上限50000字符、90秒超时、不提供工具、不自动重试。Worker 租约至少150秒。
输入含经过准入的事实、信号、当时可见案例、目标及计算基线；外部文本视为数据，不能改变工具权限。
返回必须 finish_reason=stop、JSON/Pydantic 合法，引用只能来自快照且不能遗漏已知反证；
未经校准的叙述百分比直接拒绝。数字观测/基线单独展示，不将检索排名或指标比例当作概率。

每次真实运行先持久化唯一 ModelCall 预留，每管理员滚动24小时最多5次。
started 状态崩溃后不重复发付费请求，而是终止并提示人工核对；已完成的响应可以在恢复时复用。
调用成功保存实际 model、后端 fingerprint、prompt/completion/total token 用量与结构化响应。
响应/最终状态只允许从 started 完成一次，之后数据库拒绝修改/删除。
超时或进程崩溃不能证明供应商没有计费；不展示自编价格或推断的扣费金额。

一次真实联调使用自编 DEMO 资料完成生成和重放，不将其称为真实世界研究或预测效果。
M2-deepseek-live.json 仅保存脱敏状态、hash和用量，不存 Key 或推理过程。
预留状态不明时暂不提供自动恢复 UI；管理员需核对供应商与任务状态，避免双重消费。
