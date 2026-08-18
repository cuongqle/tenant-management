import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    environments,
    health,
    organization_members,
    organizations,
    projects,
    users,
)
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

API_V1_PREFIX = "/api/v1"
protected = [Depends(get_current_user)]

app = FastAPI(
    title="Tenant Management API",
    version="0.1.0",
    description="API for managing tenants",
    docs_url="/docs",
    redoc_url="/redoc",
)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(organizations.router, prefix=API_V1_PREFIX, dependencies=protected)
app.include_router(users.router, prefix=API_V1_PREFIX, dependencies=protected)
app.include_router(projects.router, prefix=API_V1_PREFIX, dependencies=protected)
app.include_router(environments.router, prefix=API_V1_PREFIX, dependencies=protected)
app.include_router(organization_members.router, prefix=API_V1_PREFIX, dependencies=protected)


def main() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
