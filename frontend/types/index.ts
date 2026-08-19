export type ApiError = {
  detail: string | Array<{ loc?: unknown[]; msg?: string } | string>;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  name?: string | null;
  password: string;
};

export type Organization = {
  id: string;
  name: string;
  description: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  country: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  industry: string | null;
  created_at: string;
  updated_at: string;
};

export type OrganizationCreate = {
  name: string;
  description?: string | null;
  city?: string | null;
  industry?: string | null;
  email?: string | null;
};

export type OrganizationUpdate = Partial<OrganizationCreate>;

export type Project = {
  id: string;
  name: string;
  description: string | null;
  start_date: string;
  end_date: string | null;
  status: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
};

export type ProjectCreate = {
  name: string;
  description?: string | null;
  start_date: string;
  end_date?: string | null;
  status: string;
  organization_id: string;
};

export type ProjectAssign = Omit<ProjectCreate, "organization_id">;

export type ProjectUpdate = Partial<ProjectCreate>;

export const PROJECT_STATUSES = ["active", "paused", "completed"] as const;

export type Environment = {
  id: string;
  name: string;
  description: string | null;
  project_id: string;
  created_at: string;
  updated_at: string;
};

export type EnvironmentCreate = {
  name: string;
  description?: string | null;
  project_id: string;
};

export type EnvironmentAssign = Omit<EnvironmentCreate, "project_id">;

export type EnvironmentUpdate = Partial<EnvironmentCreate>;

export type User = {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
  updated_at: string;
};

export type UserCreate = {
  email: string;
  name?: string | null;
  password: string;
};

export type UserUpdate = {
  email?: string;
  name?: string | null;
  password?: string;
};

export type OrganizationMember = {
  id: string;
  organization_id: string;
  user_id: string;
  role: string;
  created_at: string;
  updated_at: string;
  user: User;
};

export type OrganizationMemberAssign = {
  user_id: string;
  role?: string;
};

export type OrganizationMemberUpdate = {
  role: string;
};

export const MEMBER_ROLES = ["admin", "member"] as const;

export type Me = {
  id: string;
  email: string;
  name: string | null;
  is_superuser: boolean;
};

export type Invitation = {
  id: string;
  organization_id: string;
  email: string;
  role: string;
  token: string;
  expires_at: string;
  accepted_at: string | null;
  invited_by_id: string | null;
  created_at: string;
  updated_at: string;
};

export type InvitationCreate = {
  email: string;
  role?: string;
};

export type InvitationPreview = {
  organization_id: string;
  organization_name: string;
  email: string;
  role: string;
  expires_at: string;
  accepted: boolean;
  expired: boolean;
};
