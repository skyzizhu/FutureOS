"use client";
import {Button,TextInput} from "../../components/ui/controls";

import {useEffect,useRef,useState} from "react";
import type {AuthConfigurationV1,EmailCodeSentV1} from "@futureos/contracts";
import {safeReturnPath} from "../../components/consumer/api";
import PasswordInput from "../../components/password-input";
import {useHumanCheck} from "../../components/human-check";
import {AuthFailure,authRequest,failureMessage,withHumanCheck} from "../../components/auth-request";
type Mode="register"|"login"|"reset";
type Field="email"|"code"|"password";
type Proof={id:string;email:string;mode:Mode;expiresAt:number};
const validEmail=(value:string)=>value.length<=254&&/^[A-Za-z0-9.!#$%&*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(value);
export default function AuthForm(){
 const[mode,setMode]=useState<Mode>("register");const[email,setEmail]=useState("");const[password,setPassword]=useState("");const[code,setCode]=useState("");const[proof,setProof]=useState<Proof|null>(null);
 const[config,setConfig]=useState<AuthConfigurationV1|null>(null);const[configError,setConfigError]=useState(false);const[busy,setBusy]=useState(false);const[error,setError]=useState("");const[fields,setFields]=useState<Partial<Record<Field,string>>>({});const[notice,setNotice]=useState("");const[now,setNow]=useState(()=>Date.now());
 const emailInput=useRef<HTMLInputElement>(null);const passwordInput=useRef<HTMLInputElement>(null);const codeInput=useRef<HTMLInputElement>(null);const sendButton=useRef<HTMLButtonElement>(null);const busyLock=useRef(false);const cooldowns=useRef(new Map<string,number>());const loginLimits=useRef(new Map<string,number>());
 const {getToken,challenge,checking}=useHumanCheck(config?.turnstile_site_key||"",config?.turnstile_enabled===true);
 const normalized=email.trim().toLowerCase();const scope=`${mode}:${normalized}`;const wait=Math.max(0,Math.ceil(((cooldowns.current.get(scope)||0)-now)/1000));const loginWait=Math.max(0,Math.ceil(((loginLimits.current.get(scope)||0)-now)/1000));
 const activeProof=proof?.email===normalized&&proof.mode===mode?proof:null;const expired=Boolean(activeProof&&activeProof.expiresAt<=now);const codeSeconds=activeProof?Math.max(0,Math.ceil((activeProof.expiresAt-now)/1000)):0;
 async function loadConfig(){setConfigError(false);try{const r=await fetch("/api/auth-config",{cache:"no-store"});if(!r.ok)throw new Error();const data=await r.json();if(typeof data.turnstile_enabled!=="boolean"||typeof data.turnstile_site_key!=="string"||(data.turnstile_enabled&&!data.turnstile_site_key))throw new Error();setConfig(data);}catch{setConfig(null);setConfigError(true);}}
 useEffect(()=>{const initialMode=new URLSearchParams(window.location.search).get("mode");if(initialMode==="reset"||initialMode==="login")setMode(initialMode);void loadConfig();},[]);
 useEffect(()=>{const timer=setInterval(()=>setNow(Date.now()),1000);return()=>clearInterval(timer);},[]);
 function showError(message:string,field?:Field){setError(message);if(field){setFields({[field]:message});requestAnimationFrame(()=>{const target=field==="email"?emailInput.current:field==="password"?passwordInput.current:activeProof&&!expired?codeInput.current:sendButton.current;target?.focus();target?.scrollIntoView({block:"nearest",behavior:"smooth"});});}}
 function clearField(field:Field){setFields(current=>({...current,[field]:undefined}));setError("");}
 function switchTo(next:Mode){if(busyLock.current)return;setMode(next);setCode("");setProof(null);setPassword("");setFields({});setError("");setNotice("");setNow(Date.now());}
 function validateEmail(){if(!normalized){showError("请填写邮箱地址。","email");return false;}if(!validEmail(normalized)){showError("请填写完整、有效的邮箱地址，例如 name@126.com。","email");return false;}return true;}
 async function sendCode(){
  if(busyLock.current)return;setError("");setNotice("");if(!validateEmail())return;if(!config){showError("认证服务尚未就绪，请稍后重试。");return;}if(wait>0)return;
  busyLock.current=true;setBusy(true);setFields({});const address=normalized;const requestMode=mode;
  try{const human=await getToken(mode==="register"?"signup":"password_reset");const data=await authRequest<EmailCodeSentV1>("/api/account/auth",{action:"email-code",email:address,purpose:requestMode==="register"?"register":"password_reset",human_token:human});const time=Date.now();setProof({id:data.challenge_id,email:address,mode:requestMode,expiresAt:time+(data.expires_in??300)*1000});setCode("");cooldowns.current.set(scope,time+(data.resend_after??60)*1000);setNow(time);setNotice(data.delivery_mode==="local_preview"?"验证码已生成到本地预览，尚未真实发信。":`已请求发送验证码，请查看 ${address} 的收件箱或垃圾邮件。`);requestAnimationFrame(()=>codeInput.current?.focus());}
  catch(e){if(e instanceof AuthFailure&&e.retryAfter){cooldowns.current.set(scope,Date.now()+e.retryAfter*1000);setNow(Date.now());}showError(failureMessage(e));}
  finally{busyLock.current=false;setBusy(false);}
 }
 async function submit(event:React.FormEvent){
  event.preventDefault();if(busyLock.current)return;setError("");setNotice("");setFields({});if(!validateEmail())return;
  if(mode!=="login"){
   if(!activeProof){showError("请先点击“发送邮箱验证码”，收到邮件后再填写。","code");return;}
   if(expired){showError("邮箱验证码已过期，请重新发送。","code");return;}
   if(!/^\d{4}$/.test(code)){showError("请填写邮件中的4位数字验证码。","code");return;}
  }
  if(password.length<12||password.length>128){showError("密码需要12–128个字符。","password");return;}
  if(!config){showError("认证服务尚未就绪，请稍后重试。");return;}if(loginWait>0)return;
  busyLock.current=true;setBusy(true);const address=normalized;const requestMode=mode;const credential=password;
  try{if(mode==="login"){await withHumanCheck(human=>authRequest("/api/account/auth",{action:"login",email:address,password:credential,human_token:human}),getToken,"login");}else{await authRequest("/api/account/auth",{action:mode==="reset"?"password-reset":"register",email:address,password:credential,verification_id:activeProof?.id,code});}
   setPassword("");if(requestMode==="reset"){setMode("login");setCode("");setProof(null);setNotice("密码已修改，所有旧会话已失效，请重新登录。");}else {const next=new URLSearchParams(window.location.search).get("next")||"";const safe=safeReturnPath(next,"");window.location.assign(requestMode==="register"?`/onboarding${safe?`?next=${encodeURIComponent(safe)}`:""}`:safe||"/dashboard");}
  }catch(e){if(e instanceof AuthFailure&&e.retryAfter){loginLimits.current.set(scope,Date.now()+e.retryAfter*1000);setNow(Date.now());}showError(failureMessage(e),e instanceof AuthFailure&&e.code==="EMAIL_CODE_INVALID"?"code":undefined);}
  finally{busyLock.current=false;setBusy(false);}
 }
 const step=!activeProof?0:code.length!==4?1:2;
 return <section className="auth-card" aria-busy={busy&&!checking}><h2>{mode==="register"?"创建账号":mode==="reset"?"忘记或修改密码":"欢迎回来"}</h2><p className="auth-intro">{mode==="register"?"先验证邮箱，再设置密码。你的个人报告仅自己可见。":mode==="reset"?"验证邮箱归属后设置新密码，旧登录会话会同时失效。":"使用已注册的邮箱和密码登录。"}</p>
 {mode!=="login"&&<ol className="auth-steps" aria-label="注册与验证步骤">{["填写邮箱","验证邮箱","设置密码"].map((label,index)=><li key={label} aria-current={index===step?"step":undefined} className={index<=step?"is-current":""}><span aria-hidden="true">{index+1}</span>{label}</li>)}</ol>}
 {config?.email_transport==="local_preview"&&<p className="badge">本地邮件预览 · 尚未真实发信</p>}
 {configError&&<div className="auth-feedback auth-error" role="alert">认证服务连接失败。<Button type="button" className="auth-text-button" onClick={()=>void loadConfig()}>重新连接</Button></div>}
 {error&&<p className="auth-feedback auth-error" role="alert">{error}</p>}{notice&&<p className="auth-feedback auth-success" role="status">{notice}</p>}
 <form onSubmit={submit} noValidate>
  <div className="auth-field"><label htmlFor="account-email">邮箱</label><div className={mode!=="login"?"auth-email-row":""}><TextInput ref={emailInput} id="account-email" type="email" autoComplete="username" required maxLength={254} disabled={busy} aria-invalid={Boolean(fields.email)} aria-describedby={fields.email?"email-error":undefined} value={email} onChange={e=>{setEmail(e.target.value);clearField("email");if(proof){setProof(null);setCode("");setNotice("邮箱已更换，请重新发送验证码。");}setNow(Date.now());}}/>{mode!=="login"&&<Button ref={sendButton} type="button" className="auth-send" disabled={busy||wait>0||!config} onClick={()=>void sendCode()}>{checking?"安全检查中…":busy?"处理中…":wait>0?`${wait}秒后可重发`:activeProof?"重新发送验证码":"发送邮箱验证码"}</Button>}</div>{fields.email&&<p id="email-error" className="auth-field-error">{fields.email}</p>}</div>
  {mode!=="login"&&<div className="auth-field"><div className="auth-label-row"><label htmlFor="email-code">邮箱验证码</label>{activeProof&&!expired&&<small aria-live="off">剩余 {Math.floor(codeSeconds/60)}:{String(codeSeconds%60).padStart(2,"0")}</small>}</div><TextInput ref={codeInput} id="email-code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{4}" minLength={4} maxLength={4} required disabled={busy||!activeProof||expired} aria-invalid={Boolean(fields.code)} aria-describedby={fields.code?"code-error":"code-help"} value={code} placeholder={activeProof?"填写收到的4位数字":"请先发送邮箱验证码"} onChange={e=>{setCode(e.target.value.replace(/\D/g,""));clearField("code");}}/>{fields.code?<p id="code-error" className="auth-field-error">{fields.code}</p>:<p id="code-help" className="auth-hint">{expired?"验证码已过期，请重新发送。":activeProof?"验证码5分钟内有效。没有收到？请先检查垃圾邮件。":"点击上方发送按钮，收到邮件后填写验证码。"}</p>}</div>}
  <div className="auth-field"><label htmlFor="account-password">{mode==="reset"?"新密码":"密码"}</label><PasswordInput key={mode} ref={passwordInput} id="account-password" autoComplete={mode==="login"?"current-password":"new-password"} minLength={12} maxLength={128} required disabled={busy} aria-invalid={Boolean(fields.password)} aria-describedby={fields.password?"password-error":"password-help"} value={password} onChange={e=>{setPassword(e.target.value);clearField("password");}}/>{fields.password?<p id="password-error" className="auth-field-error">{fields.password}</p>:<p id="password-help" className="auth-hint">12–128个字符，可点击“显示”检查输入。</p>}</div>
  {challenge}
  <Button className="auth-primary" disabled={busy||!config||loginWait>0} type="submit">{checking?"安全检查中…":busy?mode==="login"?"正在登录…":mode==="reset"?"正在修改…":"正在创建账号…":loginWait>0?`${loginWait}秒后可重试`:mode==="register"?"注册并继续":mode==="reset"?"验证并修改密码":"登录"}</Button>
 </form>
 <div className="auth-links"><Button type="button" className="auth-text-button" disabled={busy} onClick={()=>switchTo(mode==="register"?"login":"register")}>{mode==="register"?"已有账号，去登录":"创建新账号"}</Button>{mode!=="reset"&&<Button type="button" className="auth-text-button" disabled={busy} onClick={()=>switchTo("reset")}>忘记或修改密码</Button>}</div>
 </section>;
}
