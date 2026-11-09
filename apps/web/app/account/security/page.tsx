import Protected from "../../components/protected";
import SessionPanel from "../../components/session-panel";
export default function Page(){return <Protected><div className="narrow-page"><h1>账号安全</h1><p><a href="/auth/login?mode=reset">通过邮箱验证码修改密码</a></p><SessionPanel/></div></Protected>;}
