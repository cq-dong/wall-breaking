<template>
  <div :class="['message', message.isUser ? 'user-message' : 'bot-message']" v-html="parsedMessage">
  </div>

  <!-- 语音条 -->
  <div v-if="message.audio_file" class="audio-player">
    <button @click="togglePlayback" class="audio-button">
      <span v-if="!isPlaying">▶</span>
      <span v-else>⏸</span>
    </button>
    <span class="audio-label">点击播放语音</span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Marked } from 'marked';
import { markedHighlight } from "marked-highlight";
import hljs from 'highlight.js';

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

const isPlaying = ref(false);
const audioElement = ref(null);

const parsedMessage = computed(() => {
  return marked.parse(props.message.text);
});

const togglePlayback = () => {
  if (!audioElement.value) {
    audioElement.value = new Audio(props.message.audioUrl);
    audioElement.value.onended = () => {
      isPlaying.value = false;
    };
  }

  if (isPlaying.value) {
    audioElement.value.pause();
    isPlaying.value = false;
  } else {
    audioElement.value.play();
    isPlaying.value = true;
  }
};
</script>

<style scoped>
.message {
  padding: 0.8rem 1rem;
  border-radius: 18px;
  max-width: 70%;
  word-wrap: break-word;
}

.user-message {
  align-self: flex-end;
  background-color: #dcf8c6;
}

.bot-message {
  align-self: flex-start;
  background-color: #ececec;
}

.audio-player {
  display: flex;
  align-items: center;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #f0f0f0;
  border-radius: 18px;
  max-width: 50%;
}

.user-message .audio-player {
  align-self: flex-end;
  margin-left: auto;
}

.bot-message .audio-player {
  align-self: flex-start;
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