import {cookies} from "next/headers";
import Link from "next/link";
import {backend} from "../api/backend";
export default async function Protected({children}:{children:React.ReactNode}){
 let authorized=false;
 try{const token=(await cookies()).get("futureos_session")?.value;if(token){const response=await fetch(`${backend}/api/v1/auth/identity`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(5000)});authorized=response.ok;}}catch{/* Keep private content behind a validated account session. */}
 if(!authorized)return <section><h1>请先登录</h1><p>画像与报告仅对当前账号可见。</p><Link href="/auth/login">登录或注册</Link></section>;
 return <>{children}</>;
}
