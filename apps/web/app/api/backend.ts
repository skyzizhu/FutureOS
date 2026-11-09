import "server-only";
export const backend = process.env.API_INTERNAL_URL || "http://127.0.0.1:8100";
export const demoToken = process.env.DEMO_USER_TOKEN || "demo-user-local-only";
export function demoOnly() {
 if(process.env.DEMO_MODE !== "true") throw new Error("M0 Web requires DEMO_MODE=true");
}
