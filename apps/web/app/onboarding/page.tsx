import Protected from "../components/protected";
import ProfileForm from "./profile-form";
export const dynamic = "force-dynamic";
export default function Onboarding() {
  return (
    <Protected>
      <div className="narrow-page">
        <p className="eyebrow">个人资料 · 默认私有</p>
        <h1>先选与你相关的行业</h1>
        <p>
          选择你所在或关注的行业，保存后会加入「我的行业」。其余个人资料均可跳过。
        </p>
        <ProfileForm />
      </div>
    </Protected>
  );
}
