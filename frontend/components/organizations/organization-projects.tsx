"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

import { EmptyState, PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
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
import { organizationsApi, projectsApi } from "@/lib/resources";
import {
  emptyToNull,
  formatDate,
  fromDateTimeLocal,
  toDateTimeLocal,
} from "@/lib/utils";
import { PROJECT_STATUSES, type Project, type ProjectAssign } from "@/types";

const emptyForm = {
  name: "",
  description: "",
  status: "active",
  start_date: "",
  end_date: "",
};

export function OrganizationProjects({
  organizationId,
}: {
  organizationId: string;
}) {
  const { items, loading, error, reload } = useAsyncList(() =>
    organizationsApi.projects(organizationId),
  );
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Project | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function openCreate() {
    setEditing(null);
    setForm({
      ...emptyForm,
      start_date: toDateTimeLocal(new Date().toISOString()),
    });
    setFormError(null);
    setOpen(true);
  }

  function openEdit(project: Project) {
    setEditing(project);
    setForm({
      name: project.name,
      description: project.description ?? "",
      status: project.status,
      start_date: toDateTimeLocal(project.start_date),
      end_date: toDateTimeLocal(project.end_date),
    });
    setFormError(null);
    setOpen(true);
  }

  function payload(): ProjectAssign {
    return {
      name: form.name.trim(),
      description: emptyToNull(form.description),
      status: form.status,
      start_date: fromDateTimeLocal(form.start_date),
      end_date: form.end_date ? fromDateTimeLocal(form.end_date) : null,
    };
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      if (editing) {
        await projectsApi.update(editing.id, payload());
      } else {
        await organizationsApi.addProject(organizationId, payload());
      }
      setOpen(false);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(project: Project) {
    if (!window.confirm(`Delete ${project.name}?`)) {
      return;
    }
    await projectsApi.remove(project.id);
    await reload();
  }

  return (
    <>
      <PageHeader
        title="Projects"
        description="Create and manage workstreams in this organization."
        actionLabel="New project"
        onAction={openCreate}
      />
      <Card className="gap-0 py-0">
        {error ? (
          <p className="px-4 py-3 text-sm text-destructive">{error}</p>
        ) : null}
        {loading ? (
          <EmptyState>Loading projects...</EmptyState>
        ) : items.length === 0 ? (
          <EmptyState>No projects yet. Create one for this organization.</EmptyState>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Start</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y">
              {items.map((project) => (
                <tr key={project.id} className="hover:bg-muted/40">
                  <td className="px-4 py-3 font-medium">
                    <Link
                      href={`/projects/${project.id}`}
                      className="hover:text-indigo-600"
                    >
                      {project.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant="secondary">{project.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {formatDate(project.start_date)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/projects/${project.id}`}>Open</Link>
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEdit(project)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => void onDelete(project)}
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
            <DialogTitle>{editing ? "Edit project" : "New project"}</DialogTitle>
          </DialogHeader>
          <form className="flex flex-col gap-4" onSubmit={onSubmit}>
            <FormField label="Name">
              <Input
                required
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
              />
            </FormField>
            <FormField label="Status">
              <Select
                value={form.status}
                onValueChange={(value) => setForm({ ...form, status: value })}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PROJECT_STATUSES.map((status) => (
                    <SelectItem key={status} value={status}>
                      {status}
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
            <div className="grid grid-cols-2 gap-4">
              <FormField label="Start date">
                <Input
                  required
                  type="datetime-local"
                  value={form.start_date}
                  onChange={(event) =>
                    setForm({ ...form, start_date: event.target.value })
                  }
                />
              </FormField>
              <FormField label="End date">
                <Input
                  type="datetime-local"
                  value={form.end_date}
                  onChange={(event) =>
                    setForm({ ...form, end_date: event.target.value })
                  }
                />
              </FormField>
            </div>
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
