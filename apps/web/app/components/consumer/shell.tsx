"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { ArrowUpRight, ChatCircleDots } from "@phosphor-icons/react";
import Image from "next/image";
import Header from "./header";
import { BRAND_MARK, BRAND_NAME, BRAND_TAGLINE } from "./brand";
type Identity = { user_id: string; email_masked: string };
const IdentityContext = createContext<{
  identity: Identity | null;
  loading: boolean;
}>({ identity: null, loading: true });
export const useIdentity = () => useContext(IdentityContext);
export default function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const admin = path.startsWith("/admin");
  const home = path === "/";
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [loading, setLoading] = useState(true);
  const [unread, setUnread] = useState(0);
  useEffect(() => {
    let active = true;
    const load = () => {
      if (!identity || admin) {
        setUnread(0);
        return;
      }
      fetch("/api/account/me/community/notifications", { cache: "no-store" })
        .then(async (r) => (r.ok ? r.json() : []))
        .then((items: { read: boolean }[]) => {
          if (active) setUnread(items.filter((item) => !item.read).length);
        })
        .catch(() => {});
    };
    load();
    window.addEventListener("futureos:inbox-read", load);
    return () => {
      active = false;
      window.removeEventListener("futureos:inbox-read", load);
    };
  }, [identity?.user_id, admin, path]);
  useEffect(() => {
    let active = true;
    if (admin || path.startsWith("/auth/")) {
      setLoading(false);
      return;
    }
    fetch("/api/account/auth", { cache: "no-store" })
      .then(async (r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (active) setIdentity(data);
      })
      .catch(() => {})
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [admin, path]);
  if (admin)
    return (
      <div className="admin-surface">
        <header>
          <Link href="/">FutureOS</Link>
          <nav>
            <Link href="/admin">管理</Link>
            <Link href="/admin/monitor">拐点监控</Link>
            <Link href="/admin/readiness">质量与就绪</Link>
            <Link href="/admin/costs">研究成本</Link>
            <Link href="/admin/research">研究工作台</Link>
            <Link href="/admin/review">审查与评估</Link>
            <Link href="/admin/evidence">证据工作台</Link>
          </nav>
        </header>
        <main>{children}</main>
      </div>
    );
  return (
    <IdentityContext.Provider value={{ identity, loading }}>
      <div className={home ? "consumer-surface consumer-home" : "consumer-surface"}>
        <a className="skip-link" href="#page-content">
          跳到正文
        </a>
        <Header
          path={path}
          identity={identity}
          loading={loading}
          unread={unread}
        />
        <main
          id="page-content"
          className={
            path === "/chat" ? "consumer-main chat-main" : "consumer-main"
          }
        >
          <div key={path} className="page-transition">
            {children}
          </div>
        </main>
        <footer className="site-footer">
          <Link className="footer-brand" href="/">
            <Image src={BRAND_MARK} alt="" width={22} height={22} unoptimized />
            {BRAND_NAME}
          </Link>
          {!home && <p>{BRAND_TAGLINE}</p>}
          <div>
            <Link href="/help">
              关于与服务说明 <ArrowUpRight size={12} />
            </Link>
            <Link href="/settings">隐私设置</Link>
            {!home && (
              <Link href="/chat">
                <ChatCircleDots size={14} /> 开始一段研究
              </Link>
            )}
          </div>
          <small>预测包含不确定性；演示内容始终明确标记。</small>
        </footer>
      </div>
    </IdentityContext.Provider>
  );
}
