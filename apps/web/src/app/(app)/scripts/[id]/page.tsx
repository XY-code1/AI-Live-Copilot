import { ScriptEditor } from "@/components/scripts/script-editor";

export default async function ScriptDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ScriptEditor scriptId={id} />;
}
