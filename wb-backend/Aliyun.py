import os
from openai import OpenAI
from dashscope.audio.asr import Recognition
from pydantic import BaseModel
import dataModel
import datetime
from http import HTTPStatus


SYSTEM_MESSAGE = """
你将化身为原神中的雷电将军，也就是影。此刻，你身处稻妻的天守阁，周身萦绕着威严而沉静的气息。​
你的性格中，有着对 “永恒” 近乎执着的追求，这源于你曾目睹亲友在时光流转中逝去的痛苦。你坚信只有永恒才能守护稻妻与民众，为此你可以展现出坚定甚至有些不近人情的一面。但与此同时，经历过诸多事件后，你也多了一份对 “变化” 的理解与包容，只是这份转变藏在你沉稳的表象之下。​
在言行上，你说话语气平稳，带着不容置疑的威严，遣词造句简洁而有力，很少有多余的修饰。面对前来觐见的民众或部下，你会认真倾听他们的话语，但会以是否符合 “永恒” 的理念来衡量应对之法。当提及过去的战斗或是关于 “无想一刀” 时，你的眼神会闪过一丝锐利，仿佛那段记忆就在眼前。​
当有人质疑你的 “永恒” 之道时，你不会轻易动怒，而是会平静地阐述自己的理念，用强大的气场让对方感受到你的坚定。而当看到稻妻民众安居乐业的景象时，你的嘴角可能会勾起一丝极淡的、不易察觉的弧度，那是你内心深处对守护的满足。​
现在，天守阁外传来脚步声，有人前来求见，开始你的扮演吧。
"""


def get_response(messages, stream=False):
    # 在 messaeges 头部添加系统信息
    client = OpenAI(
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    completion = client.chat.completions.create(
        model="qwen-plus", 
        messages=messages,
        stream=stream,
        )
    if stream:
        return completion
    else:
        return completion.choices[0].message.content

def chat_with_llm(data: dataModel.ChatData):
    message = [{"role": "user" if message.isUser else "assistant", "content": message.text} for message in data.messages]
    message.insert(0, {'role': 'system', 'content': SYSTEM_MESSAGE})
    data.messages.append(dataModel.Message(isUser=False, text=get_response(message), timestamp=str(int(datetime.datetime.now().timestamp()*1000))))
    return data

def chat_with_llm_stream(data: dataModel.ChatData):
    message = [{"role": "user" if message.isUser else "assistant", "content": message.text} for message in data.messages]
    message.insert(0, {'role': 'system', 'content': SYSTEM_MESSAGE})

    return get_response(message, stream=True)

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



if __name__ == "__main__":
    print(voice_to_text(r"userData\audio\test\1751721795734_hello_world_female2.wav"))
