<template>
  <div :class="['message', message.isUser ? 'user-message' : 'bot-message']">
    <div v-if="message.text" v-html="parsedMessage"></div>
    <div v-if="message.audio_base64">
      <audio controls>
        <source :src="audioUrl">
        </source>
      </audio>
    </div>
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

const audioUrl = computed(() => {
  return props.message.audio_base64;
});

const parsedMessage = computed(() => {
  return marked.parse(props.message.text);
});

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