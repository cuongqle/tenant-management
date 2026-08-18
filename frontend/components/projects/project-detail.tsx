"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import { EmptyState, PageHeader } from "@/components/layout/page-header";
import { ProjectEnvironments } from "@/components/projects/project-environments";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { organizationsApi, projectsApi } from "@/lib/resources";
import {
  emptyToNull,
  fromDateTimeLocal,
  toDateTimeLocal,
} from "@/lib/utils";
import {
  PROJECT_STATUSES,
  type Project,
  type ProjectUpdate,
} from "@/types";

const emptyForm = {
  name: "",
  description: "",
  status: "active",
  start_date: "",
  end_date: "",
};

export function ProjectDetail({ projectId }: { projectId: string }) {
  const [project, setProject] = useState<Project | null>(null);
  const [organizationName, setOrganizationName] = useState<string | null>(null);
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
        const item = await projectsApi.get(projectId);
        if (cancelled) {
          return;
        }
        setProject(item);
        setForm({
          name: item.name,
          description: item.description ?? "",
          status: item.status,
          start_date: toDateTimeLocal(item.start_date),
          end_date: toDateTimeLocal(item.end_date),
        });
        try {
          const organization = await organizationsApi.get(item.organization_id);
          if (!cancelled) {
            setOrganizationName(organization.name);
          }
        } catch {
          if (!cancelled) {
            setOrganizationName(null);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Project not found");
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
  }, [projectId]);

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setSaveError(null);
    const payload: ProjectUpdate = {
      name: form.name.trim(),
      description: emptyToNull(form.description),
      status: form.status,
      start_date: fromDateTimeLocal(form.start_date),
      end_date: form.end_date ? fromDateTimeLocal(form.end_date) : null,
    };
    try {
      const updated = await projectsApi.update(projectId, payload);
      setProject(updated);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <EmptyState>Loading project...</EmptyState>;
  }

  if (error || project === null) {
    return (
      <div>
        <Link
          href="/projects"
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          ← Projects
        </Link>
        <p className="mt-4 text-sm text-destructive">
          {error ?? "Project not found."}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <div>
        <Link
          href={`/organizations/${project.organization_id}`}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          ← {organizationName ?? "Organization"}
        </Link>
        <PageHeader
          title={project.name}
          description={project.description ?? "Environments and settings."}
        />
      </div>

      <ProjectEnvironments projectId={projectId} />

      <section>
        <PageHeader
          title="Settings"
          description="Update this project's details."
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
