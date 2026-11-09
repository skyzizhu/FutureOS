import {NextResponse} from "next/server";
import {backend} from "../backend";
export async function GET(){try{const r=await fetch(`${backend}/api/v1/auth/config`,{cache:"no-store",signal:AbortSignal.timeout(5000)});return NextResponse.json(await r.json(),{status:r.status,headers:{"Cache-Control":"no-store"}});}catch{return NextResponse.json({code:"AUTH_UNAVAILABLE"},{status:503,headers:{"Cache-Control":"no-store"}});}}
