import type {NextRequest} from "next/server";
// Next may construct an internal request URL with localhost even when Host is 127.0.0.1.
// Compare the browser Origin with the actual Host, and allow only native local deployment.
export function sameLocalOrigin(request:NextRequest):boolean {
 try {
  const origin=new URL(request.headers.get("origin") || "");
  return origin.host===request.headers.get("host") && origin.protocol==="http:" &&
   ["localhost","127.0.0.1"].includes(origin.hostname);
 } catch {return false;}
}
