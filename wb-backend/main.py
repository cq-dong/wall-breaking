from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import datetime
import asyncio
import os
import base64
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis

import dataModel
import ChatLLM
# import wb_audio  # 暂时注释掉音频功能以解决Python 3.13兼容性问题


import os


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

@app.get("/")
async def root():
    return {"message": "Wall Breaking Backend API is running", "status": "ok"}

@app.get("/api/chat/{user_id}/{history_id}")
async def chat(user_id: str, history_id: str):
    chatdb = dataModel.ChatHistoryJsonDB(user_id)
    messages = chatdb.get_history_data(history_id)
    return dataModel.ChatData(history_id=history_id, messages=messages, user_id=user_id)

@app.post("/api/chat/{user_id}/{history_id}")
async def save_chat(user_id: str, history_id: str, chat_data: dataModel.ChatData):
    """保存对话数据"""
    try:
        return {"success": True, "message": "对话保存成功"}
    except Exception as e:
        return {"success": False, "message": f"保存失败: {str(e)}"}

@app.websocket("/ws/chat/")
async def chat_ws(ws: WebSocket):
    full_content = ""
    await ws.accept()
    data = await ws.receive_json()
    chat_data = dataModel.ChatData(**data).model_dump()
    
    # 获取前端传来的system_prompt，如果没有则使用默认值
    system_prompt = data.get('system_prompt', None)
    
    # 检查是否有图像消息，如果有则使用支持视觉的模型
    has_image = any(msg.get('image_base64') for msg in chat_data["messages"])
    model_name = "qwen-vl-max-latest" if has_image else "qwen-omni-turbo"
    
    llm_client = ChatLLM.LLMTextClient(model=model_name)
    t_to_vioce = ChatLLM.TextToSpeechClient()
    # 使用 LLMClient 的 stream 方法，传入自定义的system_prompt
    completion = llm_client.stream(chat_data["messages"], system_prompt=system_prompt)
    
    # 插入系统消息前，确保 messages 格式正确
    chat_data["messages"].append({"isUser": False, "text": "", "timestamp": now_time()})

    for chunk in completion:  # 注意：这里假设 completion 是异步生成器，如果不是，请根据实际情况调整
        if hasattr(chunk, 'choices') and chunk.choices:
            delta_content = chunk.choices[0].delta.content or ""
            full_content += delta_content
            # 更新最后一次的消息内容
            chat_data["messages"][-1]["text"] = full_content
            # 确保发送的数据包含完整的消息历史，包括图片信息
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

@app.delete("/api/chat_history/{user_id}/{history_id}")
async def delete_chat_history(user_id: str, history_id: str):
    chatdb = dataModel.ChatHistoryJsonDB(user_id)
    success = chatdb.delete_history(history_id)
    return {"success": success, "message": "历史记录删除成功" if success else "历史记录不存在"}

@app.delete("/api/chat_history_all/{user_id}")
async def clear_all_chat_history(user_id: str):
    chatdb = dataModel.ChatHistoryJsonDB(user_id)
    chatdb.clear_all_history()
    return {"success": True, "message": "所有历史记录已清空"}

@app.get("/api/favorites/{user_id}")
async def get_favorites(user_id: str):
    chatdb = dataModel.ChatHistoryJsonDB(user_id)
    favorites = chatdb.get_favorites()
    return {"favorites": favorites}

@app.post("/api/favorite/{user_id}/{history_id}")
async def toggle_favorite(user_id: str, history_id: str):
    chatdb = dataModel.ChatHistoryJsonDB(user_id)
    is_favorited = chatdb.toggle_favorite(history_id)
    return {
        "success": True, 
        "is_favorited": is_favorited,
        "message": "已收藏" if is_favorited else "已取消收藏"
    }

