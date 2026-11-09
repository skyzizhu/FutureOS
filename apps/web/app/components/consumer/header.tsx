"use client";

import {
  ArrowUpRight,
  Bell,
  Buildings,
  ChatCircleDots,
  Compass,
  CreditCard,
  List,
  MagnifyingGlass,
  ShieldCheck,
  SignIn,
  SlidersHorizontal,
  User,
  X,
} from "@phosphor-icons/react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Button } from "../ui/controls";
import { BRAND_MARK, BRAND_NAME, BRAND_TAGLINE } from "./brand";
import { ThemeMenu } from "./theme";

const destinations = [
  {
    href: "/",
    label: "发现",
    icon: Compass,
    matches: (path: string) =>
      path === "/" || path.startsWith("/community/reports/"),
  },
  {
    href: "/industries",
    label: "行业",
    icon: Buildings,
    matches: (path: string) =>
      path === "/industries" || path.startsWith("/industries/"),
  },
  {
    href: "/chat",
    label: "预测对话",
    icon: ChatCircleDots,
    matches: (path: string) => path === "/chat",
  },
  {
    href: "/dashboard",
    label: "我的",
    icon: User,
    matches: (path: string) =>
      /^\/(dashboard|reports|recommendations|settings|account|billing|notifications|onboarding)(\/|$)/.test(
        path,
      ),
  },
];
const accountLinks = [
  { href: "/dashboard", label: "个人中心", icon: User },
  { href: "/settings", label: "画像与隐私", icon: SlidersHorizontal },
  { href: "/account/security", label: "账号安全", icon: ShieldCheck },
  { href: "/billing", label: "套餐与账单", icon: CreditCard },
];

type Panel = "navigation" | "account";

