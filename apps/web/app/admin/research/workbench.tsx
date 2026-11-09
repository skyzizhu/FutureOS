"use client";
import {useEffect,useRef,useState} from "react";
import type {ResearchRunViewV1,ResearchSubmitV1,ResearchAcceptedV1} from "@futureos/contracts";
export default function ResearchConsole() {
 const[json,setJson]=useState("");const[view,setView]=useState<ResearchRunViewV1|null>(null);
 const[runs,setRuns]=useState<ResearchRunViewV1[]>([]);const[busy,setBusy]=useState(false);
 const[error,setError]=useState("");const[notice,setNotice]=useState("");
 const[enabled,setEnabled]=useState(false);const[provider,setProvider]=useState("mock");
 const pending=useRef<{key:string;body:string}|null>(null);
 const abort=useRef<AbortController|null>(null);
 useEffect(()=>{fetch("/api/admin/research/config").then(r=>r.json()).then(d=>setEnabled(d.live_research_enabled===true)).catch(()=>{});fetch("/api/admin/research/runs").then(r=>r.ok?r.json():[]).then(setRuns).catch(()=>{});return()=>abort.current?.abort();},[]);
 async function api(path:string,body?:unknown,key?:string) {
  const response=await fetch(`/api/admin/research/${path}`,{method:body?"POST":"GET",headers:{"Content-Type":"application/json",...(key?{"Idempotency-Key":key}:{})},body:body?JSON.stringify(body):undefined,signal:abort.current?.signal});
  const data=await response.json();if(!response.ok)throw new Error(`${data.code||"ERROR"}：${data.message||"请求失败"}`);return data;
 }
 async function action(operation:()=>Promise<void>){setBusy(true);setError("");setNotice("");abort.current=new AbortController();try{await operation();}catch(e){if(!(e instanceof DOMException&&e.name==="AbortError"))setError(e instanceof Error?e.message:"请求失败");}finally{setBusy(false);}}
 async function submit(){await action(async()=>{
  const request:ResearchSubmitV1={...JSON.parse(json),provider};
  const body=JSON.stringify(request);if(!pending.current||pending.current.body!==body)pending.current={key:crypto.randomUUID(),body};
  const accepted:ResearchAcceptedV1=await api("submit",request,pending.current.key);
  for(let i=0;i<150;i++){
   const state:ResearchRunViewV1=await api(`runs/${accepted.run_id}`);setView(state);
   if(["succeeded","failed_terminal","cancelled"].includes(state.status)){pending.current=null;setRuns(await api("runs"));if(state.error_code)throw new Error(state.error_code);return;}
   await new Promise(resolve=>setTimeout(resolve,1000));
  }
  throw new Error("仍在处理，可使用相同输入重试恢复查询；不会自动重发付费调用。");
 });}
 const draft=view?.draft;
 return <><section><h2>准备研究输入</h2><p>Mock 使用自编 DEMO 资料，验证互补信号、反证、跨领域正反案例和三期指标。也可编辑信号/案例 ID，研究已核实的库内资料。</p>
 <button disabled={busy} onClick={()=>action(async()=>{const data=await api("demo-inputs",{});setJson(JSON.stringify(data,null,2));setProvider("mock");setNotice("DEMO 输入已准备，不涉及真实研究或付费请求。");})}>准备 DEMO 研究</button>
 <label htmlFor="research-json">研究输入 JSON</label><textarea id="research-json" className="json-input" value={json} onChange={e=>setJson(e.target.value)} spellCheck={false}/>
 <label htmlFor="research-provider">生成方式</label><select id="research-provider" value={provider} onChange={e=>setProvider(e.target.value)}><option value="mock">Mock（确定性 DEMO）</option><option value="deepseek" disabled={!enabled}>DeepSeek（真实模型调用，需服务端开关）</option></select>
 <p>{provider==="mock"?"Mock 不调用外部模型。":"每次研究最多一次付费模型调用，不自动重试；不会自动搜索或补造来源。"}</p>
 <button disabled={busy||!json} onClick={submit}>{busy?"正在处理…":"创建内部草稿"}</button></section>
 <div aria-live="polite">{error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}</div>
 {view&&<section><h2>运行状态</h2><p>{view.status} · {view.label} · {view.model_id}</p><small>输入 hash：{view.input_hash}</small></section>}
 {draft&&<><section><span className="badge">{draft.label} / {draft.kind} / 草稿 A</span><h2>内部原始草稿 A</h2><p><strong>未审查 · 禁止正式发布</strong></p><h3>{draft.statement}</h3><p>研究截止：{draft.research_as_of} · 阶段：{draft.lifecycle_stage}</p>
 {draft.downgrade_reasons.length>0&&<p>保留为假设的原因：{draft.downgrade_reasons.join(" / ")}</p>}
 {draft.target&&<article><h3>待验证目标</h3><p>{draft.target.metric_definition} · {draft.target.direction_or_threshold}</p><p>范围：{draft.target.population_scope} / {draft.target.geography}</p><p>期限：{draft.target.target_end_at}</p><p>验证：{draft.target.resolution_rule}</p></article>}
 <h3>朴素统计基线</h3><p>{draft.baseline.method} · 样本 {draft.baseline.sample_count} · 对照值 {draft.baseline.projected_value??"不适用"}</p><p>{draft.baseline.limitations.join("；")}</p></section>
 <section><h2>信号融合与机制链</h2>{!draft.fusions.length&&<p>未发现满足独立来源和互补条件的组合。</p>}{draft.fusions.map(f=><article key={f.fusion_id}><h3>{f.mechanism}</h3><p>独立来源簇：{f.independent_source_groups}</p><p>瓶颈：{f.remaining_bottlenecks.join("；")}</p><p>后续观察：{f.next_observable_signals.join("；")}</p></article>)}
 {draft.mechanism_chain.map((edge,i)=><p key={i}>{edge.from_node} → {edge.to_node}（{edge.sign}）<br/><small>{edge.uncertainty}</small></p>)}</section>
 <section><h2>竞争情景与反证</h2>{draft.scenarios.map(s=><article key={s.scenario_id}><h3>{s.path==="base"?"基准路径":s.path==="acceleration"?"加速路径":"受阻路径"}</h3><p>{s.statement}</p><p>条件：{s.conditions.join("；")}</p><p>推翻条件：{s.falsification_conditions.join("；")}</p></article>)}<p>反证主张数量：{draft.contradiction_claim_ids.length}</p></section>
 <section><h2>跨领域历史类比</h2>{draft.analogies.map(a=><article key={a.case_id}><p>机制重合：{a.mechanism_overlap.join(" / ")}</p><p>相似：{a.similarities.join("；")}</p><p>差异：{a.key_differences.join("；")}</p><p>不可迁移：{a.non_transferable.join("；")}</p><p>当时可见结果：{a.known_outcomes.map(o=>o.outcome_category).join(" / ")||"尚未知晓"}</p><p>{a.limitations.join("；")}</p></article>)}</section>
 <section><h2>冻结与重放</h2><p>{draft.limitations.join("；")}</p><small>草稿 hash：{view?.draft_hash}</small><p><button disabled={busy} onClick={()=>action(async()=>{const result=await api(`runs/${draft.run_id}/replay`,{});setNotice(result.identical?"重放一致：草稿 hash 相同，联网调用 0 次。":"重放不一致，请检查冻结输入和代码版本。");})}>离线重放草稿</button></p><details><summary>查看完整结构化草稿</summary><pre>{JSON.stringify(draft,null,2)}</pre></details></section></>}
 <section><h2>历史内部研究</h2>{runs.map(run=><p key={run.run_id}><button disabled={busy} onClick={()=>action(async()=>{setView(await api(`runs/${run.run_id}`));})}>{run.title} · {run.status} · {run.label}</button></p>)}</section></>;
}
