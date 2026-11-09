import {cookies} from "next/headers";
import {backend,demoOnly} from "../../api/backend";
import EvidenceConsole from "../sources/workbench";
import ResearchConsole from "./workbench";
export const dynamic="force-dynamic";
export default async function Research() {
 let authorized=false;
 try {
  demoOnly();const token=(await cookies()).get("futureos_admin")?.value;
  if(token){const response=await fetch(`${backend}/api/v1/me`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});authorized=response.ok&&(await response.json()).role==="admin";}
 }catch{/* Privileged records stay behind API ownership/role checks. */}
 return <><p className="eyebrow">M2 · 内部研究</p><h1>研究草稿工作台</h1><p>从固定版本的证据出发，形成可反驳、可检验的草稿。所有结果尚未经过 Critic，不能正式发布。</p>{authorized?<ResearchConsole/>:<EvidenceConsole authorized={false}/>}</>;
}
