"use client";
import {TextArea,Select,Button} from "../components/ui/controls";

import Link from "next/link";
import {useState} from "react";
import type {ResearchIntakeResultV1} from "@futureos/contracts";
import {accountApi} from "../components/account-api";
export default function Intake(){const[question,setQuestion]=useState("");const[mode,setMode]=useState("DEMO");const[result,setResult]=useState<ResearchIntakeResultV1|null>(null);const[error,setError]=useState("");const[busy,setBusy]=useState(false);return <section><h2>可选：希望观察什么变化？</h2><label htmlFor="intake-question">问题或目标（选填）</label><TextArea id="intake-question" maxLength={500} value={question} onChange={e=>setQuestion(e.target.value)}/><label htmlFor="intake-label">资料范围</label><Select id="intake-label" value={mode} onValueChange={e=>setMode(e)}><option value="DEMO">合成演示</option><option value="REAL">真实已审查版本</option></Select><Button disabled={busy} onClick={async()=>{setBusy(true);setError("");try{setResult(await accountApi("research/intake","POST",{question,label:mode}));}catch(e){setError(e instanceof Error?e.message:"范围确认失败");}finally{setBusy(false);}}}>确认范围，不扣额度</Button>{error&&<p role="alert">{error}</p>}{result&&<article><h3>{result.scope}</h3><p>可用首次报告：{result.available_free_reports} · 当前匹配版本：{result.matched_version_ids.length}</p><p>{result.additional_questions.join("；")}</p><p>{result.limitations.join("；")}</p><Link href="/dashboard">回到首页确认并生成报告</Link></article>}</section>;}
