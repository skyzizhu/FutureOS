import {cookies} from "next/headers";
import {backend,demoOnly} from "../../api/backend";
import EvidenceConsole from "../sources/workbench";
import ReviewConsole from "./workbench";
export const dynamic="force-dynamic";
export default async function Research() {
 let authorized=false;
 try {
  demoOnly();const token=(await cookies()).get("futureos_admin")?.value;
  if(token){const response=await fetch(`${backend}/api/v1/me`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});authorized=response.ok&&(await response.json()).role==="admin";}
 }catch{/* Privileged records stay behind API ownership/role checks. */}
 return <><p className="eyebrow">M3 · 审查与评估</p><h1>独立审查与发布</h1><p>保留原始草稿 A，独立检查证据、类比、因果、情景和时间。实质错误阻断发布，最多进行两轮定向复核。</p>{authorized?<ReviewConsole/>:<EvidenceConsole authorized={false}/>}</>;
}
