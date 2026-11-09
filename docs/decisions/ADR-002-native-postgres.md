# ADR-002：原生本地 PostgreSQL + Redis

状态：已采用。日期：2026-11-01。用户明确覆盖计划中的 Docker 交付项。

最终选择 PostgreSQL，以便与未来线上环境一致。XAMPP 实际为 MariaDB 10.4.21；
曾验证其迁移与 Mock 测试兼容，用户随后要求直接使用 PostgreSQL。
已清理本次临时创建的 futureos_m0_demo/futureos_m0_test MariaDB 库及 futureos_local 账号，未改既有业务库。

无 Docker 依赖。`uv --group local` 安装 pgserver 提供的实际 PostgreSQL 二进制及 redislite 提供的实际 Redis。
它们是本机子进程，不是内存数据库模拟器；数据在 .local 下，停止后保留。
优先复用已运行的 Redis / redis-server。未发现系统 Redis，因此本机安装并使用项目内二进制。
原生管理器只监听 loopback；PostgreSQL 使用项目目录的 Unix socket，不占 MySQL 端口。
Web 3100 / API 8100 / Redis 6381，避开现有 3000 服务。Ctrl-C 停止本次启动的服务。

本地 PostgreSQL 16.2 / Redis 6.2.14 的便携构建用于隔离 DEMO。生产必须换成仍受支持且已更新的
PostgreSQL / Redis 服务，通过 DATABASE_URL / REDIS_URL 接入；不把便携构建视为生产安装方案。
当前 pgserver 默认 local trust 仅限该用户可访问的开发目录，.env 0600、数据目录 0700。
生产认证 / 密钥管理不在 M0 内，配置为 production 会拒绝启动。

SQLite 仅用于快速离线测试；本地最终验收在真实 PostgreSQL 上执行。
[pgserver](https://github.com/orm011/pgserver) / [redislite](https://github.com/yahoo/redislite)。
