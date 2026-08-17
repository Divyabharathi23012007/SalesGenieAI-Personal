"""Authentication endpoints and dependencies for SalesGenie AI."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)
AUTH_SECRET = os.getenv("AUTH_SECRET", "")
TOKEN_TTL_SECONDS = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "28800"))


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=1, max_length=128)


def _password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def _normalise_email(value: str) -> str:
    email = value.strip().lower()
    # This intentionally small validation avoids an additional runtime dependency
    # while rejecting malformed input before it reaches the database.
    if email.count("@") != 1 or email.startswith("@") or email.endswith("@") or "." not in email.rsplit("@", 1)[1]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Enter a valid email address.")
    return email


def _verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    try:
        algorithm, salt_b64, digest_b64 = stored_hash.split("$", 2)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _secret() -> bytes:
    if not AUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured. Add AUTH_SECRET to the backend .env file.",
        )
    return AUTH_SECRET.encode("utf-8")


def _encode_token(user_id: int) -> str:
    payload = json.dumps({"sub": user_id, "exp": int(time.time()) + TOKEN_TTL_SECONDS}, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(_secret(), encoded, hashlib.sha256).digest()
    return f"{encoded.decode()}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def _decode_token(token: str) -> int:
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        if not hmac.compare_digest(supplied, expected):
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if int(payload["exp"]) < time.time():
            raise ValueError("expired")
        return int(payload["sub"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired. Please sign in again.")


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    user = db.get(User, _decode_token(credentials.credentials))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user


def user_response(user: User) -> dict:
    return {"user_id": user.user_id, "name": user.name, "email": user.email, "role": user.role}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = _normalise_email(payload.email)
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
    user = User(name=payload.name.strip(), email=email, password_hash=_password_hash(payload.password), role="Member")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": _encode_token(user.user_id), "token_type": "bearer", "user": user_response(user)}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == _normalise_email(payload.email)).first()
    if not user or not _verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")
    return {"access_token": _encode_token(user.user_id), "token_type": "bearer", "user": user_response(user)}


@router.get("/me")
def me(user: User = Depends(current_user)):
    return user_response(user)
