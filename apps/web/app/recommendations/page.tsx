import Protected from "../components/protected";
import Recommendations from "./workbench";
export const dynamic="force-dynamic";
export default function Page(){return <Protected><div className="narrow-page"><h1>建议中心</h1><p>建议可以选择不执行。高成本、不可逆的动作不会因为预测看起来相关就被推荐。</p><Recommendations/></div></Protected>;}
