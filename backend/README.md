# Tenant Management API

FastAPI backend for organizations, users, projects, and environments.

```bash
uv sync
uv run alembic upgrade head
uv run backend
```

API docs: http://localhost:8000/docs

## Conclusion

The backend is a Python 3.14 service managed with **uv**. It exposes a **FastAPI** / **Uvicorn** API, persists data with **SQLAlchemy 2**, **Alembic**, and **PostgreSQL** (**psycopg**), validates with **Pydantic**, hashes passwords with **bcrypt**, and issues **JWT** access tokens. Tests run with **pytest**.

The matching UI is the Next.js app in `../frontend` (React 19, TypeScript, Tailwind v4, shadcn/ui). See the [project README](../README.md) for the full stack list.
