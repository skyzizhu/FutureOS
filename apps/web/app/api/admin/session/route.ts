import {NextRequest,NextResponse} from "next/server";
import {sameLocalOrigin} from "../origin";
import {backend,demoOnly} from "../../backend";
export async function POST(request:NextRequest) {
 try {
  demoOnly();
  if(!sameLocalOrigin(request)) return NextResponse.json({code:"FORBIDDEN"},{status:403});
  const body=await request.json();
  if(typeof body.token!=="string" || body.token.length>256) return NextResponse.json({code:"AUTH_REQUIRED"},{status:401});
  const response=await fetch(`${backend}/api/v1/me`,{headers:{Authorization:`Bearer ${body.token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});
  const me=await response.json();
  if(!response.ok || me.role!=="admin") return NextResponse.json({code:"FORBIDDEN"},{status:403});
  const result=NextResponse.json({role:"admin"});
  result.cookies.set("futureos_admin",body.token,{httpOnly:true,sameSite:"strict",secure:false,path:"/",maxAge:3600});
  return result;
 } catch {return NextResponse.json({code:"AUTH_UNAVAILABLE"},{status:503});}
}
export async function DELETE(request:NextRequest) {
 if(!sameLocalOrigin(request)) return NextResponse.json({code:"FORBIDDEN"},{status:403});
 const response=NextResponse.json({ok:true});response.cookies.delete("futureos_admin");return response;
}
