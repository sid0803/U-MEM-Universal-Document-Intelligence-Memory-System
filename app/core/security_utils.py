# app/core/security_utils.py

from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def validate_ownership(entity: dict, user_id: str):
    """
    Ensures the given entity belongs to the requesting user.
    Raises 403 if ownership does not match.
    """

    if not entity:
        raise HTTPException(status_code=404, detail="Resource not found")

    if entity.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
