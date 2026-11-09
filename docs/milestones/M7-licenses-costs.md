# M7 许可、依赖与成本审计

2026-11-02。本文件记录工程检查及未决项，不是法律意见或生产授权。

## 软件与数据

Python 依赖清单见 evidence/M7-python-dependencies.json；JS 锁文件许可证计数见 evidence/M7-js-license-counts.json。
许可证元数据只是线索，不能取代逐包 LICENSE/NOTICE/传递二进制审查。项目自有 workspace 未声明许可证，发布前需确定。
sharp/libvips 的跨平台预编译包包含 LGPL-3.0-or-later，需核对实际分发的二进制及替换/告知义务，不能把所有依赖概括为 MIT。

PostgreSQL 使用 [PostgreSQL License](https://www.postgresql.org/about/licence/)。
Redis 许可证随版本而变：[官方说明](https://redis.io/legal/licenses/)；当前本地 redislite 嵌入 Redis 6.2.14，PostgreSQL二进制16.2，版本记录在最终运行证据，不能用 Python redis 客户端版本代替服务器版本。CI 既有 Redis 7.4 与本机不同，商用/再分发前分别审查。
现有真实资料只保留必要引用和摘要。GitHub 项目需按冻结时点的仓库 LICENSE 确认；当前上游 [Playwright](https://github.com/microsoft/playwright/blob/main/LICENSE) 和 [Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/main/LICENSE) 的 Apache-2.0 不自动证明历史抓取/第三方内容的许可。
厂商博客/说明页面的 quote_only 记录不等于全文再分发授权。`/admin/readiness` 展示来源许可分布和 REAL 空许可说明，授权充分性仍需人工确认。

DeepSeek [Search/Fetch 接口](https://api-docs.deepseek.com/zh-cn/guides/search/)使用固定服务端出口，模型和资料来源许可分别记录。接口文档不是商用合同、留存/地域/隐私授权；正式上线前审核供应商条款及数据处理约定。
本轮模型只接收冻结公共研究输入，无个人画像，不自动搜索或发送邮件。

## 安全依赖

首次 Python 审计发现 cryptography 48.0.1 的已知公告，升级到50.0.2并更新锁文件。修复依据为[上游 changelog](https://cryptography.io/en/latest/changelog/)。本系统使用 AES-GCM，不据此推断旧 PKCS7 公告已被实际利用。
复审结果见 evidence/M7-dependency-audit.json；“未发现已知漏洞”只代表该时点/服务覆盖范围，不能代表零漏洞。
npm 镜像端不实现 security/advisories/bulk，必须使用官方审计结果或明确记录未完成，不能把404解释为无漏洞。

## 本轮真实调用与预算

唯一新增模型验证见 evidence/M7-real-validation.json：deepseek-flash，1次请求，3126输入+511输出=3637tokens，上限4096输出。
使用此前已核实的冻结公共输入，未宣称抓取了最新新闻。独立 Critic 结果 annotate，保留内部研究；没有新公开版本，没有真人独立复核，不代表预测有效性验证。

未拿到供应商账单与缓存命中/实际单价核对，因此人民币成本未知，不用猜测的单价输出费用。成本页保留单位用量；沙盒套餐价格为合成示例，不构成真实收费。
当前显式研究每账号待处理上限20；手动搜索每日20次/每分钟5次，模型每日5次预留，单次最多4096输出；幂等请求复用旧任务，失败/取消释放研究额度，未知供应商结果不自动付费重试。
本地容量测试为20任务/4线程及租约/失败回归，不据此给出生产QPS、延迟百分位、可用性或盈利承诺。

官方 npm 全依赖审计：13个 moderate 依赖链条目，根因同一 [minimatch GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249)；high/critical为0。仅开发工具 ESLint/类型与契约生成链可达，运行时 omit=dev 审计为0。修复要求minimatch11.0.1；旧工具依赖存在不同主版本API，未强制覆盖或按audit建议降级到过时ESLint。此项风险仍开放：仅运行受信任的仓库glob/schema，不接受外部配置；正式发布前验证兼容升级并复审。

Python/npm审计不覆盖嵌入PostgreSQL/Redis/OpenSSL等原生二进制的完整CVE生命周期。当前仅loopback开发运行；生产前必须选择受支持、及时修补的服务器版本并重新做迁移/恢复与漏洞验收，不沿用当前本地打包版本直接上线。
