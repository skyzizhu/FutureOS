export async function accountApi(path:string,method="GET",body?:unknown,key?:string){
 const response=await fetch(`/api/account/${path}`,{method,headers:{"Content-Type":"application/json",...(key?{"Idempotency-Key":key}:{})},body:body===undefined?undefined:JSON.stringify(body),cache:"no-store"});
 const data=await response.json();if(!response.ok)throw new Error(`${data.code||"ERROR"}：${data.message||"请求失败"}`);return data;
}
