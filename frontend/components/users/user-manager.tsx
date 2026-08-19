"use client";

import { FormEvent, useEffect, useState } from "react";

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
import { readAccessTokenClaims } from "@/lib/auth";
import { usersApi } from "@/lib/resources";
import { emptyToNull, formatDate } from "@/lib/utils";
import type { User, UserCreate, UserUpdate } from "@/types";

const emptyForm = {
  name: "",
  email: "",
  password: "",
};

export function UserManager() {
  const [isSuperuser, setIsSuperuser] = useState(false);
  const [selfId, setSelfId] = useState<string | undefined>();
  const { items, loading, error, reload } = useAsyncList(usersApi.list);

  useEffect(() => {
    const claims = readAccessTokenClaims();
    setIsSuperuser(Boolean(claims?.is_superuser));
    setSelfId(claims?.sub);
  }, []);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setFormError(null);
    setOpen(true);
  }

  function openEdit(user: User) {
    setEditing(user);
    setForm({
      name: user.name ?? "",
      email: user.email,
      password: "",
    });
    setFormError(null);
    setOpen(true);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      if (editing) {
        const payload: UserUpdate = {
          email: form.email.trim(),
          name: emptyToNull(form.name),
        };
        if (form.password.trim().length > 0) {
          payload.password = form.password;
        }
        await usersApi.update(editing.id, payload);
      } else {
        const payload: UserCreate = {
          email: form.email.trim(),
          name: emptyToNull(form.name),
          password: form.password,
        };
        await usersApi.create(payload);
      }
      setOpen(false);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(user: User) {
    if (!window.confirm(`Delete ${user.email}?`)) {
      return;
    }
    await usersApi.remove(user.id);
    await reload();
  }

  return (
    <>
      <PageHeader
        title="Users"
        description={
          isSuperuser
            ? "All accounts. Create users here, or invite them into an organization."
            : "People who share an organization with you. Invite others from an organization page."
        }
        actionLabel={isSuperuser ? "New user" : undefined}
        onAction={isSuperuser ? openCreate : undefined}
      />
      <Card className="gap-0 py-0">
        {error ? (
          <p className="px-4 py-3 text-sm text-destructive">{error}</p>
        ) : null}
        {loading ? (
          <EmptyState>Loading users...</EmptyState>
        ) : items.length === 0 ? (
          <EmptyState>
            {isSuperuser
              ? "No users yet. Create the first one."
              : "No users in your organizations yet."}
          </EmptyState>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y">
              {items.map((user) => (
                <tr key={user.id} className="hover:bg-muted/40">
                  <td className="px-4 py-3 font-medium">{user.name ?? "—"}</td>
                  <td className="px-4 py-3 text-muted-foreground">{user.email}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {formatDate(user.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {isSuperuser || user.id === selfId ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEdit(user)}
                      >
                        Edit
                      </Button>
                    ) : null}
                    {isSuperuser ? (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => void onDelete(user)}
                      >
                        Delete
                      </Button>
                    ) : null}
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
            <DialogTitle>{editing ? "Edit user" : "New user"}</DialogTitle>
          </DialogHeader>
          <form className="flex flex-col gap-4" onSubmit={onSubmit}>
            <FormField label="Name">
              <Input
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
              />
            </FormField>
            <FormField label="Email">
              <Input
                required
                type="email"
                value={form.email}
                onChange={(event) =>
                  setForm({ ...form, email: event.target.value })
                }
              />
            </FormField>
            <FormField label={editing ? "New password" : "Password"}>
              <Input
                required={!editing}
                minLength={8}
                type="password"
                autoComplete="new-password"
                placeholder={editing ? "Leave blank to keep current" : undefined}
                value={form.password}
                onChange={(event) =>
                  setForm({ ...form, password: event.target.value })
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
