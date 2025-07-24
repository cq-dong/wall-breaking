from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import datetime
import asyncio
import os

import dataModel
import Aliyun
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
    with open(CHAT_DATA_PATH_ROOT + user_id + '.json', 'r', encoding="utf-8") as f:
        messages = json.load(f)[history_id]
    return dataModel.ChatData(history_id=history_id, messages=messages, user_id=user_id)

@app.websocket("/ws/chat/")
async def chat_ws(ws: WebSocket):
    full_content = ""
    await ws.accept()
    data = await ws.receive_json()
    chat_data = dataModel.ChatData(**data)
    completion = Aliyun.chat_with_llm_stream(chat_data)
    chat_data.messages.append(dataModel.Message(isUser=False, text=full_content, timestamp=now_time()))
    for chunk in completion:
        if chunk.choices:
            full_content += chunk.choices[0].delta.content
            chat_data.messages[-1].text = full_content
        await ws.send_json(chat_data.model_dump())
    await ws.close()
    save_chater_data(chat_data)

@app.get("/api/chat_history_list/{user_id}")
async def chat_history(user_id: str):
    history_data = []
    try:
        with open(CHAT_DATA_PATH_ROOT + user_id + '.json', 'r', encoding="utf-8") as f:
            chat_data = json.load(f)
    except:
        return []
    for id, messages in chat_data.items():
        history_data.append({"id": id, "title": messages[0]["text"]})
    return history_data

@app.post("/api/audio-chat-append/{user_id}/{history_id}")
async def audio_chat_append(user_id: str, history_id: str, 
                     audio_file: UploadFile = File(...)):
    file_path, file_name = await audio_save(audio_file, user_id, history_id)
    user_text = Aliyun.voice_to_text(file_path)
    try:
        with open(AUDIO_DATA_PATH_ROOT + user_id + '.json', 'r', encoding="utf-8") as f:
            chat_file_data = json.load(f)
    except:
        chat_file_data = {}
    try:
        chat_file_data[history_id].append(dataModel.Message(text=user_text, isUser=True, timestamp=now_time(), audio_file=file_name))
    except KeyError:
        chat_file_data[history_id] = [dataModel.Message(text=user_text, isUser=True, timestamp=now_time(), audio_file=file_name)]
    
    chat_data = dataModel.ChatData(user_id=user_id, history_id=history_id, messages=chat_file_data[history_id])

    completion = Aliyun.chat_with_llm_stream(chat_data)

    full_content = ""
    chat_data.messages.append(dataModel.Message(isUser=False, text=full_content, timestamp=now_time()))
    for chunk in completion:
        if chunk.choices:
            full_content += chunk.choices[0].delta.content
            chat_data.messages[-1].text = full_content

    save_chater_data(chat_data, AUDIO_DATA_PATH_ROOT)

    return dataModel.ChatData(history_id=history_id, messages=chat_file_data[history_id], user_id=user_id)

@app.post("/api/image-generation")
async def image_generation():
    return {"response": "Image generation endpoint"}

def save_chater_data(chat_data: dataModel.ChatData, path_root:str=CHAT_DATA_PATH_ROOT):
    userId = chat_data.user_id  
    historyId = chat_data.history_id

    chat_data_dict = chat_data.model_dump()
    try:
        with open(path_root + userId + '.json', 'r', encoding="utf-8") as f:
            history_data = json.load(f)
    except:
        history_data = {}
    history_data[historyId] = chat_data_dict["messages"]
    with open(path_root + userId + '.json', 'w', encoding="utf-8") as f:
        json.dump(history_data, f, indent=2)

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
