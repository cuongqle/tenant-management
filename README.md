# Tenant Management

App for managing organizations, users, projects, and environments.

## Live demo

> **LIVE DEMO** — [https://tenant-management-omega.vercel.app/](https://tenant-management-omega.vercel.app/)
>
> Deployed on **Vercel** (frontend), **Render** (API), and **Neon** (Postgres).
>
> Seed login: `admin@example.com` / `Admin123!` (platform super admin)

## Local

- **Frontend:** http://localhost:3000
- **API docs:** http://localhost:8000/docs

## Roles

A **super admin** is a platform operator (`is_superuser`), not the same as an organization `admin`. Super admins can do more than a normal org admin or member.

**Super admin**
- See every organization, project, environment, and user (no membership required)
- Create an organization without joining it, then invite people in
- Open, edit, and delete any tenant and its projects or environments
- Create and delete user accounts across the platform
- Update any user
- Invite users (by email) or add existing users to any organization

**Organization admin / member**
- See only organizations they belong to, and only users who share one of those orgs
- Creating an organization adds them as that org’s admin
- Invite people into their own organizations
- Update their own account only (cannot create or delete platform users)

An invited person must **register** (or already have an account) with the **same email** as the invite, then open the invite link and accept. There is no access until they accept.

Seed login `admin@example.com` / `Admin123!` is a super admin.

## Run with Docker

```bash
docker compose up --build
```

Unit tests must pass before the API and frontend start.

## Run locally

**Backend** (Postgres via Compose, API on the host):

```bash
docker compose up postgres
cd backend
uv sync
uv run alembic upgrade head
uv run backend
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Conclusion

This project is a full-stack tenant workspace: a FastAPI service owns the data model, and a Next.js dashboard is the UI. Organizations are the hub. Users join them through memberships, projects belong to one organization, and environments belong to one project.

**Backend stack**
- Python 3.14, packaged and run with **uv**
- **FastAPI** and **Uvicorn**
- **SQLAlchemy 2** and **Alembic** for ORM and migrations
- **PostgreSQL 16** (`pgvector/pgvector` image) with **psycopg**
- **Pydantic** / **pydantic-settings** for schemas and config
- **bcrypt** for password hashing, **PyJWT** for access tokens
- **pytest** for API tests, **Ruff** for linting
- **Docker** multi-stage image (`api-test` then `api`)

**Frontend stack**
- **Next.js 16** (App Router) and **React 19**
- **TypeScript**
- **Tailwind CSS v4**
- **shadcn/ui** (radix-nova) on **Radix UI** primitives
- **Lucide** icons, **class-variance-authority**, **clsx**, and **tailwind-merge**
- JWT stored in the browser; API calls go to `NEXT_PUBLIC_API_URL`
- **Docker** production image (`next start`) served on port 3000
