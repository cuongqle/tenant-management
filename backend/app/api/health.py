from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/")
async def root() -> dict[str, str]:
    return {"name": "Tenant Management API", "version": "0.1.0"}