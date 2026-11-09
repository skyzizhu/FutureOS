import Protected from "../../components/protected";
import ReportView from "./workbench";
export const dynamic="force-dynamic";
export default async function Page({params,searchParams}:{params:Promise<{reportId:string}>;searchParams:Promise<{version?:string}>}){const{reportId}=await params;const{version}=await searchParams;return <Protected><div className="report-reader-shell"><ReportView reportId={reportId} versionId={version}/></div></Protected>;}
