import {NextRequest,NextResponse} from "next/server";
import {backend} from "../../../backend";
import {sameLocalOrigin} from "../../origin";
const headers={"Cache-Control":"no-store","Pragma":"no-cache"};
export async function GET(request:NextRequest,{params}:{params:Promise<{action:string}>}){
 const{action}=await params;if(action!=="sessions")return NextResponse.json({code:"NOT_FOUND"},{status:404,headers});
 const token=request.cookies.get("futureos_admin")?.value;if(!token)return NextResponse.json({code:"AUTH_REQUIRED"},{status:401,headers});
 try{const r=await fetch(`${backend}/api/v1/me/sessions`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(10000)});return NextResponse.json(await r.json(),{status:r.status,headers});}catch{return NextResponse.json({code:"AUTH_UNAVAILABLE"},{status:503,headers});}
}
export async function POST(request:NextRequest,{params}:{params:Promise<{action:string}>}){
 if(!sameLocalOrigin(request))return NextResponse.json({code:"FORBIDDEN"},{status:403,headers});
 try{
  const{action}=await params;
  if(!["bootstrap","login","enroll","verify","step-up","recovery-codes","logout","revoke-session","revoke-all"].includes(action))return NextResponse.json({code:"NOT_FOUND"},{status:404,headers});
  const text=await request.text();if(text.length>5000)return NextResponse.json({code:"PAYLOAD_TOO_LARGE"},{status:413,headers});
  const body=text?JSON.parse(text):{};const token=request.cookies.get("futureos_admin")?.value;
  let path=`admin-auth/${action}`;let method="POST";
  if(action==="revoke-all")path="me/sessions/revoke-all";
  if(action==="revoke-session"){if(!/^[0-9a-f-]{36}$/.test(body.session_id||""))return NextResponse.json({code:"VALIDATION_ERROR"},{status:422,headers});path=`me/sessions/${body.session_id}`;method="DELETE";}
  const r=await fetch(`${backend}/api/v1/${path}`,{method,headers:{"User-Agent":(request.headers.get("user-agent")||"").slice(0,500),"Content-Type":"application/json",...(token?{Authorization:`Bearer ${token}`}:{})},body:method==="DELETE"?undefined:JSON.stringify(body),cache:"no-store",signal:AbortSignal.timeout(20000)});
  const data=await r.json();const retry=r.headers.get("Retry-After");const outHeaders={...headers,...(retry&&/^\d{1,5}$/.test(retry)?{"Retry-After":retry}:{})};
  if(action==="logout"&&[200,401,403].includes(r.status)){const out=NextResponse.json({ok:true},{headers});out.cookies.delete("futureos_admin");return out;}
  if(!r.ok)return NextResponse.json({code:data.code,message:data.message},{status:r.status,headers:outHeaders});
  if(data.access_token){const out=NextResponse.json({identity:data.identity,recovery_codes:data.recovery_codes||[]},{headers});out.cookies.set("futureos_admin",data.access_token,{httpOnly:true,sameSite:"strict",secure:false,path:"/",expires:new Date(data.expires_at)});return out;}
  const out=NextResponse.json(data,{headers});if(action==="revoke-all")out.cookies.delete("futureos_admin");return out;
 }catch{return NextResponse.json({code:"AUTH_UNAVAILABLE",message:"请求未完成，请重试登录"},{status:503,headers});}
}
