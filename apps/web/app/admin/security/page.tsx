import Security from "./workbench";
import SessionPanel from "../../components/session-panel";
export default function Page(){return <><h1>管理员安全与权限</h1><p><a href="/admin/login">管理员登录 / 认证器恢复</a></p><Security/><SessionPanel admin/></>;}
