# ADR-006：M1 来源版本、时间视图与人工核实

状态：已采用。2026-11-01，用户验收 M0 后授权实施 M1。

## 数据边界

SourceDocument 是稳定 URL 身份；SourceVersion 是追加写的时间/内容/许可快照；
EvidenceClaim 是带原文片段、定位、事实/观点/假设分类和人工核实记录的独立主张。
SearchHit/FetchedPage 永远不是已核实证据。正文作为不可信文本，不执行网页中的指令。
所有来源、指标、信号和案例均带 DEMO/REAL，去重和关联不跨两类数据。

来源 hash 针对保留文本；另以规范化 URL + 元数据/内容快照 hash 保证重复导入幂等。
移除已知跟踪参数，保留业务参数及同名参数的相对顺序。SHA-256 URL 指纹避免长 URL 的 B-tree 长度限制。
相同文本、归一化近似转载（至少100字符，5-gram Jaccard >=0.85）、声明的原文链接可归同源簇。
相似度规则是保守去重启发式，不是通用语义同源识别；近似匹配目前检查最近1000个同标签版本。
信号独立来源数从关联表 DISTINCT 来源簇计算，不能以 URL/主张条数代替。

## 时间与版本

- published_at：来源公开时间，可以未知；event_at 与之分开。
- available_at：**该版本**可以被研究者获取的时点；unknown 为 null。
- observed_now：服务端分配当前采集时刻，不能把实时抓取的旧日期补成历史快照。
- verified_archive/verified_release：管理员必须提交时间及可复核依据，属于人工证明记录，不代表系统自动验证归档真实性。
- ingested_at：系统收到资料的时间；verified_at/verified_by 单独记录管理员何时核实，不能冒充发布时间。
- claim known_at 继承已证明的版本可用时间；历史资料的现代人工标注不代表系统当时真的预测过。

指标修订使用独立行，按 indicator/period/revision 唯一。新修订的 available_at 必须严格递增。
as-of 查询取每个统计期当时可获取的最新有效修订，排除 UNVERIFIED；DEMO_DATA 只能属于 DEMO 数据集。
来源版本缺失、晚于指标可用时点、同一修订号内容不同等均返回具名错误。

source_documents/groups/versions、evidence_claims、indicators/vintages、historical_cases/events
由 PostgreSQL UPDATE/DELETE 触发器禁止原地改写；SQLite 测试安装等价触发器。
合法更正追加来源/指标版本，当前不提供篡改/删除历史的普通 API。
测试库通过 TRUNCATE 清理，需显式 _test 库名；迁移回滚是受控 DDL，不作为产品删除入口。
[PostgreSQL 触发器文档](https://www.postgresql.org/docs/16/plpgsql-trigger.html)。

历史案例背景固定在 cutoff，事后结果单独按 known_at 保存。as-of < cutoff 拒绝查看该案例背景；
等于 cutoff 的视图不返回未来结果或成功/失败标签；之后才按可用时点开放结果。
夹具含成功和失败两条合成路径，不把它们声称为真实历史预测成绩。

当前视图支持新导入的历史归档补全资料；尚未冻结整个研究输入数据集。
M2 必须冻结具体来源/指标版本和输入 hash，不能把可补全的历史查询当作不可变研究存档。

## 信号与接口

M1 仅创建 candidate 信号，不发布预测。已核实、时间有效的 fact 才能进入信号；
默认阶段 unknown，人工可指定阶段。关键词规则版本 signals-keywords-v1，配置化12领域数据字典；
它只提示候选领域，不是因果发现、概率评分或通用跨领域研究。

所有 M1 API 在 /api/v1/admin 下；普通 DEMO 用户不能访问来源或提升自身角色。
Web 工作台要求用户主动输入管理员令牌，由 API 验证角色；HttpOnly/SameSite Strict 本地 cookie，
写操作检查浏览器 Origin/Host 且仅允许 localhost/127.0.0.1。
此身份仍是开发身份，非生产认证，不允许公开部署。
