import type { NextConfig } from "next";
const config: NextConfig = {poweredByHeader:false,async headers(){return [{source:"/(.*)",headers:[
 {key:"X-Content-Type-Options",value:"nosniff"},{key:"Referrer-Policy",value:"no-referrer"},
 {key:"X-Frame-Options",value:"DENY"},{key:"Permissions-Policy",value:"camera=(), microphone=(), geolocation=()"},
 {key:"Content-Security-Policy",value:"default-src 'self'; script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://challenges.cloudflare.com; frame-src https://challenges.cloudflare.com; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"}
]}];}};
export default config;
