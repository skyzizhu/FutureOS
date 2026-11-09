import { randomUUID } from "node:crypto";
import {NextRequest,NextResponse} from "next/server";
import {backend} from "../../backend";
import {sameLocalOrigin} from "../../admin/origin";
const headers={"Cache-Control":"no-store","Pragma":"no-cache"};
export async function GET(request:NextRequest){
 const token=request.cookies.get("futureos_session")?.value;
 if(!token)return NextResponse.json({code:"AUTH_REQUIRED"},{status:401,headers});
 try{const response=await fetch(`${backend}/api/v1/auth/identity`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(10000)});return NextResponse.json(await response.json(),{status:response.status,headers});}
 catch{return NextResponse.json({code:"API_UNAVAILABLE"},{status:503,headers});}
}
async function readAuthBody(request: NextRequest): Promise<string | null> {
 const reader = request.body?.getReader();
 if (!reader) return "";
 const decoder = new TextDecoder();
 let size = 0;
 let text = "";
 try {
  for (;;) {
   const { done, value } = await reader.read();
   if (done) return text + decoder.decode();
   size += value.byteLength;
   if (size > 5000) {
    await reader.cancel();
    return null;
   }
   text += decoder.decode(value, { stream: true });
  }
 } finally {
  reader.releaseLock();
 }
}

export async function POST(request: NextRequest) {
 if (!sameLocalOrigin(request)) {
  return NextResponse.json({ code: "FORBIDDEN" }, { status: 403, headers });
 }
 try {
  const text = await readAuthBody(request);
  if (text === null) {
   return NextResponse.json({ code: "PAYLOAD_TOO_LARGE" }, { status: 413, headers });
  }
  let data;
  try {
   data = JSON.parse(text);
  } catch {
   return NextResponse.json({ code: "VALIDATION_ERROR" }, { status: 422, headers });
  }
  const { action, email, password, verification_id, code, purpose, human_token } = data ?? {};
  if (!["register", "login", "email-code", "password-reset"].includes(action)) {
   return NextResponse.json({ code: "VALIDATION_ERROR" }, { status: 422, headers });
  }
  const existing = request.cookies.get("futureos_auth_device")?.value;
  const device = existing && /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(existing)
   ? existing : randomUUID();
  const upstream = await fetch(`${backend}/api/v1/auth/${action}`, {
   method: "POST",
   headers: {
    "User-Agent": (request.headers.get("user-agent") || "").slice(0, 500),
    "Accept-Language": (request.headers.get("accept-language") || "").slice(0, 120),
    "X-FutureOS-Auth-Device": device,
    "Content-Type": "application/json",
   },
   body: JSON.stringify(action === "email-code" ? { email, purpose, human_token }
    : action === "login" ? { email, password, human_token }
    : { email, password, verification_id, code }),
   cache: "no-store",
   signal: AbortSignal.timeout(15000),
  });
  const result = await upstream.json();
  const retry = upstream.headers.get("Retry-After");
  const response = NextResponse.json(
   upstream.ok ? (action === "login" || action === "register" ? result.identity : result)
    : { code: result.code, message: result.message },
   {
    status: upstream.status,
    headers: { ...headers, ...(retry && /^\d{1,5}$/.test(retry) ? { "Retry-After": retry } : {}) },
   }
  );
  if (device !== existing) {
   response.cookies.set("futureos_auth_device", device, {
    httpOnly: true, sameSite: "strict", secure: request.nextUrl.protocol === "https:",
    path: "/", maxAge: 30 * 86400,
   });
  }
  if (upstream.ok && (action === "login" || action === "register")) {
   response.cookies.set("futureos_session", result.access_token, {
    httpOnly: true, sameSite: "strict", secure: false, path: "/",
    expires: new Date(result.expires_at),
   });
  } else if (upstream.ok && action === "password-reset") {
   response.cookies.delete("futureos_session");
   response.cookies.delete("futureos_admin");
  }
  return response;
 } catch {
  return NextResponse.json(
   { code: "AUTH_UNAVAILABLE", message: "请求未完成，请稍后再试" },
   { status: 503, headers }
  );
 }
}
export async function DELETE(request:NextRequest){
 if(!sameLocalOrigin(request))return NextResponse.json({code:"FORBIDDEN"},{status:403,headers});
 const token=request.cookies.get("futureos_session")?.value;
 try{if(token){const upstream=await fetch(`${backend}/api/v1/auth/logout`,{method:"POST",headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(10000)});if(!upstream.ok&&![401,403].includes(upstream.status))return NextResponse.json({code:"LOGOUT_UNAVAILABLE",message:"注销尚未完成，请重试"},{status:503,headers});}}
 catch{return NextResponse.json({code:"LOGOUT_UNAVAILABLE",message:"注销尚未完成，请重试"},{status:503,headers});}
 const response=NextResponse.json({ok:true},{headers});response.cookies.delete("futureos_session");return response;
}
