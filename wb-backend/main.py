from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import datetime
import asyncio
import os
import base64

import dataModel
import ChatLLM
import wb_audio

USER_DATA_PATH_ROOT = 'userData/'
AUDIO_DATA_PATH_ROOT = USER_DATA_PATH_ROOT + 'audio/'
IMAGE_DATA_PATH_ROOT = USER_DATA_PATH_ROOT + 'image/'
CHAT_DATA_PATH_ROOT = USER_DATA_PATH_ROOT + 'chat/'

app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def now_time() -> str:
    return str(int(datetime.datetime.now().timestamp()*1000))

@app.get("/api/chat/{user_id}/{history_id}")
async def chat(user_id: str, history_id: str):
    chatdb = dataModel.ChatHistoryJsonDB(user_id)
    messages = chatdb.get_history_data(history_id)
    return dataModel.ChatData(history_id=history_id, messages=messages, user_id=user_id)

@app.websocket("/ws/chat/")
async def chat_ws(ws: WebSocket):
    full_content = ""
    await ws.accept()
    data = await ws.receive_json()
    chat_data = dataModel.ChatData(**data).model_dump()
    llm_client = ChatLLM.LLMTextClient()
    t_to_vioce = ChatLLM.TextToSpeechClient()
    # 使用 LLMClient 的 stream 方法代替旧的 chat_with_llm_stream 函数
    completion = llm_client.stream(chat_data["messages"])
    
    # 插入系统消息前，确保 messages 格式正确
    chat_data["messages"].append({"isUser": False, "text": "", "timestamp": now_time()})

    for chunk in completion:  # 注意：这里假设 completion 是异步生成器，如果不是，请根据实际情况调整
        if hasattr(chunk, 'choices') and chunk.choices:
            delta_content = chunk.choices[0].delta.content or ""
            full_content += delta_content
            # 更新最后一次的消息内容
            chat_data["messages"][-1]["text"] = full_content
            await ws.send_json(chat_data)

    chat_data["messages"][-1]["audio_base64"] = t_to_vioce.text_to_speech(full_content)
    await ws.send_json(chat_data)
    
    await ws.close()
    
    # 保存聊天记录到数据库
    chatdb = dataModel.ChatHistoryJsonDB(chat_data["user_id"])
    chatdb.add_history(chat_data["history_id"], chat_data["messages"])

@app.get("/api/chat_history_list/{user_id}")
async def chat_history(user_id: str):
    chatdb = dataModel.ChatHistoryJsonDB(user_id)
    history_data = chatdb.get_history_list()
    return history_data

@app.post("/api/image-generation")
async def image_generation():
    return {"response": "Image generation endpoint"}


async def audio_save(audio_file: UploadFile, userId: str, historyId: str) -> str:
    # Validate content type
    allowed_types = ['audio/wav', 'audio/mpeg', 'audio/ogg']
    if audio_file.content_type not in allowed_types:
        return {"error": f"Invalid file type. Allowed types: {', '.join(allowed_types)}"}
    
    # Save the uploaded audio file
    upload_dir = AUDIO_DATA_PATH_ROOT + userId
    os.makedirs(upload_dir, exist_ok=True)
    file_name = f"{historyId}_{now_time()}.{audio_file.filename.split('.')[-1]}"
    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, "wb") as buffer:
        buffer.write(await audio_file.read())
    try:
        if(wb_audio.audio_length(file_path) > 60):
            raise Exception("Audio length is too long")
        if(wb_audio.get_audio_track_count(file_path) > 1):
            audio_file = wb_audio.merge_audio_tracks(file_path)
            audio_file.export(file_path, format="wav")
    except Exception as e:
        os.remove(file_path)
        raise e
    return file_path, file_name

