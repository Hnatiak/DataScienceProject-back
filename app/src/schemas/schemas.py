import uuid
from typing import Dict, Hashable, List, Optional, Annotated, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, PastDate, PlainSerializer, Strict, conset, UUID4
# from pydantic_extra_types.phone_numbers import PhoneNumber
from src.entity.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=16)
    email: str
    password: str = Field(min_length=4, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str
    role: Role

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

class UserResponseAll(BaseModel):
    user: UserDb

    class Config:
        from_attributes = True

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr

class CommentResponseSchema(BaseModel):
    id: int
    user_id: int
    photo_id: int
    text: str
    created_at: datetime
    updated_at: datetime


class CommentNewSchema(BaseModel):
    photo_id: int
    text: str

class PhotoBase(BaseModel):   
    description: Optional[str] = Field(None, max_length=2200)
    # tags: Optional[set[str]] = conset(str, max_length=4)
    tags: Optional[conset(str, max_length=5)]


class TagBase(BaseModel):
    name: str

    class Config:
        from_attributes = True

# tags output format is controlled here
def tags_serializer(tags: TagBase) -> str:
    names = [f'#{tag.name}' for tag in tags]
    return " ".join(names)    

CustomStr = Annotated[List[TagBase], PlainSerializer(tags_serializer, return_type=str)]
UUIDString = Annotated[UUID4, PlainSerializer(lambda x: str(x), return_type=str)]
class PhotoResponse(PhotoBase):
    id: Annotated[UUID4, Strict(False)]
    #id: UUIDString
    created_at: datetime
    updated_at: datetime
    url: str
    # tags: list[TagBase]
    tags: CustomStr

    class Config:
        from_attributes = True


class PhotoTransform(BaseModel):
    ...
