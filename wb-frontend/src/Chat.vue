<template>
  <div class="chat-container">
    <div class="section">
      <h2>动漫对话——请开始与你心仪对象对话吧~</h2>
      <div class="chat-scoop">
        <div class="chat-history">
          <h3>历史记录</h3>
          <button class="send-button" @click="newChat">新对话</button>
          <div class="history-list">
            <div v-for="item in chatHistroy" class="history-items" @click="selectHistory(item.id)">
              {{ item.title }}
            </div>
          </div>
        </div>
        <div class="chat-section">
          <div class="chat-messages" ref="chatMessages">
            <ChatMessage 
              v-for="(message, index) in messages" 
              :key="index"
              :message="message" />
          </div>
          <form @submit.prevent="sendMessage" class="chat-input-form">
            <textarea v-model="userInput" type="text" placeholder="输入您的消息..." class="chat-input" required></textarea>
            <button type="submit" class="send-button">发送</button>
          </form>
          <VoiceRecorder @finish-record="handleRecordFinish"/>
        </div>
      </div>
    </div>
    <div class="section audio-section">
      <h2>音频克隆区</h2>
      <form @submit.prevent="uploadAudio" class="upload-form">
        <input type="file" accept="audio/*" @change="handleAudioFileChange" class="file-input">
        <button type="submit" class="upload-button">上传音频</button>
      </form>
      <div v-if="audioResult" class="result-audio">
        <audio :src="audioResult" controls></audio>
      </div>
    </div>

    <div class="section image-section">
      <h2>图片生成区</h2>
      <form @submit.prevent="uploadImage" class="upload-form">
        <input type="file" accept="image/*" @change="handleImageFileChange" class="file-input">
        <button type="submit" class="upload-button">上传图片</button>
      </form>
      <div v-if="imageResult" class="result-image">
        <img :src="imageResult" alt="生成的图片">
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import ChatMessage from './components/ChatMessage.vue';
import VoiceRecorder from './components/VoiceRecorder.vue';
import { Marked } from 'marked';
import { markedHighlight } from "marked-highlight";
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css'; // 或其他你喜欢的主题

const marked = new Marked(
  markedHighlight({
    emptyLangClass: 'hljs',
    langPrefix: 'hljs language-',
    highlight(code, lang, info) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    }
  })
);
// Chat section
const messages = ref([]);
const userInput = ref('');
const chatMessages = ref(null);
const chatHistroy = ref([]);

const Domain = "127.0.0.1:8000"

const apiDomain = "http://" + Domain;  // Set the API domain
const wsDomain = "ws://" + Domain;

const chatId = ref(String(Date.now()));
const audioChatId = ref(String(Date.now()));

let userName = localStorage.getItem('username');
if (!userName) {
  userName = 'test_username';
  localStorage.setItem('username', userName);
}
let chat_ws = null;
const audioBase64String = ref(null);
const handleRecordFinish = async (base64String) => {
  audioBase64String.value = base64String;
  await sendMessage();
};

const sendMessage = async () => {
  // let username = localStorage.getItem('username');
  if (!userInput.value.trim() && !audioBase64String.value) return;

  // Add user message to chat
  messages.value.push({ text: userInput.value, isUser: true, 
    timestamp: String(Date.now()), 
    audio_base64: audioBase64String.value });
  audioBase64String.value= null;
  // Clear input
  var userInputValue = userInput.value;
  userInput.value = '';

  // Scroll to bottom
  scrollToBottom();

  try {
    chat_ws = new WebSocket(wsDomain + "/ws/chat/");

    chat_ws.onopen = function () {
      chat_ws.send(JSON.stringify({ user_id: userName, history_id: chatId.value, messages: messages.value }));
      scrollToBottom();
    };

    chat_ws.onmessage = function (event) {
      messages.value = JSON.parse(event.data).messages;
      scrollToBottom();
    };

    chat_ws.onerror = function (error) {
      console.error('WebSocket Error:', error);
    };

    chat_ws.onclose = function () {
      console.log('WebSocket connection closed');
      refreshHistory();
    };
  } catch (error) {
    console.error('Error sending message:', error);
    messages.value.push({ text: '抱歉，发生错误，请重试。', isUser: false, timestamp: String(Date.now()) });
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight;
    }
  });
};

