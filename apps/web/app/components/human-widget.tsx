"use client";
import {useEffect,useRef,useState} from "react";
type Turnstile={render:(element:HTMLElement,options:{sitekey:string;action:string;appearance:"interaction-only";language:"zh-cn";retry:"never";"refresh-expired":"manual";callback:(token:string)=>void;"expired-callback":()=>void;"timeout-callback":()=>void;"error-callback":()=>void})=>string;remove:(id:string)=>void};
declare global{interface Window{turnstile?:Turnstile}}
let scriptPromise:Promise<void>|null=null;
function loadScript(){
 if(window.turnstile)return Promise.resolve();
 if(!scriptPromise)scriptPromise=new Promise((resolve,reject)=>{
  const script=document.createElement("script");let done=false;
  const timeout=setTimeout(()=>finish(false),15000);
  function finish(ok:boolean){if(done)return;done=true;clearTimeout(timeout);if(ok)resolve();else{script.remove();scriptPromise=null;reject(new Error("unavailable"));}}
  script.src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";script.async=true;
  script.onload=()=>finish(Boolean(window.turnstile));script.onerror=()=>finish(false);document.head.appendChild(script);
 });
 return scriptPromise;
}
export default function HumanWidget({siteKey,action,nonce,onToken,onError}:{siteKey:string;action:string;nonce:number;onToken:(token:string)=>void;onError?:(message:string)=>void}){
 const element=useRef<HTMLDivElement>(null);const[error,setError]=useState(false);
 const callbacks=useRef({onToken,onError});callbacks.current={onToken,onError};
 useEffect(()=>{if(!siteKey)return;let cancelled=false;let id:string|undefined;setError(false);
  function fail(message:string){if(cancelled)return;setError(true);callbacks.current.onToken("");callbacks.current.onError?.(message);}
  loadScript().then(()=>{if(cancelled||!element.current||!window.turnstile)return;try{id=window.turnstile.render(element.current,{sitekey:siteKey,action,appearance:"interaction-only",language:"zh-cn",retry:"never","refresh-expired":"manual",callback:token=>{if(!cancelled)callbacks.current.onToken(token);},"expired-callback":()=>fail("安全验证已过期，请重新操作。"),"timeout-callback":()=>fail("安全检查超时，请重新操作。"),"error-callback":()=>fail("安全验证暂不可用，请稍后重试。")});}catch{fail("安全验证暂不可用，请稍后重试。");}}).catch(()=>fail("安全验证加载失败，请检查网络后重试。"));
  return()=>{cancelled=true;if(id&&window.turnstile)window.turnstile.remove(id);};
 },[siteKey,action,nonce]);
 return siteKey?<div><div ref={element}/>{error&&!onError&&<p role="alert">动态验证暂不可用，请刷新后重试。</p>}</div>:null;
}
