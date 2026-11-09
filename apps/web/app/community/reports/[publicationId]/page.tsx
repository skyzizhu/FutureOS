import PublicReader from "../../../components/consumer/public-reader";
export default async function Page({
  params,
}: {
  params: Promise<{ publicationId: string }>;
}) {
  const { publicationId } = await params;
  return <PublicReader id={publicationId} />;
}
