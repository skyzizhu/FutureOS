import {NextRequest,NextResponse} from "next/server";
import {sameLocalOrigin} from "../origin";
import {backend,demoOnly} from "../../backend";
async function forward(request:NextRequest,{params}:{params:Promise<{path:string[]}>}) {
 try {
  demoOnly();
  const token=request.cookies.get("futureos_admin")?.value;
  if(!token) return NextResponse.json({code:"AUTH_REQUIRED"},{status:401});
  if(request.method!=="GET" && !sameLocalOrigin(request)) return NextResponse.json({code:"FORBIDDEN"},{status:403});
  const {path}=await params;
  if(!["sources","evidence","indicators","signals","historical-cases","web-access","research","review","monitor","costs","readiness","security"].includes(path[0]) || path.some(x=>!/^[-a-zA-Z0-9]+$/.test(x))) return NextResponse.json({code:"NOT_FOUND"},{status:404});
  const body=["POST","PUT"].includes(request.method)?await request.text():undefined;
  if(body && body.length>150000) return NextResponse.json({code:"PAYLOAD_TOO_LARGE"},{status:413});
  const response=await fetch(`${backend}/api/v1/admin/${path.join("/")}${request.nextUrl.search}`,{method:request.method,headers:{Authorization:`Bearer ${token}`,"Content-Type":"application/json","Idempotency-Key":request.headers.get("Idempotency-Key") || ""},body,cache:"no-store",signal:AbortSignal.timeout(25000)});
  return NextResponse.json(await response.json(),{status:response.status,headers:{"Cache-Control":"no-store"}});
 } catch {return NextResponse.json({code:"API_UNAVAILABLE"},{status:503});}
}
export const GET=forward;
export const POST=forward;

export const PUT=forward;
