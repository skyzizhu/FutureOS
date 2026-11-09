import SocialInbox from "../components/consumer/social-inbox";
import Protected from "../components/protected";
import Notifications from "./workbench";
export const dynamic = "force-dynamic";
export default function Page() {
  return (
    <Protected>
      <div className="narrow-page">
        <h1>通知与订阅</h1>
        <p>
          原主题的重要更新会免费生成新版报告。关闭邮件不会暂停研究和站内通知。
        </p>
        <SocialInbox />
        <Notifications />
      </div>
    </Protected>
  );
}
