import Link from "next/link";
import Protected from "../components/protected";
import GuidedResearch from "./guided";
import Intake from "./workbench";
export const dynamic="force-dynamic";
export default function Page(){return <Protected><p className="eyebrow">更多研究设置</p><h1>确认研究范围</h1><p><Link className="button" href="/chat">用聊天开始一段研究</Link></p><p>先确认希望观察的问题。这里只做范围说明，提交报告前不预留额度。</p><GuidedResearch/><details><summary>首份免费报告的范围预览</summary><Intake/></details></Protected>;}
