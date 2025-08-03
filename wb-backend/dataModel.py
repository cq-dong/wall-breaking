from pydantic import BaseModel, FilePath
from sqlmodel import Field, Session, SQLModel, create_engine, select
import json

# file : user_id - {history_id - str : messages - [{text: str, isUser: bool, timestamp: str}]}, ...]}

USER_DATA_PATH_ROOT = 'userData/'
AUDIO_DATA_PATH_ROOT = USER_DATA_PATH_ROOT + 'audio/'
IMAGE_DATA_PATH_ROOT = USER_DATA_PATH_ROOT + 'image/'
CHAT_DATA_PATH_ROOT = USER_DATA_PATH_ROOT + 'chat/'

class Message(BaseModel):
    text: str | None = ""
    isUser: bool
    timestamp: str
    audio_base64: str | None = None

class ChatData(BaseModel):
    user_id: str
    history_id: str
    messages: list[Message]


# 与Json对话数据文件交互
class ChatHistoryJsonDB:
    def __init__(self, user_id: str):
        self.userId = user_id
        try: 
            with open(CHAT_DATA_PATH_ROOT + self.userId + '.json', 'r', encoding="utf-8") as f:
                self.historyData = json.load(f)
        except:
            self.historyData = {}

    def __save_json(self):
        with open(CHAT_DATA_PATH_ROOT + self.userId + '.json', 'w', encoding="utf-8") as f:
            json.dump(self.historyData, f, indent=2)

    def get_history_list(self):
        history_data = []
        for id, messages in self.historyData.items():
            history_data.append({"id": id, "title": messages[0]["text"] if messages[0]["text"] != "" else "无标题" })
        history_data.sort(key=lambda x: x['id'])
        return history_data

    def get_history_data(self, history_id: str):
        return self.historyData.get(history_id)
    
    def add_history(self, history_id: str, messages: list):
        self.historyData[history_id] = messages
        self.__save_json()
    
    def change_chat_in_history(self, history_id: str, message: Message, index: int):
        if(index == -1 or index >= len(self.historyData[history_id])):
            self.historyData[history_id].append(message.model_dump())
        else:
            self.historyData[history_id][index] = message.model_dump()
        self.__save_json()

    def save(self):
        self.__save_json()

    def __del__(self):
        self.__save_json()
