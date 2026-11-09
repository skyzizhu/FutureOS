import Protected from "../components/protected";
import ProfileForm from "../onboarding/profile-form";
import AccountSettings from "./workbench";
export const dynamic="force-dynamic";
export default function Page(){return <Protected><div className="narrow-page"><h1>画像与隐私设置</h1><p>当前画像可编辑，已完成报告保留原快照。选填内容只有在勾选授权时用于新报告；撤回授权会取消尚未完成的报告并释放额度。</p><p><a href="/account/security">账号安全与登录会话</a></p><AccountSettings/><ProfileForm/></div></Protected>;}
