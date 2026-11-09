# 互联网与信息技术细分选项

2026-11-02。根据用户指定调整当前产品目录：

- “信息技术”显示为“互联网与信息技术”，technology 代码保持不变。
- 新增“产品经理”与“UI设计师”，作为其二级选项；23个一级、261个二级。
- “暂不适用职业行业”改为“暂不按职业分类（学生／退休等）”，选中后解释身份兜底用途及仍可关注感兴趣的行业。
- 新增0018_tech_roles迁移，为数据库追加两个细分；不改写旧画像、快照、分类代码及历史不可变目录行。当前API展示名来自产品目录v2.1，遵循既有目录接口设计。见ADR-022补充。

验收完成：`make check`（Ruff、格式、ESLint、mypy 97 源文件、TypeScript、427 pytest）、`make build` 和原生 `make local-verify`（427 pytest、22 浏览器流程、持久队列 smoke）全部通过。最后修改的迁移断言亦在原生全量回归中通过。唯一 Python 警告为已有 Starlette TestClient/httpx 弃用提示。

接口回归验证新选项和旧 software 选项均可保存/重读，分类父子关系正常；迁移回归验证两个新选项直接落库。浏览器回归验证父级新名称、两个子项、身份兜底说明和原有画像填写流程。截图为 `evidence/profile-technology-roles.png`，使用虚构测试账号。

回归使用独立 _test 数据库、本地验证码预览与虚构账号，未调用真实 SMTP、Turnstile 或 DeepSeek。完整命令记录在 `evidence/taxonomy-roles/`；正常环境保留原有配置，数据库升级至0018_tech_roles。

