from datetime import datetime, UTC, timedelta
from jose import jwt, JWTError

# ⚠️ In production, move this to environment variable
SECRET_KEY = "CHANGE_ME_SUPER_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")
