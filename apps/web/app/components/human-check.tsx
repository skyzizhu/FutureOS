"use client";
import {Button} from "./ui/controls";

import {useCallback,useEffect,useRef,useState} from "react";
import HumanWidget from "./human-widget";
import {AuthFailure} from "./auth-request";
type Pending={id:number;action:string};
export function useHumanCheck(siteKey:string,enabled:boolean){
 const[pending,setPending]=useState<Pending|null>(null);const next=useRef(0);
 const waiter=useRef<{resolve:(token:string)=>void;reject:(error:Error)=>void}|null>(null);
 const cancel=useCallback(()=>{const current=waiter.current;waiter.current=null;setPending(null);current?.reject(new AuthFailure("HUMAN_CANCELLED","安全检查已取消，可以重新操作。"));},[]);
 const complete=useCallback((token:string)=>{if(!token)return;const current=waiter.current;waiter.current=null;setPending(null);current?.resolve(token);},[]);
 const fail=useCallback((message:string)=>{const current=waiter.current;waiter.current=null;setPending(null);current?.reject(new AuthFailure("HUMAN_VERIFICATION_FAILED",message));},[]);
 const getToken=useCallback((action:string):Promise<string>=>{
  if(!enabled)return Promise.resolve("");
  if(!siteKey)return Promise.reject(new AuthFailure("HUMAN_UNAVAILABLE","安全验证配置暂不可用，请稍后重试。"));
  if(waiter.current)return Promise.reject(new AuthFailure("HUMAN_PENDING","安全检查正在进行，请稍候。"));
  return new Promise((resolve,reject)=>{waiter.current={resolve,reject};setPending({id:++next.current,action});});
 },[enabled,siteKey]);
 useEffect(()=>{if(!pending)return;const timeout=setTimeout(()=>fail("安全检查超时，请重新操作。"),120000);return()=>clearTimeout(timeout);},[pending,fail]);
 useEffect(()=>()=>{waiter.current?.reject(new AuthFailure("HUMAN_CANCELLED","安全检查已取消。"));waiter.current=null;},[]);
 const challenge=pending?<div className="auth-human-check" role="region" aria-label="安全检查"><p role="status">正在进行安全检查；通常会自动完成，需要时请按提示操作。</p><HumanWidget key={pending.id} siteKey={siteKey} action={pending.action} nonce={pending.id} onToken={complete} onError={fail}/><Button type="button" className="auth-text-button" onClick={cancel}>取消安全检查</Button></div>:null;
 return {getToken,challenge,checking:pending!==null};
}
