import {cookies} from "next/headers";
import {backend} from "../../api/backend";
import EvidenceConsole from "../sources/workbench";
import Costs from "./workbench";
export const dynamic="force-dynamic";
export default async function Page(){let authorized=false;try{const token=(await cookies()).get("futureos_admin")?.value;if(token){const response=await fetch(`${backend}/api/v1/me`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});authorized=response.ok&&(await response.json()).role==="admin";}}catch{/* Keep cost records behind admin authentication. */}return <><h1>研究复用与成本观测</h1>{authorized?<Costs/>:<EvidenceConsole authorized={false}/>}</>;}
