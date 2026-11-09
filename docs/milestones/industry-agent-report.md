# 行业监听 Agent 单轮编排

实现检索覆盖补搜、分析阶段证据补搜和报告引用校验。通过现有 Search、Fetch 和结构化模型端口运行。草稿包含条件预测、反证、类比边界与可复查的行动。调度、报告入库和邮件交付的接入边界见 [行业监听架构草案](../industry-monitoring-design.md)。

运行 `uv run python -m scripts.industry_agent`，得到 DEMO 草稿。该样本执行 8 次搜索、6 次抓取和 5 次模型接口调用，分别补齐市场线索和季度量化指标。DEMO 模型接口使用确定性夹具。真实供应商入口使用现有配置闸门和 Fetch 白名单。

专项验收 `uv run pytest tests/unit/test_industry_agent.py -q` 为 3 passed。覆盖两个补搜循环、证据不足时停止写作、报告拒绝未知来源，以及个人字段留在本地。`make contracts` 生成 152 个领域 Schema 与 API 类型。`make build` 通过 Next.js 生产构建与 TypeScript 检查。

最终 `make check` 通过 Ruff、ESLint、TypeScript 与 99 个源文件的 mypy 检查，pytest 为 442 passed（187.69 秒）。最终 `make local-verify` 在隔离 PostgreSQL 测试库中完成 442 passed（183.95 秒），队列冒烟输出 `PASS: readiness -> accepted -> idempotent replay -> worker -> DEMO hypothesis`，Playwright 为 22 passed（2.6 分钟）。验收使用本地验证码预览与 Mock 研究数据。

首次原生回归因遗留本地进程占用端口退出。释放端口后的运行遇到引擎代码在测试期间变更，旧审查流程返回 `REVIEW_INPUT_CHANGED`。固定最终代码后重新执行完整验收并通过。命令输出位于 `.local/industry-agent-{contracts,build,check-final,native-final}.log`，结构化演示输出位于 `.local/industry-agent-demo.json`。

## 证据行业发展链

允许模型根据研究机制寻找当前行业或其他行业的历史过程。案例以背景、实际节点和有出处的结果组织，逐节点校验原文，并记录迁移条件与关键差异。其他行业的发展链可以单独支撑带条件的类比情景。报告引用的案例与节点可在结构化运行输出中查询。

本轮 `make contracts` 生成 154 个领域 Schema 与 API 类型。专项测试为 5 passed，新增场景覆盖跨行业链独立支撑条件草稿与拦截没有出处的结果节点。`make build` 通过。原生回归首次遇到旧来源组写入的 PostgreSQL 唯一索引竞争。该组的两个唯一键由同一身份派生，调整其插入以幂等处理任一唯一键冲突。最终 `make check` 为 446 passed（185.98 秒），原生后端为 446 passed（184.28 秒）。

最终 `make local-verify` 队列冒烟通过，Playwright 为 22 passed（2.6 分钟）。输出见 `.local/industry-chain-{contracts,build,check-final,native-final}.log`。
