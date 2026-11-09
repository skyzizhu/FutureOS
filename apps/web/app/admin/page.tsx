import "server-only";
import Link from "next/link";
import {backend,demoOnly} from "../api/backend";
export const dynamic = "force-dynamic";
export default async function Admin() {
 let status = "API 暂不可用";
 try {
  demoOnly();
  const response = await fetch(`${backend}/api/v1/health/ready`,{cache:"no-store",signal:AbortSignal.timeout(5000)});
  const data = await response.json(); status = response.ok?`API 就绪 · DB ${data.database} · Redis ${data.redis}`:"依赖尚未就绪";
 } catch { /* Public admin shell exposes only readiness, not privileged data. */ }
 return <section><h1>管理台</h1><p className="badge">LOCAL</p><p><Link href="/admin/login">账号与双重认证登录</Link> · <Link href="/admin/security">管理员权限、会话与审计</Link></p><p><Link href="/admin/sources">进入来源与信号工作台</Link> · <Link href="/admin/research">进入研究草稿工作台</Link> · <Link href="/admin/review">进入审查与评估</Link></p><p>{status}</p><p>受保护的作业统计位于后端 /api/v1/admin/overview，需要独立管理员身份。此页面只展示公共健康状态。</p></section>;
}
