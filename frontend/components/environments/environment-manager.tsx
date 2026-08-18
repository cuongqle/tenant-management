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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAsyncList } from "@/hooks/use-async-list";
import { environmentsApi, projectsApi } from "@/lib/resources";
import { emptyToNull, formatDate } from "@/lib/utils";
import type { Environment, EnvironmentCreate } from "@/types";

const emptyForm = {
  name: "",
  description: "",
  project_id: "",
};

export function EnvironmentManager() {
  const { items, loading, error, reload } = useAsyncList(environmentsApi.list);
  const { items: projects } = useAsyncList(projectsApi.list);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Environment | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function projectName(id: string) {
    return projects.find((project) => project.id === id)?.name ?? id;
  }

  function openCreate() {
    setEditing(null);
    setForm({ ...emptyForm, project_id: projects[0]?.id ?? "" });
    setFormError(null);
    setOpen(true);
  }

  function openEdit(environment: Environment) {
    setEditing(environment);
    setForm({
      name: environment.name,
      description: environment.description ?? "",
      project_id: environment.project_id,
    });
    setFormError(null);
    setOpen(true);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    const payload: EnvironmentCreate = {
      name: form.name.trim(),
      description: emptyToNull(form.description),
      project_id: form.project_id,
    };
    try {
      if (editing) {
        await environmentsApi.update(editing.id, payload);
      } else {
        await environmentsApi.create(payload);
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
        description="All environments across projects. Create under a project for the usual workflow."
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
          <EmptyState>No environments yet.</EmptyState>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Project</th>
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
                    <Link
                      href={`/projects/${environment.project_id}`}
                      className="hover:text-indigo-600"
                    >
                      {projectName(environment.project_id)}
                    </Link>
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
            <FormField label="Project">
              <Select
                value={form.project_id || undefined}
                onValueChange={(value) => setForm({ ...form, project_id: value })}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent>
                  {projects.map((project) => (
                    <SelectItem key={project.id} value={project.id}>
                      {project.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
