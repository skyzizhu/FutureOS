export class AuthFailure extends Error{
 constructor(readonly code:string,message:string,readonly retryAfter=0){super(message);this.name="AuthFailure";}
}
export async function authRequest<T>(path:string,body:unknown):Promise<T>{
 let response:Response;
 try{response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});}catch{throw new AuthFailure("NETWORK_ERROR","网络连接中断，请稍后重试。");}
 let data;try{data=await response.json();}catch{throw new AuthFailure("INVALID_RESPONSE","服务暂不可用，请稍后重试。");}
 if(!response.ok){const retry=Number(response.headers.get("Retry-After"));throw new AuthFailure(typeof data.code==="string"?data.code:"AUTH_ERROR",typeof data.message==="string"?data.message:"操作未完成，请重试。",Number.isFinite(retry)&&retry>0&&retry<=86400?retry:0);}
 return data as T;
}
export async function withHumanCheck<T>(request:(token:string)=>Promise<T>,getToken:(action:string)=>Promise<string>,action:string):Promise<T>{
 try{return await request("");}catch(error){if(error instanceof AuthFailure&&error.code==="HUMAN_VERIFICATION_REQUIRED")return request(await getToken(action));throw error;}
}
export function failureMessage(error:unknown):string{
 if(!(error instanceof Error))return "操作未完成，请重试。";
 if(error instanceof AuthFailure&&error.retryAfter){const wait=error.retryAfter>=3600?`${Math.ceil(error.retryAfter/3600)}小时`:`${error.retryAfter}秒`;return `${error.message}（约${wait}后重试）`;}
 return error.message;
}
