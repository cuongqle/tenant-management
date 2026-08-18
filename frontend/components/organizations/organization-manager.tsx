"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { EmptyState, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useAsyncList } from "@/hooks/use-async-list";
import { organizationsApi } from "@/lib/resources";
import { emptyToNull, formatDate } from "@/lib/utils";
import type { Organization, OrganizationCreate } from "@/types";

const emptyForm = {
  name: "",
  description: "",
  industry: "",
  city: "",
  email: "",
};

export function OrganizationManager() {
  const { items, loading, error, reload } = useAsyncList(organizationsApi.list);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Organization | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setFormError(null);
    setOpen(true);
  }

  function openEdit(organization: Organization) {
    setEditing(organization);
    setForm({
      name: organization.name,
      description: organization.description ?? "",
      industry: organization.industry ?? "",
      city: organization.city ?? "",
      email: organization.email ?? "",
    });
    setFormError(null);
    setOpen(true);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    const payload: OrganizationCreate = {
      name: form.name.trim(),
      description: emptyToNull(form.description),
      industry: emptyToNull(form.industry),
      city: emptyToNull(form.city),
      email: emptyToNull(form.email),
    };
    try {
      if (editing) {
        await organizationsApi.update(editing.id, payload);
      } else {
        await organizationsApi.create(payload);
      }
      setOpen(false);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(organization: Organization) {
    if (!window.confirm(`Delete ${organization.name}?`)) {
      return;
    }
    await organizationsApi.remove(organization.id);
    await reload();
  }

  return (
    <>
      <PageHeader
        title="Organizations"
        description="Create and manage tenant organizations."
        actionLabel="New organization"
        onAction={openCreate}
      />
      <Card className="gap-0 py-0">
        {error ? (
          <p className="px-4 py-3 text-sm text-destructive">{error}</p>
        ) : null}
        {loading ? (
          <EmptyState>Loading organizations...</EmptyState>
        ) : items.length === 0 ? (
          <EmptyState>No organizations yet. Create the first one.</EmptyState>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Industry</th>
                <th className="px-4 py-3 font-medium">City</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y">
              {items.map((organization) => (
                <tr key={organization.id} className="hover:bg-muted/40">
                  <td className="px-4 py-3 font-medium">
                    <Link
                      href={`/organizations/${organization.id}`}
                      className="hover:text-indigo-600"
                    >
                      {organization.name}
                    </Link>
                    {organization.description ? (
                      <p className="font-normal text-muted-foreground">
                        {organization.description}
                      </p>
                    ) : null}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {organization.industry ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {organization.city ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {formatDate(organization.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/organizations/${organization.id}`}>Open</Link>
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEdit(organization)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => void onDelete(organization)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {editing ? "Edit organization" : "New organization"}
            </DialogTitle>
          </DialogHeader>
          <form className="flex flex-col gap-4" onSubmit={onSubmit}>
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
            {formError ? (
              <p className="text-sm text-destructive">{formError}</p>
            ) : null}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
