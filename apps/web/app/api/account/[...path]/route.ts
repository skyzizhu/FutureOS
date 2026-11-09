import {NextRequest,NextResponse} from "next/server";
import {backend} from "../../backend";
import {sameLocalOrigin} from "../../admin/origin";
const privateHeaders={"Cache-Control":"no-store","Pragma":"no-cache"};
async function forward(request:NextRequest,{params}:{params:Promise<{path:string[]}>}){
 try{
  const{path}=await params;
  if(!["me","research","reports","recommendations","forecasts","jobs","taxonomies","notifications","billing"].includes(path[0])||path.some(x=>!/^[-a-zA-Z0-9]+$/.test(x)))return NextResponse.json({code:"NOT_FOUND"},{status:404,headers:privateHeaders});
  const token=request.cookies.get("futureos_session")?.value;
  if(!token&&path[0]!=="taxonomies")return NextResponse.json({code:"AUTH_REQUIRED"},{status:401,headers:privateHeaders});
  if(request.method!=="GET"&&!sameLocalOrigin(request))return NextResponse.json({code:"FORBIDDEN"},{status:403,headers:privateHeaders});
  const body=request.method==="GET"?undefined:await request.text();
  if(body&&body.length>150000)return NextResponse.json({code:"PAYLOAD_TOO_LARGE"},{status:413,headers:privateHeaders});
  const response=await fetch(`${backend}/api/v1/${path.join("/")}${request.nextUrl.search}`,{method:request.method,headers:{...(token?{Authorization:`Bearer ${token}`}:{ }),"Content-Type":"application/json","Idempotency-Key":request.headers.get("Idempotency-Key")||""},body,cache:"no-store",signal:AbortSignal.timeout(20000)});
  if(response.ok && path.at(-1)==="download")return new NextResponse(await response.text(),{status:response.status,headers:{...privateHeaders,"Content-Type":"text/markdown; charset=utf-8","Content-Disposition":`attachment; filename="futureos-report-${path.at(-2)}.md"`}});
  const result=NextResponse.json(await response.json(),{status:response.status,headers:privateHeaders});
  if(response.ok&&((request.method==="DELETE"&&path.join("/")==="me/data")||path.join("/")==="me/sessions/revoke-all"))result.cookies.delete("futureos_session");
  return result;
 }catch{return NextResponse.json({code:"API_UNAVAILABLE"},{status:503,headers:privateHeaders});}
}
export const GET=forward;export const POST=forward;export const PUT=forward;

export const DELETE=forward;
