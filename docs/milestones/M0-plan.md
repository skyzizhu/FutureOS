# M0 实施与验收范围

基线：IMPLEMENTATION_PLAN.md v1.3，第 7、18.7、19、23、26 节。
用户随后明确：原生本地部署，不需要 Docker；最终直接使用 PostgreSQL；检查并安装 Redis。
另评估 sky-agent-mvp-stu 的搜索能力复用。本阶段完成后停止，等待 M0 验收。

- [x] 统一目录、Python/Node 锁文件、本地环境与启动工具。
- [x] 独立预测包及核心五对象、Critic、拐点、报告、权益与 Provider ports。
- [x] 生成 JSON Schema / OpenAPI / TypeScript；检查漂移。
- [x] API 健康检查、演示鉴权 / RBAC、请求日志、错误结构。
- [x] PostgreSQL 用户 / 作业 / 事件首迁移；DEMO 身份种子。
- [x] Worker 持久化幂等、有限重试、租约恢复、完成去重。
- [x] 六类 Mock Provider，禁用生产模式 / 真实发信收费。
- [x] Web 首页、认证占位、公共管理壳、DEMO 研究交互。
- [x] lint、typecheck、unit / contract / integration / security、浏览器 E2E。
- [x] 搜索参考仓库复用评估、ADR、启动说明及实际验收报告。

验收对象是基础架构及 Mock 连通性，不是预测准确率、生产认证或真实研究。
