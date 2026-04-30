from pydantic import BaseModel, Field
from uuid import UUID

class POST_chat(BaseModel):
    session_id: UUID
    message:    str

# log in
class LoginRequest(BaseModel):
    username: str
    password: str