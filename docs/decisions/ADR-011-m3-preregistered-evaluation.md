# ADR-011：M3 预登记评估与真实前瞻

状态：已采用，2026-11-01。

合成测试、历史时间截断和真实前瞻分别存储/统计，不把结构测试通过率包装成预测准确率。
EvaluationProtocol 在验证前冻结目标、阈值、来源、单位、as_of、due_at、输入 hash、模型、提示词和版本。
阈值必须解析自已发布草稿；同版本只有一个不可修改的协议。真实前瞻必须 REAL、输入 cutoff 距当前不超过24小时，
且登记在窗口开始前。不能用事后重新设置的窗口伪造提前预测。

到期解析只接受 M1 中已存档的 ObservationVintage，校验指标/地区/单位/标签/验证来源与统计期完全匹配，
并检查该版本当时确已发布可获取。每次结果追加，保留旧结果；支持 not_due、confirmed、disconfirmed、
inconclusive、unresolved_due_to_data。缺数据/网络故障不能当成预测正确，也不能默认当作事件未发生。

M2 主引擎没有数值点预测，所以不把阈值当成点预测，A/B MAE 缺失时保留 null。
数值评估纯函数支持登记点预测后的 A/B 绝对误差及持平基线误差；管理端当前实际只登记持平基线。
合成 A/B 另测量反证遗漏等实质问题减少量、差分、CPU 时间与额外模型调用；不能声称提高真实准确率。

35条故障题由代码作者逐项编写，包含明确2020年 cutoff、预期等级/裁决和失败样本。
独立人工题组评审尚未完成，保存 pending 状态，不将编码代理自检称为独立人工验收。
现代基础模型可能已知历史未来信息，时间过滤不能消除此类知识泄漏。

首条 REAL 前瞻仅预测 microsoft/playwright 在未来30天窗口中是否有公开稳定发布，
不是能力、就业或个人行动预测。官方功能文档只是候选机制线索；两条结果案例只证明公开发布/关闭事件，
不证明增长率或因果迁移。编码代理读取官方原文并检查短引用，未声称独立人工语义审查。

代码：scripts/m3_forward_start.py 只请求一次受预算约束的 DeepSeek 生成，持久化 run_id 后不自动重试；
scripts/m3_forward_resolve.py 到期前不联网，到期后最多10页官方 GitHub API 查询，
完整分页才可以输出事件0/1，否则记录数据不可用。没有定时任务或自动通知（属后续 M5）。
供应商用量保留原始 token 统计，金额以账单为准。参考：
[Google Gemini CLI](https://github.com/google-gemini/gemini-cli)、
[Microsoft Playwright](https://github.com/microsoft/playwright)、
[Anthropic 工具评估](https://www.anthropic.com/research/writing-tools-for-agents)、
[Stadia 官方说明](https://support.google.com/stadia/answer/9578631?hl=en)、
[Playwright 官方 releases API](https://api.github.com/repos/microsoft/playwright/releases)。
