import Link from "next/link";
export default function Page(){return <section><h1>个人数据已删除</h1><p>本地账号和会话已撤销，私人画像、报告与邮件内容已清除。必要计费审计保留不含邮箱、画像和报告的随机标识；公开共享研究保留。</p><p>历史加密备份按保留策略到期清除，恢复时必须重放删除登记。</p><Link href="/auth/login">返回登录或创建新账号</Link></section>;}
