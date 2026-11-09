# 契约 v1.0

唯一来源：services/prediction_engine/contracts/models.py 与 providers.py。
`make contracts` 导出 packages/contracts/schemas/*.json、openapi.json、generated/domain.d.ts、generated/api.d.ts。
Pydantic → JSON Schema + FastAPI OpenAPI → 自动 TypeScript。

所有 DTO 禁止额外字段、冻结对象；ID 为 UUID，时间为有时区时间。
正式 ForecastVersionV1 必须具备可验证目标、基线、验证来源与规则、期限、证据、反证列表和失效条件。
M0 仅允许 uncalibrated / qualitative_assessment，不提供虚构的数值概率。
报告必须引用具体 forecast_version_id，个人影响必须绑定 user_id / profile_snapshot_id。

M0 开放健康、me、DEMO 任务提交/轮询和受保护的 admin overview；后续管理路由见下文。
DEMO 结果仅为 hypothesis，不是 ForecastVersion、用户正式报告或准确率证据。

19.4 节错误码保留：VALIDATION_ERROR/AUTH_REQUIRED/FORBIDDEN/RATE_LIMITED/ENTITLEMENT_REQUIRED/
ENTITLEMENT_RESERVED/PROVIDER_UNAVAILABLE/EVIDENCE_UNVERIFIED/FORECAST_REVIEW_BLOCKED/JOB_FAILED/EMAIL_NOT_CONSENTED。
尚未实现的领域路由不伪造响应。当前另有 NOT_FOUND、IDEMPOTENCY_CONFLICT、DEPENDENCY_UNAVAILABLE、INTERNAL_ERROR。

搜索/抓取补充：SearchProvider 返回 SearchHitV1（日期允许未知，固定 unverified）；FetchProvider 返回 FetchedPageV1。
SourceV1 保留为来源对象契约，不再由搜索返回值直接充当。搜索日期是供应商元数据，尚未核实；
抓取仅有正文与检索时间，不补造 published_at / available_at。25 个 Schema 已重新导出。


M1：现共43个生成的域 Schema。增加 SourceImport/SourceVersion/EvidenceClaim、IndicatorDefinition/Observation、
Signal、HistoricalCase 和 Web 预览契约；维护时间依据、许可、人工作证、DEMO/REAL 与来源版本引用。
Schema 版本仍为1.0；M0 未作为外部稳定API发布，SearchHit 和正式来源/证据继续分开。


M2：当时共55个域 Schema。新增 ResearchSubmit/Snapshot/Narrative、MechanismEdge、AnalogyAssessment、Scenario、
Baseline、M2Draft/ResearchResult、ResearchAccepted/RunView/ReplayResult。JobV1.result 现在是旧 DEMO 结果与 M2 结果的联合类型。
M2Draft.status 固定 internal_unreviewed、publication_allowed 固定 false；内部 draft_forecast 不等于正式 ForecastVersion。

M3：现共67个域 Schema。新增审查报告/裁决/定向复核/发布版本/预登记协议与解析结果；契约仍从 Pydantic 自动生成。

M4：现共86个域 Schema。新增本地账号/会话、画像/最小快照、首次报告权益、个人影响、建议、
私有报告与邮件预览/授权 DTO；JobV1.result 增加 UserReportResultV1，仍不返回私有正文到通用作业结果。
