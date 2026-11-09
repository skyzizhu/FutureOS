import {cookies} from "next/headers";
import {backend,demoOnly} from "../../api/backend";
import EvidenceConsole from "./workbench";
export const dynamic="force-dynamic";
export default async function Sources() {
 let authorized=false;
 try {
  demoOnly();const token=(await cookies()).get("futureos_admin")?.value;
  if(token) {
   const response=await fetch(`${backend}/api/v1/me`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});
   authorized=response.ok && (await response.json()).role==="admin";
  }
 } catch { /* Workbench shows login instead of privileged data when API is unavailable. */ }
 return <><p className="eyebrow">M1 · 证据与信号基础</p><h1>来源工作台</h1>
 <p>只有核实过来源、时间和适用范围，资料才能成为信号。此处不生成预测。</p>
 <EvidenceConsole authorized={authorized}/></>;
}
