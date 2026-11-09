import type { Metadata } from "next";
import { themeBootstrap } from "./components/ui/theme-bootstrap";
import Shell from "./components/consumer/shell";
import {
  BRAND_MARK,
  BRAND_NAME,
  BRAND_TAGLINE,
} from "./components/consumer/brand";
import "./style.css";
import "./consumer.css";
import "./ui.css";
import "./navigation.css";
import "./home-discovery.css";
export const metadata: Metadata = {
  title: {
    default: `${BRAND_NAME} · ${BRAND_TAGLINE}`,
    template: `%s · ${BRAND_NAME}`,
  },
  icons: { icon: BRAND_MARK },
  description:
    "面向未来行业与机遇的预测 Agent，目标是通过 AI 持续关注行业动态，形成趋势与机遇预测报告。当前提供公开报告与演示研究体验。",
};
export default function Layout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <head>
        <meta name="color-scheme" content="light dark" />
        <script dangerouslySetInnerHTML={{ __html: themeBootstrap }} />
      </head>
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
