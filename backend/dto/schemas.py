from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    filename: str
