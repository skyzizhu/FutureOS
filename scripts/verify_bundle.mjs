import fs from "node:fs/promises";
import path from "node:path";
async function scan(folder) {
 for(const item of await fs.readdir(folder,{withFileTypes:true})) {
  const file=path.join(folder,item.name);
  if(item.isDirectory()) await scan(file);
  else if(file.endsWith(".js")) {
   const content=await fs.readFile(file,"utf8");
   for(const secret of ["demo-user-local-only","demo-admin-local-only","demo-other-local-only","OPENAI_API_KEY","TAVILY_API_KEY","DEEPSEEK_API_KEY"]) {
    if(content.includes(secret)) throw new Error(`Server-only credential/config found in client chunk: ${file}`);
   }
  }
 }
}
await scan("apps/web/.next/static");
console.log("PASS: client bundles contain no demo identity tokens or provider key configuration");
