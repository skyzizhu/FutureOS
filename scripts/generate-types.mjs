import fs from "node:fs/promises";
import {compile} from "json-schema-to-typescript";
import openapiTS,{astToString} from "openapi-typescript";
const root = new URL("../packages/contracts/",import.meta.url);
const files = (await fs.readdir(new URL("schemas/",root))).filter(x=>x.endsWith(".json")).sort();
const definitions = {};
const properties = {};
for(const file of files) {
 const schema = JSON.parse(await fs.readFile(new URL(`schemas/${file}`,root),"utf8"));
 const {$defs,...body} = schema;
 for(const [name,value] of Object.entries($defs || {})) {
  if(definitions[name] && JSON.stringify(definitions[name])!==JSON.stringify(value)) throw new Error(`Conflicting definition ${name}`);
  definitions[name]=value;
 }
 definitions[schema.title]=body;
 properties[schema.title]={$ref:`#/$defs/${schema.title}`};
}
const bundle = {title:"DomainContracts",type:"object",properties,additionalProperties:false,$defs:definitions};
await fs.mkdir(new URL("generated/",root),{recursive:true});
const code = await compile(bundle,"DomainContracts",{bannerComment:"// Generated from Pydantic JSON Schemas. Do not edit.",additionalProperties:false});
await fs.writeFile(new URL("generated/domain.d.ts",root),code);
const ast = await openapiTS(new URL("openapi.json",root));
await fs.writeFile(new URL("generated/api.d.ts",root),astToString(ast));
console.log(`Generated ${files.length} domain schemas and API types`);
