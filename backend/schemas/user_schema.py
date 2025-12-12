from pydantic import BaseModel

class UserCreateSchema(BaseModel):
    plate: str
    country: str