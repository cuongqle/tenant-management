"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";

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
import { organizationMembersApi, organizationsApi, usersApi } from "@/lib/resources";
import { formatDate } from "@/lib/utils";
import { MEMBER_ROLES } from "@/types";

function inviteLink(token: string): string {
  return `${window.location.origin}/invite/${token}`;
}

export function OrganizationMembers({
  organizationId,
}: {
  organizationId: string;
}) {
  const { items, loading, error, reload } = useAsyncList(() =>
    organizationsApi.members(organizationId),
  );
  const {
    items: invitations,
    loading: invitationsLoading,
    error: invitationsError,
    reload: reloadInvitations,
  } = useAsyncList(() => organizationsApi.invitations(organizationId));
  const { items: users } = useAsyncList(usersApi.list);
  const [open, setOpen] = useState(false);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [userId, setUserId] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [role, setRole] = useState<(typeof MEMBER_ROLES)[number]>("member");
  const [inviteRole, setInviteRole] = useState<(typeof MEMBER_ROLES)[number]>("member");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const memberUserIds = useMemo(
    () => new Set(items.map((member) => member.user_id)),
    [items],
  );
  const availableUsers = users.filter((user) => !memberUserIds.has(user.id));

  function openAdd() {
    setUserId(availableUsers[0]?.id ?? "");
    setRole("member");
    setFormError(null);
    setOpen(true);
  }

  function openInvite() {
    setInviteEmail("");
    setInviteRole("member");
    setFormError(null);
    setInviteOpen(true);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      await organizationsApi.addMember(organizationId, {
        user_id: userId,
        role,
      });
      setOpen(false);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Could not add member");
    } finally {
      setSaving(false);
    }
  }

  async function onInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      const invitation = await organizationsApi.invite(organizationId, {
        email: inviteEmail.trim(),
        role: inviteRole,
      });
      setInviteOpen(false);
      await reloadInvitations();
      try {
        await navigator.clipboard.writeText(inviteLink(invitation.token));
      } catch {
        // Clipboard can be blocked; the invite still appears in the pending list.
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Could not send invitation");
    } finally {
      setSaving(false);
    }
  }

  async function onRoleChange(memberId: string, nextRole: string) {
    try {
      await organizationMembersApi.update(memberId, { role: nextRole });
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Could not update role");
      await reload();
    }
  }

  async function onRemove(memberId: string, email: string) {
    if (!window.confirm(`Remove ${email} from this organization?`)) {
      return;
    }
    try {
      await organizationMembersApi.remove(memberId);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Could not remove member");
    }
  }

  async function onCopyInvite(token: string) {
    await navigator.clipboard.writeText(inviteLink(token));
  }

  async function onCancelInvite(invitationId: string, email: string) {
    if (!window.confirm(`Cancel invitation for ${email}?`)) {
      return;
    }
    try {
      await organizationsApi.cancelInvitation(organizationId, invitationId);
      await reloadInvitations();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Could not cancel invitation");
    }
  }

  return (
    <>
      <PageHeader
        title="Members"
        description="Invite people by email, or add an existing user and set their role."
        actions={
          <>
            <Button variant="outline" size="lg" onClick={openInvite}>
              Invite by email
            </Button>
            <Button size="lg" onClick={openAdd}>
              Add member
            </Button>
          </>
        }
      />
      <Card className="gap-0 py-0">
        {error ? (
          <p className="px-4 py-3 text-sm text-destructive">{error}</p>
        ) : null}
        {formError && !open && !inviteOpen ? (
          <p className="px-4 py-3 text-sm text-destructive">{formError}</p>
        ) : null}
        {loading ? (
          <EmptyState>Loading members...</EmptyState>
        ) : items.length === 0 ? (
          <EmptyState>No members yet. Invite someone or add an existing user.</EmptyState>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Joined</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y">
              {items.map((member) => (
                <tr key={member.id} className="hover:bg-muted/40">
                  <td className="px-4 py-3 font-medium">
                    {member.user.name ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {member.user.email}
                  </td>
                  <td className="px-4 py-3">
                    <Select
                      value={member.role}
                      onValueChange={(value) => void onRoleChange(member.id, value)}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {MEMBER_ROLES.map((item) => (
                          <SelectItem key={item} value={item}>
                            {item}
                          </SelectItem>
                        ))}
                        {MEMBER_ROLES.includes(
                          member.role as (typeof MEMBER_ROLES)[number],
                        ) ? null : (
                          <SelectItem value={member.role}>{member.role}</SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {formatDate(member.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => void onRemove(member.id, member.user.email)}
                    >
                      Remove
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <div className="mt-6">
        <h3 className="mb-3 text-sm font-semibold text-slate-900">Pending invitations</h3>
        <Card className="gap-0 py-0">
          {invitationsError ? (
            <p className="px-4 py-3 text-sm text-destructive">{invitationsError}</p>
          ) : null}
          {invitationsLoading ? (
            <EmptyState>Loading invitations...</EmptyState>
          ) : invitations.length === 0 ? (
            <EmptyState>No pending invitations.</EmptyState>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Role</th>
                  <th className="px-4 py-3 font-medium">Expires</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y">
                {invitations.map((invitation) => (
                  <tr key={invitation.id} className="hover:bg-muted/40">
                    <td className="px-4 py-3 font-medium">{invitation.email}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {invitation.role}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {formatDate(invitation.expires_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => void onCopyInvite(invitation.token)}
                        >
                          Copy link
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() =>
                            void onCancelInvite(invitation.id, invitation.email)
                          }
                        >
                          Cancel
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Add member</DialogTitle>
          </DialogHeader>
          <form className="flex flex-col gap-4" onSubmit={onSubmit}>
            <FormField label="User">
              {availableUsers.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Every user is already a member.{" "}
                  <Link href="/users" className="font-medium text-indigo-600">
                    Create a user
                  </Link>{" "}
                  first, or invite by email.
                </p>
              ) : (
                <Select value={userId || undefined} onValueChange={setUserId}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select user" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableUsers.map((user) => (
                      <SelectItem key={user.id} value={user.id}>
                        {user.name ? `${user.name} (${user.email})` : user.email}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </FormField>
            <FormField label="Role">
              <Select
                value={role}
                onValueChange={(value) =>
                  setRole(value as (typeof MEMBER_ROLES)[number])
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MEMBER_ROLES.map((item) => (
                    <SelectItem key={item} value={item}>
                      {item}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
            {formError ? (
              <p className="text-sm text-destructive">{formError}</p>
            ) : null}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving || availableUsers.length === 0}>
                {saving ? "Adding..." : "Add"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Invite by email</DialogTitle>
          </DialogHeader>
          <form className="flex flex-col gap-4" onSubmit={onInvite}>
            <FormField label="Email">
              <Input
                type="email"
                required
                value={inviteEmail}
                onChange={(event) => setInviteEmail(event.target.value)}
                placeholder="user@example.com"
              />
            </FormField>
            <FormField label="Role">
              <Select
                value={inviteRole}
                onValueChange={(value) =>
                  setInviteRole(value as (typeof MEMBER_ROLES)[number])
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MEMBER_ROLES.map((item) => (
                    <SelectItem key={item} value={item}>
                      {item}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
            <p className="text-sm text-muted-foreground">
              The invite link is copied to your clipboard. Share it with the person
              you invited.
            </p>
            {formError ? (
              <p className="text-sm text-destructive">{formError}</p>
            ) : null}
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setInviteOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? "Inviting..." : "Create invite"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