const refreshHistory = async () => {
  try {
    await fetch(`${apiDomain}/api/chat_history_list/${userName}`)
      .then(response => response.json())
      .then(data => {
        chatHistroy.value = data;
        scrollToBottom();
      })
      .catch(error => {
        console.error('Error fetching history:', error);
      });
  }
  catch (error) {
    console.error('Error fetching history:', error);
  }
};
refreshHistory();

const selectHistory = async (historyId) => {
  try {
    await fetch(`${apiDomain}/api/chat/${userName}/${historyId}`)
      .then(response => response.json())
      .then(data => {
        messages.value = data.messages;
        chatId.value = data.history_id;
        scrollToBottom();
      })
      .catch(error => {
        console.error('Error fetching history:', error);
      });
  }
  catch (error) {
    console.error('Error choosing history:', error);
  }

};

const newChat = async () => {
  chatId.value = String(Date.now());
  messages.value = [];
};

// Audio section
const audioFile = ref(null);
const audioResult = ref(null);

const handleAudioFileChange = (event) => {
  audioFile.value = event.target.files[0];
};

const uploadAudio = async () => {
  if (!audioFile.value) return;

  const formData = new FormData();
  formData.append('audio_file', audioFile.value);

  try {
    // Call backend API with the new domain and proper headers
    const response = await fetch(`${apiDomain}/api/audio-chat-append/${userName}/${audioChatId.value}`, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    // Set the result audio URL
    audioResult.value = data.audioUrl;
  } catch (error) {
    console.error('Error uploading audio:', error);
  }
};

// Image section
const imageFile = ref(null);
const imageResult = ref(null);

const handleImageFileChange = (event) => {
  imageFile.value = event.target.files[0];
};

const uploadImage = async () => {
  if (!imageFile.value) return;

  const formData = new FormData();
  formData.append('image', imageFile.value);

  try {
    // Call backend API with the new domain and proper headers
    const response = await fetch(`${apiDomain}/api/image-generation`, {
      method: 'POST',
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST'
      },
      body: formData
    });

    const data = await response.json();

    // Set the result image URL
    imageResult.value = data.imageUrl;
  } catch (error) {
    console.error('Error uploading image:', error);
  }
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Check if this cookie string begins with the name we want
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

};
</script>

<style scoped>
.chat-container {
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
}

.section {
  margin-bottom: 3rem;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.chat-scoop {
  display: flex;
  flex-direction: row;
  height: 80vh;
}

.chat-section {
  display: flex;
  flex: 0 1 90%;
  flex-direction: column;
  gap: 1.5rem;
  /* 固定高度为页面高度的80% */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e4e4e4;
  border-radius: 4px;
  padding: 1rem;
  height: 100%;
  /* 填满父容器 */
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  /* background-image: url('./assets/leidianying.png'); */
  background-repeat: repeat;
  background-position: top;
  background-attachment: scroll;
}

.chat-history {
  flex: 0 0 25%;
  max-width: 10cm;
  overflow-y: auto;
  border: 1px solid #e4e4e4;
  border-radius: 4px;
  padding: 1rem;
  /* 填满父容器 */
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-list{
  overflow-y: auto;
  overflow-x: hidden;
}

.history-items {
  padding: 0.6rem;
  margin-bottom: 0.5rem;
  background-color: #ffffff;
  border-left: 4px solid #42b983;
  border-radius: 4px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  align-items: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.history-items:hover {
  background-color: #f0f0f0;
  transform: translateX(4px);
}

.history-items:active {
  background-color: #e0e0e0;
}

.chat-input-form {
  display: flex;
  gap: 0.5rem;
}

.chat-input {
  flex: 1;
  padding: 0.8rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.send-button {
  padding: 0.8rem 1.2rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.send-button:hover {
  background-color: #36996b;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.file-input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.upload-button {
  padding: 0.8rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  width: 120px;
}

.upload-button:hover {
  background-color: #36996b;
}

.result-audio,
.result-image {
  margin-top: 1rem;
}

.result-image img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}
</style>