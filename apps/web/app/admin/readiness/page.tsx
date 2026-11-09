import {cookies} from "next/headers";
import {backend} from "../../api/backend";
import EvidenceConsole from "../sources/workbench";
import Readiness from "./workbench";
export const dynamic="force-dynamic";
export default async function Page(){let authorized=false;try{const token=(await cookies()).get("futureos_admin")?.value;if(token){const response=await fetch(`${backend}/api/v1/me`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});authorized=response.ok&&(await response.json()).role==="admin";}}catch{/* Privileged snapshot stays behind admin authentication. */}return <><h1>质量与上线就绪</h1><p>本地工程检查与真实服务上线审批分开记录。未到期样本不计为预测成功。</p>{authorized?<Readiness/>:<EvidenceConsole authorized={false}/>}</>;}
