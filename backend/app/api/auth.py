from fastapi import APIRouter, HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def _token_for(user: User) -> TokenResponse:
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email},
    )
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, users: UserRepository) -> TokenResponse:
    user = users.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_for(user)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, users: UserRepository) -> TokenResponse:
    if users.get_by_email(payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = users.create(
        {
            "email": str(payload.email),
            "name": payload.name,
            "password": hash_password(payload.password),
        }
    )
    return _token_for(user)
