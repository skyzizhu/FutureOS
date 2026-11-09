"use client";
import {TextInput,Button} from "./ui/controls";

import {forwardRef,useState,type InputHTMLAttributes} from "react";
type Props=Omit<InputHTMLAttributes<HTMLInputElement>,"type">;
const PasswordInput=forwardRef<HTMLInputElement,Props>(function PasswordInput(props,ref){
 const[visible,setVisible]=useState(false);
 return <div className="password-control"><TextInput {...props} ref={ref} type={visible?"text":"password"}/><Button type="button" className="password-toggle" aria-label={visible?"隐藏密码":"显示密码"} aria-pressed={visible} aria-controls={props.id} onClick={()=>setVisible(!visible)}>{visible?"隐藏":"显示"}</Button></div>;
});
export default PasswordInput;
