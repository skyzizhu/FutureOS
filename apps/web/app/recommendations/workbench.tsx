"use client";
import {Button} from "../components/ui/controls";

import Link from "next/link";
import {useEffect,useState} from "react";
import type {RecommendationV1} from "@futureos/contracts";
import {accountApi} from "../components/account-api";
type Item={recommendation:RecommendationV1;feedback:string|null};
export default function Recommendations(){const[items,setItems]=useState<Item[]>([]);const[error,setError]=useState("");const[notice,setNotice]=useState("");async function reload(){setItems(await accountApi("recommendations"));}useEffect(()=>{reload().catch(e=>setError(e.message));},[]);return <section><h2>我的可选建议</h2>{error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}{items.length?items.map(({recommendation:r,feedback})=><article key={r.recommendation_id}>{feedback==="hide"?<p>这条建议已隐藏；反馈仍保留。</p>:<><p className="badge">{r.priority}</p><h3>{r.action}</h3><p>{r.rationale}</p><p>成本：{r.estimated_effort_and_cost}</p><p>停止条件：{r.stop_or_revisit_condition}</p><p>替代：{r.alternatives.join("；")}</p><p>当前反馈：{feedback||"未反馈"}</p></>}{([['helpful','有帮助'],['not_applicable','不适用'],['taken','已采取'],['hide','不想看到']] as const).map(([status,label])=><Button key={status} onClick={async()=>{try{await accountApi(`recommendations/${r.recommendation_id}/feedback`,"POST",{status});await reload();setNotice("反馈已保存，不改变原报告内容。");}catch(e){setError(e instanceof Error?e.message:"反馈失败");}}}>{label}</Button>)}</article>):<p>还没有建议。<Link href="/dashboard">先生成首份报告</Link>。</p>}</section>;}
