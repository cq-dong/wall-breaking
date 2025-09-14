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
    image_base64: str | None = None
    image_type: str | None = None

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
        
        # 加载收藏数据
        try:
            with open(CHAT_DATA_PATH_ROOT + self.userId + '_favorites.json', 'r', encoding="utf-8") as f:
                self.favoriteData = json.load(f)
        except:
            self.favoriteData = []

    def __save_json(self):
        with open(CHAT_DATA_PATH_ROOT + self.userId + '.json', 'w', encoding="utf-8") as f:
            json.dump(self.historyData, f, indent=2)
    
    def __save_favorites(self):
        with open(CHAT_DATA_PATH_ROOT + self.userId + '_favorites.json', 'w', encoding="utf-8") as f:
            json.dump(self.favoriteData, f, indent=2)

    def get_history_list(self):
        history_data = []
        for id, messages in self.historyData.items():
            # 获取第一条用户消息作为标题
            title = "无标题"
            for msg in messages:
                if msg.get("isUser", False) and msg.get("text", "").strip():
                    title = msg["text"][:30] + ("..." if len(msg["text"]) > 30 else "")
                    break
            
            # 获取最后一条消息的时间戳
            last_timestamp = messages[-1].get("timestamp", id) if messages else id
            
            history_data.append({
                "id": id, 
                "title": title,
                "timestamp": last_timestamp,
                "message_count": len(messages)
            })
        
        # 按时间戳倒序排列（最新的在前面）
        history_data.sort(key=lambda x: int(x['timestamp']), reverse=True)
        return history_data

    def get_history_data(self, history_id: str):
        return self.historyData.get(history_id)
    
    def add_history(self, history_id: str, messages: list):
        self.historyData[history_id] = messages
        self.__save_json()
    
    def delete_history(self, history_id: str):
        if history_id in self.historyData:
            del self.historyData[history_id]
            self.__save_json()
            return True
        return False
    
    def clear_all_history(self):
        self.historyData = {}
        self.__save_json()
    
    def change_chat_in_history(self, history_id: str, message: Message, index: int):
        if(index == -1 or index >= len(self.historyData[history_id])):
            self.historyData[history_id].append(message.model_dump())
        else:
            self.historyData[history_id][index] = message.model_dump()
        self.__save_json()

    def save(self):
        self.__save_json()
    
    # 收藏相关方法
    def get_favorites(self):
        return self.favoriteData
    
    def add_favorite(self, history_id: str):
        if history_id not in self.favoriteData:
            self.favoriteData.append(history_id)
            self.__save_favorites()
            return True
        return False
    
    def remove_favorite(self, history_id: str):
        if history_id in self.favoriteData:
            self.favoriteData.remove(history_id)
            self.__save_favorites()
            return True
        return False
    
    def toggle_favorite(self, history_id: str):
        if history_id in self.favoriteData:
            self.favoriteData.remove(history_id)
            self.__save_favorites()
            return False
        else:
            self.favoriteData.append(history_id)
            self.__save_favorites()
            return True

    def __del__(self):
        self.__save_json()
        self.__save_favorites()
