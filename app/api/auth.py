from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.user_store import create_user, get_user_by_email
from app.core.security_utils import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.models.user import UserCreate
from app.models.auth import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate):
    existing = get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = create_user(
        user.email,
        hash_password(user.password)
    )

    token = create_access_token({"sub": user_id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ✅ FIXED LOGIN
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    record = get_user_by_email(form_data.username)  # Swagger sends username field

    if not record:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, record["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": record["user_id"]})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
