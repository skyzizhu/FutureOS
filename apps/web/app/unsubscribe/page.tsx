import Unsubscribe from "./workbench";
export const dynamic="force-dynamic";
export default async function Page({searchParams}:{searchParams:Promise<{token?:string}>}){const{token}=await searchParams;return <><h1>退订报告邮件</h1><p>退订后将关闭全部邮件提醒。原主题复查和站内报告更新继续运行。</p><Unsubscribe token={token||""}/></>;}
