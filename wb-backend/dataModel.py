from pydantic import BaseModel, FilePath

# file : user_id - {history_id - str : messages - [{text: str, isUser: bool, timestamp: str}]}, ...]}

class Message(BaseModel):
    text: str
    isUser: bool
    timestamp: str
    audio_file: str | None = None

class ChatData(BaseModel):
    user_id: str
    history_id: str
    messages: list[Message]