@app.post("/api/image-generation")
async def image_generation(request: dict):
    try:
        prompt = request.get('prompt', '')
        print(f"Received request: {request}")
        import sys
        sys.stdout.flush()
        if not prompt:
            return {"error": "Prompt is required"}
        
        print(f"Generating image with prompt: {prompt}")
        sys.stdout.flush()
        
        # 调用阿里云百炼图像生成API
        api_key = os.getenv("DASHSCOPE_API_KEY")
        print(f"Using API key: {api_key[:10]}..." if api_key else "No API key found")
        sys.stdout.flush()
        
        rsp = ImageSynthesis.call(
            api_key=api_key,
            model="qwen-image",
            prompt=prompt,
            n=1,
            size='1024*1024',
            prompt_extend=True,
            watermark=False
        )
        
        print(f"API response status: {rsp.status_code}")
        print(f"API response type: {type(rsp)}")
        print(f"API response attributes: {dir(rsp)}")
        print(f"Full API response: {rsp}")
        sys.stdout.flush()
        
        # 打印完整的响应内容
        if hasattr(rsp, '__dict__'):
            print(f"Response dict: {rsp.__dict__}")
        if hasattr(rsp, 'output'):
            print(f"Response output dict: {rsp.output.__dict__ if hasattr(rsp.output, '__dict__') else rsp.output}")
        sys.stdout.flush()
        
        if rsp.status_code == HTTPStatus.OK:
            print(f"Response output: {rsp.output}")
            print(f"Response output type: {type(rsp.output)}")
            
            # 检查输出结构
            if hasattr(rsp.output, 'results') and len(rsp.output.results) > 0:
                # 获取生成的图像URL
                image_url = rsp.output.results[0].url
                print(f"Image URL: {image_url}")
                
                # 下载图像并转换为base64
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_base64 = base64.b64encode(response.content).decode('utf-8')
                    print(f"Successfully generated image, base64 length: {len(image_base64)}")
                    return {
                        "success": True,
                        "image_base64": image_base64,
                        "image_type": "image/png",
                        "prompt": prompt
                    }
                else:
                    return {"error": f"Failed to download generated image, status: {response.status_code}"}
            else:
                print(f"No results found. Output structure: {rsp.output}")
                return {"error": f"No results in API response. Output: {rsp.output}"}
        else:
            print(f"API call failed with status: {rsp.status_code}")
            print(f"Error code: {getattr(rsp, 'code', 'Unknown')}")
            print(f"Error message: {getattr(rsp, 'message', 'Unknown')}")
            return {
                "error": f"Image generation failed: {getattr(rsp, 'message', 'Unknown error')}",
                "status_code": rsp.status_code,
                "code": getattr(rsp, 'code', 'Unknown')
            }
    except Exception as e:
        print(f"Exception in image generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Image generation error: {str(e)}"}


# 暂时注释掉音频功能
# async def audio_save(audio_file: UploadFile, userId: str, historyId: str) -> str:
#     # Validate content type
#     allowed_types = ['audio/wav', 'audio/mpeg', 'audio/ogg']
#     if audio_file.content_type not in allowed_types:
#         return {"error": f"Invalid file type. Allowed types: {', '.join(allowed_types)}"}
#     
#     # Save the uploaded audio file
#     upload_dir = AUDIO_DATA_PATH_ROOT + userId
#     os.makedirs(upload_dir, exist_ok=True)
#     file_name = f"{historyId}_{now_time()}.{audio_file.filename.split('.')[-1]}"
#     file_path = os.path.join(upload_dir, file_name)
#     with open(file_path, "wb") as buffer:
#         buffer.write(await audio_file.read())
#     try:
#         if(wb_audio.audio_length(file_path) > 60):
#             raise Exception("Audio length is too long")
#         if(wb_audio.get_audio_track_count(file_path) > 1):
#             audio_file = wb_audio.merge_audio_tracks(file_path)
#             audio_file.export(file_path, format="wav")
#     except Exception as e:
#         os.remove(file_path)
#         raise e
#     return file_path, file_name

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

