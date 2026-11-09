import Discovery from "../../components/consumer/discovery";
export default async function Page({
  params,
}: {
  params: Promise<{ industryId: string }>;
}) {
  const { industryId } = await params;
  return <Discovery industryId={industryId} />;
}
