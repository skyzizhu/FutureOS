"use client";
import {TextArea,Button} from "../components/ui/controls";

import {useEffect, useRef, useState} from "react";
import type {JobAcceptedV1, JobV1} from "@futureos/contracts";
export default function DemoConsole() {
 const [question,setQuestion] = useState("工具可靠性提高可能如何影响软件开发任务？");
 const [job,setJob] = useState<JobV1|null>(null);
 const [error,setError] = useState("");
 const [busy,setBusy] = useState(false);
 const pending = useRef<{key:string; question:string}|null>(null);
 const controller = useRef<AbortController|null>(null);
 useEffect(()=>()=>controller.current?.abort(),[]);
 async function run() {
  setBusy(true); setError(""); setJob(null);
  if (!pending.current || pending.current.question !== question) pending.current = {key:crypto.randomUUID(),question};
  controller.current = new AbortController();
  try {
   const response = await fetch("/api/demo/research",{method:"POST",headers:{"Content-Type":"application/json","Idempotency-Key":pending.current.key},body:JSON.stringify({question}),signal:controller.current.signal});
   if(!response.ok) throw new Error("提交失败，请检查 API 连接后重试。");
   const accepted:JobAcceptedV1 = await response.json();
   for(let n=0;n<60;n++) {
    const status = await fetch(`/api/jobs/${accepted.job_id}`,{signal:controller.current.signal});
    if(!status.ok) throw new Error("无法获取任务状态。");
    const data:JobV1 = await status.json(); setJob(data);
    if(["succeeded","failed_terminal","cancelled"].includes(data.status)) {pending.current=null; return;}
    await new Promise(resolve=>setTimeout(resolve,1000));
   }
   throw new Error("任务仍在处理中。请保留页面，使用同一内容重试可恢复查询。");
  } catch(e) {if(!(e instanceof DOMException && e.name === "AbortError")) setError(e instanceof Error?e.message:"请求失败");}
  finally {setBusy(false);}
 }
 return <><label htmlFor="question">演示研究问题</label><TextArea id="question" value={question} onChange={e=>setQuestion(e.target.value)} minLength={3} maxLength={500} />
 <Button onClick={run} disabled={busy || question.length<3}>{busy?"任务处理中…":"运行 DEMO 任务"}</Button>
 <div aria-live="polite">{error&&<p role="alert">{error}</p>}{job&&<><p>任务状态：<strong>{job.status}</strong> · 尝试 {job.attempts} 次</p>
 {job.result&&"statement" in job.result&&<article><span className="badge">{job.result.label} / {job.result.kind}</span><h3>{job.result.statement}</h3><p>{job.result.limitations.join("；")}</p><small>研究截止：{job.result.research_as_of}</small></article>}
 {job.error_code&&<p role="alert">任务失败：{job.error_code}</p>}</>}</div></>;
}
