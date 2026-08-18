"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import { OrganizationMembers } from "@/components/organizations/organization-members";
import { OrganizationProjects } from "@/components/organizations/organization-projects";
import { EmptyState, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { organizationsApi } from "@/lib/resources";
import { emptyToNull } from "@/lib/utils";
import type { Organization, OrganizationUpdate } from "@/types";

const emptyForm = {
  name: "",
  description: "",
  industry: "",
  city: "",
  email: "",
};

export function OrganizationDetail({
  organizationId,
}: {
  organizationId: string;
}) {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const item = await organizationsApi.get(organizationId);
        if (cancelled) {
          return;
        }
        setOrganization(item);
        setForm({
          name: item.name,
          description: item.description ?? "",
          industry: item.industry ?? "",
          city: item.city ?? "",
          email: item.email ?? "",
        });
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Organization not found");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [organizationId]);

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setSaveError(null);
    const payload: OrganizationUpdate = {
      name: form.name.trim(),
      description: emptyToNull(form.description),
      industry: emptyToNull(form.industry),
      city: emptyToNull(form.city),
      email: emptyToNull(form.email),
    };
    try {
      const updated = await organizationsApi.update(organizationId, payload);
      setOrganization(updated);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <EmptyState>Loading organization...</EmptyState>;
  }

  if (error || organization === null) {
    return (
      <div>
        <Link
          href="/organizations"
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          ← Organizations
        </Link>
        <p className="mt-4 text-sm text-destructive">
          {error ?? "Organization not found."}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <div>
        <Link
          href="/organizations"
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          ← Organizations
        </Link>
        <PageHeader
          title={organization.name}
          description={organization.description ?? "Members, projects, and settings."}
        />
      </div>

      <OrganizationMembers organizationId={organizationId} />

      <OrganizationProjects organizationId={organizationId} />

      <section>
        <PageHeader
          title="Settings"
          description="Update this organization's profile."
        />
        <Card className="p-6">
          <form className="flex max-w-xl flex-col gap-4" onSubmit={onSave}>
            <FormField label="Name">
              <Input
                required
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
              />
            </FormField>
            <FormField label="Description">
              <Input
                value={form.description}
                onChange={(event) =>
                  setForm({ ...form, description: event.target.value })
                }
              />
            </FormField>
            <div className="grid grid-cols-2 gap-4">
              <FormField label="Industry">
                <Input
                  value={form.industry}
                  onChange={(event) =>
                    setForm({ ...form, industry: event.target.value })
                  }
                />
              </FormField>
              <FormField label="City">
                <Input
                  value={form.city}
                  onChange={(event) =>
                    setForm({ ...form, city: event.target.value })
                  }
                />
              </FormField>
            </div>
            <FormField label="Email">
              <Input
                type="email"
                value={form.email}
                onChange={(event) =>
                  setForm({ ...form, email: event.target.value })
                }
              />
            </FormField>
            {saveError ? (
              <p className="text-sm text-destructive">{saveError}</p>
            ) : null}
            <div>
              <Button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Save settings"}
              </Button>
            </div>
          </form>
        </Card>
      </section>
    </div>
  );
}
