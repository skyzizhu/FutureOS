export type {
  CommunityIndustryViewV1 as Industry,
  CommunityReportViewV1 as PublicReport,
} from "@futureos/contracts";
export type { ConversationViewV1 as Conversation } from "@futureos/contracts";
const messages: Record<string, string> = {
  AUTH_REQUIRED: "请先登录后继续。",
  LOCAL_ACCOUNT_REQUIRED: "请先注册或登录。",
  PROFILE_REQUIRED: "请先完善行业画像，再生成报告。",
  FIRST_REPORT_UNAVAILABLE:
    "首份免费报告已使用或正在生成。可以在我的报告中继续查看。",
  PUBLIC_REPORT_NOT_FOUND: "报告未公开或已撤回。",
  CONVERSATION_NOT_FOUND: "这段研究对话不存在。",
  API_UNAVAILABLE: "暂时连接不上服务，请稍后重试。",
};
export async function consumerApi<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await fetch(`/api/${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      messages[data.code] || data.message || "操作未完成，请重试。",
    );
  return data;
}
export const dateLabel = (value: string) =>
  new Date(value).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
export function loginHref(next: string) {
  return `/auth/login?mode=login&next=${encodeURIComponent(next)}`;
}

export function safeReturnPath(value: string, fallback = "/dashboard") {
  try {
    return value.startsWith("/") &&
      new URL(value, window.location.origin).origin === window.location.origin
      ? value
      : fallback;
  } catch {
    return fallback;
  }
}
