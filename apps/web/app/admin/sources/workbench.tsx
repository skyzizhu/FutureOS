"use client";
import {useEffect,useState} from "react";
import {useRouter} from "next/navigation";
import type {SourceImportV1,SourceVersionV1,SignalV1,SearchHitV1,WebFetchPreviewV1} from "@futureos/contracts";

const demo:SourceImportV1={url:"https://example.invalid/m1-browser-fixture",title:"DEMO 合成资料",publisher:"FutureOS Fixture",source_type:"manual",published_at:"2020-08-10T00:00:00Z",available_at:"2020-08-10T00:00:00Z",availability_basis:"verified_archive",availability_note:"DEMO fixture archived snapshot",content:"DEMO：工具可靠性提高，招聘岗位变化仍需继续观察。",usage_permission:"authorized_full",license_note:"Synthetic fixture created for FutureOS demo",reliability_note:"DEMO only, not real evidence",domain_tags:["technology","workforce"],label:"DEMO",claims:[{claim_text:"DEMO：工具可靠性提高，招聘岗位变化仍需继续观察。",quote:"DEMO：工具可靠性提高，招聘岗位变化仍需继续观察。",source_locator:"paragraph 1",relation:"context",claim_kind:"fact",verification_status:"verified",verification_note:"Checked against synthetic fixture",scope:"DEMO region"}]};

