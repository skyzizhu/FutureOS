# FutureOS prediction engine — M0

独立 Python 包，只依赖 Pydantic。`contracts/` 是 DTO / Provider ports 的唯一来源；
`forecasting/demo.py` 是合成假设工作流，不实现真实预测、证据核实或发布。
其他目录是后续里程碑的边界占位，尚无业务实现。严禁导入 apps / infra / workers。

从仓库根运行 `uv build --package futureos-prediction-engine` 可生成独立 wheel。

M4 adds pure personalization/taxonomy, decision_value/rules and reporting/builder functions. They receive only consented profile DTOs and fixed published versions; they never load keys or call external models.
