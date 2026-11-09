import {NextRequest, NextResponse} from "next/server";
import {backend,demoToken,demoOnly} from "../../backend";
export async function POST(request:NextRequest) {
 try {
  demoOnly();
  const body = await request.text();
  if(body.length>4096) return NextResponse.json({code:"VALIDATION_ERROR"},{status:413});
  const response = await fetch(`${backend}/api/v1/demo/research`,{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${demoToken}`,"Idempotency-Key":request.headers.get("Idempotency-Key")||""},body,signal:AbortSignal.timeout(5000)});
  return NextResponse.json(await response.json(),{status:response.status});
 } catch {return NextResponse.json({code:"API_UNAVAILABLE"},{status:503});}
}