export default function EvidenceConsole({authorized}:{authorized:boolean}) {
 const router=useRouter();const[token,setToken]=useState("");
 const[demoAllowed,setDemoAllowed]=useState(false);
 useEffect(()=>{fetch("/api/auth-config").then(r=>r.json()).then(c=>setDemoAllowed(c.demo_admin_enabled===true)).catch(()=>setDemoAllowed(false));},[]);
 const[error,setError]=useState("");const[notice,setNotice]=useState("");const[busy,setBusy]=useState(false);
 const[json,setJson]=useState(JSON.stringify(demo,null,2));const[asOf,setAsOf]=useState("");
 const[sources,setSources]=useState<SourceVersionV1[]>([]);const[signals,setSignals]=useState<SignalV1[]>([]);
 const[query,setQuery]=useState("");const[hits,setHits]=useState<SearchHitV1[]>([]);
 const[preview,setPreview]=useState<WebFetchPreviewV1|null>(null);
 async function api(path:string,body?:unknown) {
  const response=await fetch(`/api/admin/${path}`,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined});
  const data=await response.json();if(!response.ok) throw new Error(`${data.code || "ERROR"}：${data.message || "请求失败"}`);return data;
 }
 async function reload() {
  const params=asOf?`?as_of=${encodeURIComponent(asOf)}`:"";
  const [s,g]=await Promise.all([api(`sources${params}`),api(`signals${params}`)]);
  setSources(s);setSignals(g);
 }
 useEffect(()=>{if(authorized){Promise.all([fetch("/api/admin/sources"),fetch("/api/admin/signals")]).then(async([a,b])=>{if(a.ok&&b.ok){setSources(await a.json());setSignals(await b.json());}}).catch(()=>setError("无法加载资料"));}},[authorized]);
 async function action(operation:()=>Promise<void>) {
  setBusy(true);setError("");setNotice("");try{await operation();}catch(e){setError(e instanceof Error?e.message:"请求失败");}finally{setBusy(false);}
 }
 if(!authorized) return <section><h2>管理员登录</h2><p><a href="/admin/login">使用管理员账号与双重认证登录</a></p>{demoAllowed&&<><p>本地演示认证已显式开启，仅用于自动化验收。</p>
 <form onSubmit={e=>{e.preventDefault();action(async()=>{const response=await fetch("/api/admin/session",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token})});if(!response.ok)throw new Error("管理员身份验证失败");setToken("");router.refresh();});}}>
 <label htmlFor="admin-token">管理员令牌</label><input id="admin-token" type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)}/><button disabled={busy}>进入工作台</button></form></>}{error&&<p role="alert">{error}</p>}</section>;
 return <><div className="toolbar"><span className="badge">ADMIN · M1</span><button onClick={()=>action(async()=>{await fetch("/api/admin/session",{method:"DELETE"});router.refresh();})}>退出</button></div>
 <div aria-live="polite">{error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}</div>
 <section><h2>DeepSeek 搜索与抓取</h2><p>手动调用真实接口，按供应商规则计费。搜索结果和正文预览均未核实；不会自动成为证据。</p>
 <label htmlFor="search-query">搜索词（最多 128 字符）</label><input id="search-query" maxLength={128} value={query} onChange={e=>setQuery(e.target.value)}/>
 <button disabled={busy||!query.trim()} onClick={()=>action(async()=>{const data=await api("sources/search",{query,count:3});setHits(data.results);setPreview(null);if(!data.results.length)setNotice("搜索完成，无匹配结果。");})}>搜索网页</button>
 {hits.map(hit=><article key={hit.hit_id}><h3>{hit.title}</h3><a href={hit.url} target="_blank" rel="noreferrer">{hit.url}</a><p>{hit.snippet}</p><p>发布时间：{hit.published_at||"未知"} · 待核实</p><button disabled={busy} onClick={()=>action(async()=>{setPreview(await api("sources/fetch",{url:hit.url}));})}>抓取正文预览</button></article>)}
 {preview&&<article><h3>{preview.title||"正文预览"}</h3><p>最多 2000 字符；发布时间未知。先确认许可和引用范围，再导入。</p><pre>{preview.excerpt}</pre><button onClick={()=>{setJson(JSON.stringify({url:preview.url,title:preview.title||"待核实来源",publisher:"待核实",source_type:"manual",availability_basis:"observed_now",usage_permission:"metadata_only",license_note:"仅保留链接和元数据；未授权保留正文",access_method:"deepseek",reliability_note:"待核实；不作为正式证据",domain_tags:["technology"],label:"REAL",claims:[]},null,2));setNotice("已生成仅含元数据的导入草稿，请核对后提交。");}}>准备来源元数据</button></article>}
 </section>
 <section><h2>导入来源与证据</h2><p>默认示例是自编 DEMO 资料。真实资料需填写许可、时间依据、引用定位和人工核实说明。未知时间不能补造。</p>
 <label htmlFor="source-json">来源 JSON</label><textarea id="source-json" className="json-input" value={json} onChange={e=>setJson(e.target.value)} spellCheck={false}/>
 <button disabled={busy} onClick={()=>action(async()=>{const result=await api("sources/ingest",JSON.parse(json));await reload();setNotice(result.duplicate?"已存在相同版本，复用成功。":"来源已导入；符合条件的事实已生成信号候选。");})}>导入来源</button>
 <label htmlFor="json-file" className="file-label">或读取 JSON 文件</label><input id="json-file" type="file" accept=".json,application/json" onChange={e=>{const file=e.target.files?.[0];if(file){if(file.size>150000){setError("文件不能超过 150 KB");return;}file.text().then(setJson);}}}/></section>
 <section><h2>按时间查看</h2><label htmlFor="as-of">研究截止时间（带时区的 ISO 时间，可留空）</label><input id="as-of" placeholder="2020-08-20T00:00:00Z" value={asOf} onChange={e=>setAsOf(e.target.value)}/><button disabled={busy} onClick={()=>action(reload)}>刷新时间视图</button>
 <h3>来源版本 · {sources.length}</h3>{!sources.length&&<p>此时间视图没有可获取的来源版本。</p>}
 {sources.map(source=><article key={source.source_version_id}><span className="badge">{source.label}</span><h3>{source.title}</h3><p>版本：{source.version_label}</p><p>公开：{source.published_at||"未知"}<br/>可获取：{source.available_at||"未知"}<br/>采集：{source.ingested_at}</p><p>依据：{source.availability_basis} · {source.availability_note||"未提供"}</p><p>许可：{source.usage_permission} · {source.license_note}</p><small>来源簇：{source.source_group_id}</small></article>)}
 <h3>信号候选 · {signals.length}</h3>{!signals.length&&<p>尚无符合条件的信号。</p>}{signals.map(signal=><article key={signal.signal_id}><span className="badge">{signal.label} / signal / candidate</span><h3>{signal.headline}</h3><p>独立来源簇：{signal.independent_source_count} · 阶段：{signal.lifecycle_stage}</p><p>领域：{signal.domain_tags.join(" / ")}</p></article>)}</section></>;
}
