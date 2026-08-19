import { api } from "@/lib/api";
import type {
  Environment,
  EnvironmentAssign,
  EnvironmentCreate,
  EnvironmentUpdate,
  Organization,
  OrganizationCreate,
  OrganizationUpdate,
  Project,
  ProjectAssign,
  ProjectCreate,
  ProjectUpdate,
  User,
  UserCreate,
  UserUpdate,
  OrganizationMember,
  OrganizationMemberAssign,
  OrganizationMemberUpdate,
  Invitation,
  InvitationCreate,
  InvitationPreview,
} from "@/types";

export const organizationsApi = {
  list: () => api<Organization[]>("/api/v1/organizations/"),
  get: (id: string) => api<Organization>(`/api/v1/organizations/${id}`),
  create: (body: OrganizationCreate) =>
    api<Organization>("/api/v1/organizations/", { method: "POST", body }),
  update: (id: string, body: OrganizationUpdate) =>
    api<Organization>(`/api/v1/organizations/${id}`, { method: "PATCH", body }),
  remove: (id: string) =>
    api<void>(`/api/v1/organizations/${id}`, { method: "DELETE" }),
  projects: (id: string) =>
    api<Project[]>(`/api/v1/organizations/${id}/projects`),
  addProject: (id: string, body: ProjectAssign) =>
    api<Project>(`/api/v1/organizations/${id}/projects`, {
      method: "POST",
      body,
    }),
  members: (id: string) =>
    api<OrganizationMember[]>(`/api/v1/organizations/${id}/members`),
  addMember: (id: string, body: OrganizationMemberAssign) =>
    api<OrganizationMember>(`/api/v1/organizations/${id}/members`, {
      method: "POST",
      body,
    }),
  invitations: (id: string) =>
    api<Invitation[]>(`/api/v1/organizations/${id}/invitations`),
  invite: (id: string, body: InvitationCreate) =>
    api<Invitation>(`/api/v1/organizations/${id}/invitations`, {
      method: "POST",
      body,
    }),
  cancelInvitation: (organizationId: string, invitationId: string) =>
    api<void>(`/api/v1/organizations/${organizationId}/invitations/${invitationId}`, {
      method: "DELETE",
    }),
};

export const organizationMembersApi = {
  update: (id: string, body: OrganizationMemberUpdate) =>
    api<unknown>(`/api/v1/organization-members/${id}`, {
      method: "PATCH",
      body,
    }),
  remove: (id: string) =>
    api<void>(`/api/v1/organization-members/${id}`, { method: "DELETE" }),
};

export const invitationsApi = {
  preview: (token: string) =>
    api<InvitationPreview>(`/api/v1/invitations/${token}`, { auth: false }),
  accept: (token: string) =>
    api<OrganizationMember>(`/api/v1/invitations/${token}/accept`, {
      method: "POST",
    }),
};

export const projectsApi = {
  list: () => api<Project[]>("/api/v1/projects/"),
  get: (id: string) => api<Project>(`/api/v1/projects/${id}`),
  create: (body: ProjectCreate) =>
    api<Project>("/api/v1/projects/", { method: "POST", body }),
  update: (id: string, body: ProjectUpdate) =>
    api<Project>(`/api/v1/projects/${id}`, { method: "PATCH", body }),
  remove: (id: string) => api<void>(`/api/v1/projects/${id}`, { method: "DELETE" }),
  environments: (id: string) =>
    api<Environment[]>(`/api/v1/projects/${id}/environments`),
  addEnvironment: (id: string, body: EnvironmentAssign) =>
    api<Environment>(`/api/v1/projects/${id}/environments`, {
      method: "POST",
      body,
    }),
};

export const environmentsApi = {
  list: () => api<Environment[]>("/api/v1/environments/"),
  create: (body: EnvironmentCreate) =>
    api<Environment>("/api/v1/environments/", { method: "POST", body }),
  update: (id: string, body: EnvironmentUpdate) =>
    api<Environment>(`/api/v1/environments/${id}`, { method: "PATCH", body }),
  remove: (id: string) =>
    api<void>(`/api/v1/environments/${id}`, { method: "DELETE" }),
};

export const usersApi = {
  list: () => api<User[]>("/api/v1/users/"),
  create: (body: UserCreate) =>
    api<User>("/api/v1/users/", { method: "POST", body }),
  update: (id: string, body: UserUpdate) =>
    api<User>(`/api/v1/users/${id}`, { method: "PATCH", body }),
  remove: (id: string) => api<void>(`/api/v1/users/${id}`, { method: "DELETE" }),
};