export default function Header({
  path,
  identity,
  loading,
  unread,
}: {
  path: string;
  identity: { email_masked: string } | null;
  loading: boolean;
  unread: number;
}) {
  const [panel, setPanel] = useState<Panel | null>(null);
  const nav = useRef<HTMLElement>(null);
  const account = useRef<HTMLDivElement>(null);
  const navTrigger = useRef<HTMLButtonElement>(null);
  const accountTrigger = useRef<HTMLButtonElement>(null);
  const active = destinations.findIndex((item) => item.matches(path));

  useEffect(() => setPanel(null), [path]);
  useEffect(() => {
    if (!panel) return;
    const surface = panel === "navigation" ? nav.current : account.current;
    const trigger =
      panel === "navigation" ? navTrigger.current : accountTrigger.current;
    if (!surface || !trigger) return;
    const first = surface.querySelector<HTMLAnchorElement>(
      panel === "navigation" && active !== -1 ? "a[aria-current]" : "a",
    );
    first?.focus({ preventScroll: true });
    const closeOutside = (event: Event) => {
      if (
        event.target instanceof Node &&
        !surface.contains(event.target) &&
        !trigger.contains(event.target)
      )
        setPanel(null);
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !event.defaultPrevented) {
        event.preventDefault();
        setPanel(null);
        trigger.focus();
      }
    };
    const compact = window.matchMedia("(max-width: 980px)");
    const resize = () => {
      if (panel === "navigation" && !compact.matches) setPanel(null);
    };
    document.addEventListener("pointerdown", closeOutside);
    document.addEventListener("focusin", closeOutside);
    document.addEventListener("keydown", escape);
    compact.addEventListener("change", resize);
    return () => {
      document.removeEventListener("pointerdown", closeOutside);
      document.removeEventListener("focusin", closeOutside);
      document.removeEventListener("keydown", escape);
      compact.removeEventListener("change", resize);
    };
  }, [panel, active]);

  function search(event: React.MouseEvent<HTMLAnchorElement>) {
    setPanel(null);
    if (
      path !== "/" ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    const field = document.getElementById("report-search");
    if (!field) return;
    event.preventDefault();
    field.focus({ preventScroll: true });
    field.scrollIntoView({
      block: "center",
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto"
        : "smooth",
    });
  }

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link
          className="site-brand"
          href="/"
          aria-label={`${BRAND_NAME} 首页`}
          onClick={() => setPanel(null)}
        >
          <Image src={BRAND_MARK} alt="" width={38} height={38} unoptimized />
          <span className="site-brand-type">
            <strong>{BRAND_NAME}</strong>
            <span>{BRAND_TAGLINE}</span>
          </span>
        </Link>
        <nav
          id="site-primary-nav"
          ref={nav}
          className="site-navigation"
          data-open={panel === "navigation"}
          aria-label="主导航"
        >
          <div className="site-nav-track" data-active={active}>
            {destinations.map(({ href, label, icon: Icon }, index) => (
              <Link
                key={href}
                href={href}
                aria-current={
                  index === active
                    ? path === href
                      ? "page"
                      : "location"
                    : undefined
                }
                onClick={() => setPanel(null)}
              >
                <Icon
                  size={17}
                  weight={index === active ? "fill" : "regular"}
                  aria-hidden="true"
                />
                {label}
              </Link>
            ))}
          </div>
          <div className="site-nav-utilities">
            <Link href="/?search=1" onClick={search}>
              <MagnifyingGlass size={17} aria-hidden="true" />
              搜索公开报告
            </Link>
            {identity ? (
              <Link href="/notifications" onClick={() => setPanel(null)}>
                <Bell size={17} aria-hidden="true" />
                通知
                {unread > 0 && (
                  <span className="site-nav-count">
                    {unread > 99 ? "99+" : unread}
                  </span>
                )}
              </Link>
            ) : (
              !loading && (
                <Link
                  href="/auth/login?mode=login"
                  onClick={() => setPanel(null)}
                >
                  <User size={17} aria-hidden="true" />
                  登录
                </Link>
              )
            )}
          </div>
        </nav>
        <div className="site-header-actions">
          <div
            className="site-utility-group"
            role="group"
            aria-label="搜索与外观"
          >
            <Link
              className="site-icon site-desktop-action"
              href="/?search=1"
              aria-label="搜索公开报告"
              title="搜索公开报告"
              onClick={search}
            >
              <MagnifyingGlass size={18} aria-hidden="true" />
            </Link>
            <ThemeMenu />
          </div>
          {identity ? (
            <>
              <Link
                className="site-icon site-desktop-action"
                href="/notifications"
                aria-label={unread ? `通知，${unread} 条未读` : "通知"}
                title="通知"
              >
                <Bell
                  size={18}
                  weight={path === "/notifications" ? "fill" : "regular"}
                  aria-hidden="true"
                />
                {unread > 0 && <span className="site-notification-dot" />}
              </Link>
              <div className="site-account" ref={account}>
                <Button
                  ref={accountTrigger}
                  className="site-icon site-avatar"
                  aria-label="账号菜单"
                  title="账号菜单"
                  aria-expanded={panel === "account"}
                  aria-controls="site-account-panel"
                  onClick={() =>
                    setPanel(panel === "account" ? null : "account")
                  }
                >
                  <User size={18} weight="duotone" aria-hidden="true" />
                </Button>
                <div
                  id="site-account-panel"
                  className="site-account-panel"
                  hidden={panel !== "account"}
                >
                  <small>{identity.email_masked}</small>
                  {accountLinks.map(({ href, label, icon: Icon }) => (
                    <Link key={href} href={href} onClick={() => setPanel(null)}>
                      <Icon size={17} aria-hidden="true" />
                      {label}
                    </Link>
                  ))}
                </div>
              </div>
            </>
          ) : loading ? (
            <span className="site-identity-placeholder" aria-label="加载账号" />
          ) : (
            <>
              <Link
                className="site-login site-desktop-action"
                href="/auth/login?mode=login"
              >
                <SignIn size={15} aria-hidden="true" /> 登录
              </Link>
              <Link className="site-register" href="/auth/login">
                注册 <ArrowUpRight size={13} aria-hidden="true" />
              </Link>
            </>
          )}
          <Button
            ref={navTrigger}
            className="site-icon site-menu-toggle"
            aria-label={panel === "navigation" ? "关闭导航" : "展开导航"}
            aria-expanded={panel === "navigation"}
            aria-controls="site-primary-nav"
            onClick={() =>
              setPanel(panel === "navigation" ? null : "navigation")
            }
          >
            {panel === "navigation" ? (
              <X size={20} aria-hidden="true" />
            ) : (
              <List size={21} aria-hidden="true" />
            )}
            {unread > 0 && panel !== "navigation" && (
              <span className="site-notification-dot" />
            )}
          </Button>
        </div>
      </div>
    </header>
  );
}
