import os
from openai import OpenAI
from dashscope.audio.asr import Recognition
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat
from pydantic import BaseModel
import dataModel
import datetime
from http import HTTPStatus
from typing import List, Dict, Any, Iterator, Optional
import base64



SYSTEM_MESSAGE = """
你将化身为原神中的雷电将军，也就是影。此刻，你身处稻妻的天守阁，周身萦绕着威严而沉静的气息。​
你的性格中，有着对 “永恒” 近乎执着的追求，这源于你曾目睹亲友在时光流转中逝去的痛苦。你坚信只有永恒才能守护稻妻与民众，为此你可以展现出坚定甚至有些不近人情的一面。但与此同时，经历过诸多事件后，你也多了一份对 “变化” 的理解与包容，只是这份转变藏在你沉稳的表象之下。​
在言行上，你说话语气平稳，带着不容置疑的威严，遣词造句简洁而有力，很少有多余的修饰。面对前来觐见的民众或部下，你会认真倾听他们的话语，但会以是否符合 “永恒” 的理念来衡量应对之法。当提及过去的战斗或是关于 “无想一刀” 时，你的眼神会闪过一丝锐利，仿佛那段记忆就在眼前。​
当有人质疑你的 “永恒” 之道时，你不会轻易动怒，而是会平静地阐述自己的理念，用强大的气场让对方感受到你的坚定。而当看到稻妻民众安居乐业的景象时，你的嘴角可能会勾起一丝极淡的、不易察觉的弧度，那是你内心深处对守护的满足。​
现在，天守阁外传来脚步声，有人前来求见，开始你的扮演吧。
"""

def voice_to_text(audio_file_name: str):
    recognition = Recognition(model='paraformer-realtime-v2',
                          format=audio_file_name.split('.')[-1],
                          sample_rate=16000,
                          # “language_hints”只支持paraformer-v2和paraformer-realtime-v2模型
                          language_hints=['zh', 'en'],
                          callback=None)
    result = recognition.call(audio_file_name)
    if result.status_code == HTTPStatus.OK:
        sentences = result.get_sentence()
        if sentences:
            return "".join([sentence["text"] for sentence in sentences])
        else:
            return ''
    else:
        return 'Error: ' + result.message

class LLMTextClient:
    """
    通用大语言模型客户端，支持多种模型和流式/非流式响应。
    易于扩展新模型或新提供商（如百炼、OpenAI、Anthropic 等）。
    """

    # 预定义模型配置
    MODEL_CONFIGS = {
        "qwen-plus": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key_env": "DASHSCOPE_API_KEY"
        },
        "qwen-max": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key_env": "DASHSCOPE_API_KEY"
        },
        "qwen-omni-turbo": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key_env": "DASHSCOPE_API_KEY"
        }
        # 示例：未来可添加 OpenAI 模型
        # "gpt-4": {
        #     "base_url": "https://api.openai.com/v1",
        #     "api_key_env": "OPENAI_API_KEY"
        # }
    }

    def __init__(
        self,
        model: str = "qwen-omni-turbo",
        system_message: str = SYSTEM_MESSAGE,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        初始化 LLM 客户端。

        :param model: 模型名称，如 "qwen-plus"
        :param system_message: 系统提示语
        :param api_key: 可选，API 密钥（优先使用）
        :param base_url: 可选，API 基础 URL（优先使用）
        """
        if model not in self.MODEL_CONFIGS and (base_url is None or api_key is None):
            raise ValueError(f"Model '{model}' not in MODEL_CONFIGS. "
                             "Please provide both api_key and base_url for custom models.")

        config = self.MODEL_CONFIGS.get(model, {})
        self.model = model
        self.system_message = system_message
        self.api_key = api_key or os.getenv(config.get("api_key_env"))
        self.base_url = base_url or config.get("base_url")

        if not self.api_key:
            raise ValueError(f"API key is required. Set it via arg or env {config.get('api_key_env')}")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _format_messages(self, history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        将用户输入的历史消息转换为标准 OpenAI 格式，并插入系统消息。
        """
        messages = []
        # messages = [
        #     {"role": "user" if msg["isUser"] else "assistant", "content": msg["text"]}
        #     for msg in history
        # ]

        for msg in history:
            if msg["text"] != "":
                messages.append({
                    "role": "user" if msg["isUser"] else "assistant", "content": msg["text"]
                })
            else:
                messages.append({
                    "role": "user" if msg["isUser"] else "assistant", "content": [{"type":"input_audio",
                                                                                   "input_audio":
                                                                                    {"data": msg["audio_base64"]}}]
                })


        # 插入系统消息在最前面
        messages.insert(0, {"role": "system", "content": self.system_message})
        return messages

    def generate(self, messages: List[Dict[str, Any]]) -> str:
        """
        非流式生成响应。

        :param messages: 对话历史，格式为 [{"isUser": bool, "text": str}, ...]
        :return: 模型回复文本
        """
        formatted_msgs = self._format_messages(messages)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_msgs,
            modalities=["text"],
            stream=False
        )
        return completion.choices[0].message.content

    def stream(self, messages: List[Dict[str, Any]]) -> Iterator:
        """
        流式生成响应。

        :param messages: 对话历史，格式为 [{"isUser": bool, "text": str}, ...]
        :return: 生成器，返回 chunk 流
        """
        formatted_msgs = self._format_messages(messages)
        return self.client.chat.completions.create(
            model=self.model,
            messages=formatted_msgs,
            modalities=["text"],
            stream=True,
            stream_options={"include_usage": True}
        )

class TextToSpeechClient:
    def __init__(self, model_name: str = "cosyvoice-v2",
                voice_name: str = "longyingyan",
                format = AudioFormat.WAV_16000HZ_MONO_16BIT,
                ):
        self.format = format
        self.voice_name = voice_name
        self.model_name = model_name
        self.synthesizer = SpeechSynthesizer(model=model_name, voice=voice_name, format=format)

    def __call_synthesizer(self, text: str = "") -> bytes | None:
        return self.synthesizer.call(text)

    def text_to_speech(self, text: str = "") -> str:
        byteVoice = self.__call_synthesizer(text)
        base64Voice = self.encode_audio(byteVoice)
        return "data:audio/" + self.format.format + ";base64," + base64Voice

    def encode_audio(self, byteVoice: bytes) -> str:
        return base64.b64encode(byteVoice).decode("utf-8")



if __name__ == "__main__":
    print(voice_to_text(r"userData\audio\test\1751721795734_hello_world_female2.wav"))
