import { OrganizationDetail } from "@/components/organizations/organization-detail";

export default async function OrganizationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <OrganizationDetail organizationId={id} />;
}
