import Protected from "../../components/protected";
import Forecast from "./workbench";
export const dynamic="force-dynamic";
export default async function Page({params}:{params:Promise<{versionId:string}>}){const{versionId}=await params;return <Protected><div className="report-reader-shell"><Forecast versionId={versionId}/></div></Protected>;}
