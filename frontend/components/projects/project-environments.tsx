"use client";

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
import { environmentsApi, projectsApi } from "@/lib/resources";
import { emptyToNull, formatDate } from "@/lib/utils";
import type { Environment, EnvironmentAssign } from "@/types";

const emptyForm = {
  name: "",
  description: "",
};

export function ProjectEnvironments({ projectId }: { projectId: string }) {
  const { items, loading, error, reload } = useAsyncList(() =>
    projectsApi.environments(projectId),
  );
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Environment | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setFormError(null);
    setOpen(true);
  }

  function openEdit(environment: Environment) {
    setEditing(environment);
    setForm({
      name: environment.name,
      description: environment.description ?? "",
    });
    setFormError(null);
    setOpen(true);
  }

  function payload(): EnvironmentAssign {
    return {
      name: form.name.trim(),
      description: emptyToNull(form.description),
    };
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      if (editing) {
        await environmentsApi.update(editing.id, payload());
      } else {
        await projectsApi.addEnvironment(projectId, payload());
      }
      setOpen(false);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(environment: Environment) {
    if (!window.confirm(`Delete ${environment.name}?`)) {
      return;
    }
    await environmentsApi.remove(environment.id);
    await reload();
  }

  return (
    <>
      <PageHeader
        title="Environments"
        description="Create runtime targets for this project."
        actionLabel="New environment"
        onAction={openCreate}
      />
      <Card className="gap-0 py-0">
        {error ? (
          <p className="px-4 py-3 text-sm text-destructive">{error}</p>
        ) : null}
        {loading ? (
          <EmptyState>Loading environments...</EmptyState>
        ) : items.length === 0 ? (
          <EmptyState>No environments yet. Create one for this project.</EmptyState>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y">
              {items.map((environment) => (
                <tr key={environment.id} className="hover:bg-muted/40">
                  <td className="px-4 py-3 font-medium">
                    {environment.name}
                    {environment.description ? (
                      <p className="font-normal text-muted-foreground">
                        {environment.description}
                      </p>
                    ) : null}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {formatDate(environment.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEdit(environment)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => void onDelete(environment)}
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
              {editing ? "Edit environment" : "New environment"}
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
