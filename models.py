from pydantic import BaseModel

class TikTokCredentials(BaseModel):
    username: str
    password: str

class Message(BaseModel):
    sender: str
    content: str
    timestamp: str
