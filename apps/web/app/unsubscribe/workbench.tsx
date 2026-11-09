"use client";
import {Button} from "../components/ui/controls";

import {useState} from "react";
export default function Unsubscribe({token}:{token:string}){const[message,setMessage]=useState("");const[busy,setBusy]=useState(false);return <><Button disabled={!token||busy} onClick={async()=>{setBusy(true);try{const response=await fetch("/api/mail/unsubscribe",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token})});if(!response.ok)throw new Error("链接无效或已过期，请登录后在通知设置中退订。");setMessage("退订成功，原主题研究与站内通知继续运行。");}catch(e){setMessage(e instanceof Error?e.message:"操作失败");setBusy(false);}}}>确认退订全部邮件</Button>{message&&<p role="status">{message}</p>}</>;}
