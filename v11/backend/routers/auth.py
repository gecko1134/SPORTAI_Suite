"""
SportAI Suite v11 — Authentication
JWT-based login · Role-based access (admin, staff, viewer)
Default admin seeded on first run

Add to main.py:
    from routers.auth import router as auth_router
    app.include_router(auth_router)
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from database import get_db

# ── Config ─────────────────────────────────────────────────────────────────────

SECRET_KEY  = os.environ.get("JWT_SECRET", "nxs-sportai-v11-secret-change-in-prod-2025")
ALGORITHM   = "HS256"
TOKEN_EXPIRE_HOURS = 12

pwd_ctx  = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2   = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Default admin credentials (override via env vars in production)
DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "NXSsportai2025!")
DEFAULT_ADMIN_EMAIL    = os.environ.get("ADMIN_EMAIL",    "shaun.marline@gmail.com")


# ── ORM ────────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "sportai_users"

    id: Mapped[str]           = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str]     = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str]        = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str]         = mapped_column(String(20), default="viewer")   # admin | staff | viewer
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool]   = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic ───────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    full_name: Optional[str] = None
    expires_in: int   # seconds


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "viewer"


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str
    full_name: Optional[str]
    is_active: bool
    created_at: str


# ── Helpers ────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2), db: AsyncSession = Depends(get_db)) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise cred_exc
    except JWTError:
        raise cred_exc

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise cred_exc
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ── Router ─────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/seed-admin", summary="Seed default admin user (run once after alembic upgrade)")
async def seed_admin(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.execute(select(User).where(User.username == DEFAULT_ADMIN_USERNAME))
    if existing.scalar_one_or_none():
        return {"message": "Admin already exists", "username": DEFAULT_ADMIN_USERNAME, "seeded": False}

    admin = User(
        username=DEFAULT_ADMIN_USERNAME,
        email=DEFAULT_ADMIN_EMAIL,
        hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
        role="admin",
        full_name="Shaun Marline",
        is_active=True,
    )
    db.add(admin)
    await db.commit()
    return {
        "message": "Admin user created",
        "username": DEFAULT_ADMIN_USERNAME,
        "role": "admin",
        "seeded": True,
    }


@router.post("/token", response_model=Token, summary="Login — returns JWT access token")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    token = create_token({"sub": user.username, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        username=user.username,
        full_name=user.full_name,
        expires_in=TOKEN_EXPIRE_HOURS * 3600,
    )


@router.get("/me", summary="Get current logged-in user")
async def get_me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=user.id, username=user.username, email=user.email,
        role=user.role, full_name=user.full_name, is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


@router.post("/users", summary="Create a new user (admin only)")
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserOut:
    existing = await db.execute(select(User).where(User.username == payload.username))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Username already exists")

    user = User(
        username=payload.username, email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name, role=payload.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut(
        id=user.id, username=user.username, email=user.email,
        role=user.role, full_name=user.full_name, is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


@router.get("/users", summary="List all users (admin only)")
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[UserOut]:
    result = await db.execute(select(User).order_by(User.created_at))
    users = result.scalars().all()
    return [
        UserOut(id=u.id, username=u.username, email=u.email,
                role=u.role, full_name=u.full_name, is_active=u.is_active,
                created_at=u.created_at.isoformat())
        for u in users
    ]
