<template>
  <div :class="['message-container', message.isUser ? 'user-container' : 'bot-container', message.isBackground ? 'background-container' : '']">
    <div class="avatar">
      <img :src="message.isUser ? userAvatar : (message.isBackground ? backgroundAvatar : botAvatar)" alt="Avatar" class="avatar-img">
    </div>
    <div :class="['message', message.isUser ? 'user-message' : (message.isBackground ? 'background-message' : 'bot-message')]">
      <div v-if="message.image_base64" class="message-image">
        <img :src="imageUrl" alt="用户发送的图片" class="chat-image">
      </div>
      <div v-if="message.text" v-html="parsedMessage"></div>
      <div v-if="message.audio_base64">
        <audio controls>
          <source :src="audioUrl">
          </source>
        </audio>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Marked } from 'marked';
import { markedHighlight } from "marked-highlight";
import hljs from 'highlight.js';
import defaultUserAvatar from '../assets/default-user-avatar.svg';
import defaultBotAvatar from '../assets/default-bot-avatar.svg';

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

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
});

const audioUrl = computed(() => {
  return props.message.audio_base64;
});

const imageUrl = computed(() => {
  if (props.message.image_base64 && props.message.image_type) {
    return `data:${props.message.image_type};base64,${props.message.image_base64}`;
  }
  return null;
});

const parsedMessage = computed(() => {
  return marked.parse(props.message.text);
});

// 获取用户头像，如果localStorage中有则使用，否则使用默认头像
const userAvatar = computed(() => {
  const savedAvatar = localStorage.getItem('userAvatar');
  return savedAvatar || defaultUserAvatar;
});

// 获取机器人头像，如果localStorage中有则使用，否则使用默认头像
const botAvatar = computed(() => {
  const savedAvatar = localStorage.getItem('botAvatar');
  return savedAvatar || defaultBotAvatar;
});

// 背景头像 - 使用一个特殊的背景图标
const backgroundAvatar = computed(() => {
  // 创建一个简单的SVG背景头像，使用URL编码避免btoa的Unicode问题
  const svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
    <circle cx="20" cy="20" r="18" fill="#e8f4fd" stroke="#4a90e2" stroke-width="2"/>
    <rect x="12" y="14" width="16" height="12" fill="#4a90e2" rx="2"/>
    <circle cx="15" cy="18" r="2" fill="#e8f4fd"/>
    <polygon points="12,22 16,18 20,22 24,18 28,22 28,24 12,24" fill="#e8f4fd"/>
  </svg>`;
  return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgContent);
});

</script>

<style scoped>
.message-container {
  display: flex;
  margin-bottom: 15px;
  width: 100%;
}

.user-container {
  flex-direction: row-reverse;
}

.bot-container {
  flex-direction: row;
}

.avatar {
  width: 40px;
  height: 40px;
  margin: 0 10px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #ddd;
}

.message {
  padding: 0.8rem 1rem;
  border-radius: 18px;
  max-width: 70%;
  word-wrap: break-word;
}

.message-image {
  margin-bottom: 8px;
}

.chat-image {
  max-width: 300px;
  max-height: 200px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-image:hover {
  transform: scale(1.02);
}

.user-message {
  background-color: #dcf8c6;
}

.bot-message {
  background-color: #ececec;
}

.background-message {
  background: linear-gradient(135deg, #e8f4fd 0%, #d1e7dd 100%);
  border: 1px solid #4a90e2;
  position: relative;
  font-style: italic;
}

.background-message::before {
  content: "💬";
  position: absolute;
  top: -8px;
  right: -8px;
  background: #4a90e2;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
}

.background-container {
  opacity: 0.9;
  animation: backgroundMessageFade 0.5s ease-in;
}

@keyframes backgroundMessageFade {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 0.9;
    transform: translateY(0);
  }
}

.audio-player {
  display: flex;
  align-items: center;
}

.audio-button {
  background: #42b983;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.audio-label {
  font-size: 14px;
  color: #333;
}
</style>