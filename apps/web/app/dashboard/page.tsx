import Protected from "../components/protected";
import MyCenter from "../components/consumer/my-center";
export const dynamic = "force-dynamic";
export default function Page() {
  return (
    <Protected>
      <MyCenter />
    </Protected>
  );
}
