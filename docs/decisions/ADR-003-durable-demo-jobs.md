# ADR-003：数据库持久化任务与最小权限 DEMO

状态：已采用。日期：2026-11-01。

M0 使用持久化 SQL 作业队列，Redis 提供唤醒提示；不引入 Celery 及另一套任务持久化状态。
条件 UPDATE 原子争抢、租约 fencing token 防过时 worker 提交；最多三次重试，失败不伪装成功。
DEMO outbox / inbox 与作业事务一致。完整调度、通知、死信运营和分布式限流在 M5。

本地三种固定身份：user / other-user / admin，令牌只存在后端或 Web 服务端；客户端不能提交角色。
管理权限不自动允许读取他人私有作业。未知和越权 job 均返回 404。
这是可测试的鉴权边界，不是生产登录。服务端生产配置拒绝启动。

Mock Email 仅接受 @example.invalid；Mock Payment 只返回 example.invalid 地址并校验 DEMO 签名。
LLM 返回固定 schema-valid 合成假设；不允许用户提示改变工具权限，不执行网络、发信、扣费。
Provider 策略以实例为边界提供超时、有限重试、间隔限制与熔断；尚非全局供应商限流。
