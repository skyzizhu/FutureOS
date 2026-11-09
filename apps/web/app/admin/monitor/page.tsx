import {cookies} from "next/headers";
import {backend} from "../../api/backend";
import EvidenceConsole from "../sources/workbench";
import MonitorConsole from "./workbench";
export const dynamic="force-dynamic";
export default async function Page(){let authorized=false;try{const token=(await cookies()).get("futureos_admin")?.value;if(token){const response=await fetch(`${backend}/api/v1/me`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});authorized=response.ok&&(await response.json()).role==="admin";}}catch{/* API authorization keeps privileged controls private. */}return <><p className="eyebrow">M5 · 原主题持续复查</p><h1>拐点监控</h1><p>T0 归档、T1 观察、T2 定向复查、T3 关键条件复核。新版本须经过独立审查；旧版及验证窗口保留。</p>{authorized?<MonitorConsole/>:<EvidenceConsole authorized={false}/>}</>;}
