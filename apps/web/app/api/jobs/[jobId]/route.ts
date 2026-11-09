import {NextResponse} from "next/server";
import {backend,demoToken,demoOnly} from "../../backend";
export async function GET(_:Request,{params}:{params:Promise<{jobId:string}>}) {
 try {
  demoOnly(); const {jobId} = await params;
  if(!/^[a-f0-9-]{36}$/i.test(jobId)) return NextResponse.json({code:"VALIDATION_ERROR"},{status:422});
  const response = await fetch(`${backend}/api/v1/jobs/${jobId}`,{headers:{Authorization:`Bearer ${demoToken}`},cache:"no-store",signal:AbortSignal.timeout(5000)});
  return NextResponse.json(await response.json(),{status:response.status});
 } catch {return NextResponse.json({code:"API_UNAVAILABLE"},{status:503});}
}
