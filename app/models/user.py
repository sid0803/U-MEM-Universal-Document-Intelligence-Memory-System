from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    user_id: str
    email: EmailStr
