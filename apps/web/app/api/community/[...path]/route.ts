import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "node:crypto";
import { sameLocalOrigin } from "../../admin/origin";
import { backend } from "../../backend";
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  const headers = { "Cache-Control": "no-store" };
  if (
    !["industries", "reports"].includes(path[0]) ||
    path.some((part) => !/^[-a-zA-Z0-9]+$/.test(part))
  )
    return NextResponse.json({ code: "NOT_FOUND" }, { status: 404, headers });
  try {
    const response = await fetch(
      `${backend}/api/v1/community/${path.join("/")}${request.nextUrl.search}`,
      { cache: "no-store", signal: AbortSignal.timeout(12000) },
    );
    const result = NextResponse.json(await response.json(), {
      status: response.status,
      headers,
    });
    if (response.ok && path[0] === "reports" && path.length === 2)
      readerCookie(request, result);
    return result;
  } catch {
    return NextResponse.json(
      { code: "API_UNAVAILABLE", message: "暂时无法加载，请稍后重试" },
      { status: 503, headers },
    );
  }
}

function readerCookie(request: NextRequest, response: NextResponse) {
  const stored = request.cookies.get("futureos_reader")?.value;
  const visitor =
    stored &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(
      stored,
    )
      ? stored
      : randomUUID();
  if (visitor !== stored)
    response.cookies.set("futureos_reader", visitor, {
      httpOnly: true,
      sameSite: "lax",
      secure: request.nextUrl.protocol === "https:",
      path: "/",
      maxAge: 60 * 60 * 24 * 30,
    });
  return visitor;
}
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const headers = { "Cache-Control": "no-store" };
  const { path } = await params;
  if (!sameLocalOrigin(request))
    return NextResponse.json({ code: "FORBIDDEN" }, { status: 403, headers });
  if (
    path.length !== 3 ||
    path[0] !== "reports" ||
    path[2] !== "read" ||
    !/^[0-9a-f-]{36}$/.test(path[1])
  )
    return NextResponse.json({ code: "NOT_FOUND" }, { status: 404, headers });
  const cookieResponse = NextResponse.json({});
  const visitor = readerCookie(request, cookieResponse);
  try {
    const upstream = await fetch(
      `${backend}/api/v1/community/reports/${path[1]}/read`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ visitor_id: visitor }),
        cache: "no-store",
        signal: AbortSignal.timeout(12000),
      },
    );
    const result = NextResponse.json(await upstream.json(), {
      status: upstream.status,
      headers,
    });
    if (upstream.ok)
      for (const cookie of cookieResponse.cookies.getAll())
        result.cookies.set(cookie);
    return result;
  } catch {
    return NextResponse.json(
      { code: "API_UNAVAILABLE" },
      { status: 503, headers },
    );
  }
}
