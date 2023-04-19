from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str


class Follower(BaseModel):
    screen_name: str


# User DB model
class UserDB(BaseModel):
    id: int
    email: str
    hashed_password: str

    class Config:
        orm_mode = True


# Follower DB model
class FollowerDB(BaseModel):
    id: int
    user_id: int
    screen_name: str
    created_at: datetime

    class Config:
        orm_mode = True

