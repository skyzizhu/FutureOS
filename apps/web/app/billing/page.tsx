import Protected from "../components/protected";
import Billing from "./workbench";
export const dynamic="force-dynamic";
export default async function Page({searchParams}:{searchParams:Promise<{checkout?:string}>}){const{checkout}=await searchParams;return <Protected><div className="billing-page"><p className="eyebrow">套餐体验 · 模拟流程</p><h1>套餐与账单</h1><p>下面的金额只用于模拟流程，未确定正式定价，不会真实扣款。套餐研究额度与首次免费报告分开记录；原主题重要更新继续免费。</p><Billing initialCheckout={checkout}/></div></Protected>;}
