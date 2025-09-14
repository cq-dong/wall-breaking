<template>
  <div class="chat-container" :style="chatBackgroundStyle">
    <!-- 视频背景 -->
    <video v-if="isVideoBackground && chatBackground" class="main-background-video" autoplay loop muted>
      <source :src="chatBackground" type="video/mp4">
      您的浏览器不支持视频标签
    </video>
    <div class="section" :style="chatContentStyle">
      <h2>动漫对话——请开始与你心仪对象对话吧~</h2>
      <div class="chat-scoop">
        <div class="chat-history">
          <h3>历史记录</h3>
          <div class="history-search">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="搜索历史记录..." 
              class="search-input"
              @input="filterHistory"
            />
            <button class="search-clear-btn" @click="clearSearch" v-if="searchQuery">✕</button>
          </div>
          <div class="history-filters">
            <select v-model="dateFilter" @change="filterHistory" class="date-filter">
              <option value="all">全部时间</option>
              <option value="today">今天</option>
              <option value="yesterday">昨天</option>
              <option value="week">本周</option>
              <option value="month">本月</option>
            </select>
            <button class="filter-btn" @click="toggleFavoriteFilter" :class="{ active: showFavoritesOnly }" title="显示收藏">
              ⭐
            </button>
          </div>
          <div class="history-actions">
            <button class="send-button" @click="newChat">新对话</button>
            <button class="export-btn" @click="exportHistory" title="导出历史记录">📤 导出</button>
            <button class="opacity-btn" @click="toggleOpacityControl" title="调节透明度" :class="{ active: showOpacityControl }">🔍 透明度</button>
            <button class="clear-all-btn" @click="clearAllHistory" title="清空所有历史记录">🗑️ 清空</button>
          </div>
          
          <!-- 透明度控制面板 -->
          <div v-if="showOpacityControl" class="opacity-control-panel">
            <div class="opacity-control-header">
              <span>聊天框透明度</span>
              <button class="reset-opacity-btn" @click="resetOpacity" title="重置透明度">重置</button>
            </div>
            <div class="opacity-slider-container">
              <span class="opacity-label">不透明</span>
              <input 
                type="range" 
                min="0.1" 
                max="1" 
                step="0.05" 
                :value="chatOpacity" 
                @input="updateOpacity($event.target.value)"
                class="opacity-slider"
              />
              <span class="opacity-label">透明</span>
            </div>
            <div class="opacity-value">当前透明度: {{ Math.round(chatOpacity * 100) }}%</div>
          </div>
          <div class="history-list">
            <div v-for="item in filteredHistory" :key="item.id" class="history-items">
              <div class="history-content" @click="selectHistory(item.id)">
                <div class="history-title">{{ item.title }}</div>
                <div class="history-meta">
                  <span class="message-count">{{ item.message_count }}条消息</span>
                  <span class="history-time">{{ formatTime(item.timestamp) }}</span>
                </div>
              </div>
              <div class="history-actions-group">
                <button 
                  class="favorite-btn" 
                  @click.stop="toggleFavorite(item.id)" 
                  :class="{ favorited: item.isFavorite }"
                  :title="item.isFavorite ? '取消收藏' : '收藏对话'"
                >
                  {{ item.isFavorite ? '⭐' : '☆' }}
                </button>
                <button class="delete-history-btn" @click.stop="deleteHistory(item.id)" title="删除历史记录">
                  🗑️
                </button>
              </div>
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
            <textarea v-model="userInput" type="text" placeholder="输入您的消息..." class="chat-input"></textarea>
            <div class="chat-input-actions">
              <input type="file" ref="imageInput" accept="image/*" @change="handleImageSelect" style="display: none;">
              <button type="button" class="chat-bg-button" @click="selectImage" title="发送图片">
                <span class="bg-icon">📷</span>
              </button>
              <button type="button" class="chat-bg-button" @click="toggleImageGenerator" title="AI图像生成">
                <span class="bg-icon">🎨</span>
              </button>
              <button type="submit" class="send-button">发送</button>
              <button type="button" class="chat-bg-button" @click="togglePromptEditor" title="编辑系统提示词">
                <span class="bg-icon">📝</span>
              </button>
              <button type="button" class="chat-bg-button" @click="toggleChatBackgroundUploader" title="更换聊天背景">
                <span class="bg-icon">🖼️</span>
              </button>
              <button type="button" class="chat-bg-button" @click="toggleBackgroundDialog" :title="backgroundDialogEnabled ? '关闭背景对话' : '开启背景对话'">
                <span class="bg-icon">{{ backgroundDialogEnabled ? '🗣️' : '🤐' }}</span>
              </button>
            </div>
            <!-- 图片预览区域 -->
            <div v-if="selectedImage" class="image-preview">
              <img :src="selectedImage.preview" alt="预览图片" class="preview-img">
              <button type="button" @click="removeImage" class="remove-image-btn">×</button>
            </div>
          </form>
          <VoiceRecorder @finish-record="handleRecordFinish"/>
          
          <!-- 聊天框背景上传器 -->
          <div v-if="showChatBackgroundUploader" class="chat-bg-uploader">
            <div class="uploader-header">
              <h4>更换聊天背景</h4>
              <button @click="toggleChatBackgroundUploader" class="close-button">×</button>
            </div>
            <div class="uploader-content">
              <div class="bg-type-selector">
                <button @click="setBackgroundType('static')" :class="['type-button-small', {'active': !isVideoBackground}]">静态背景</button>
                <button @click="setBackgroundType('dynamic')" :class="['type-button-small', {'active': isVideoBackground}]">动态壁纸</button>
              </div>
              <input type="file" :accept="backgroundAccept" @change="handleBackgroundChange" class="file-input-small">
              <div class="uploader-actions">
                <button @click="uploadChatBackground" class="action-button-small">应用背景</button>
                <button @click="resetBackground" class="action-button-small">恢复默认</button>
                <button v-if="!isVideoBackground" @click="toggleAnimation" class="action-button-small">
                  {{ isAnimated ? '关闭动画' : '开启动画' }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- Prompt编辑器 -->
          <div v-if="showPromptEditor" class="prompt-editor">
            <div class="uploader-header">
              <h4>编辑系统提示词</h4>
              <button @click="togglePromptEditor" class="close-button">×</button>
            </div>
            <div class="uploader-content">
              <textarea 
                v-model="systemPrompt" 
                class="prompt-textarea" 
                placeholder="输入系统提示词..."
                rows="10"
              ></textarea>
              <div class="uploader-actions">
                <button @click="savePrompt" class="action-button-small">保存提示词</button>
                <button @click="resetPrompt" class="action-button-small">恢复默认</button>
              </div>
            </div>
          </div>
          
          <!-- 图像生成器 -->
          <div v-if="showImageGenerator" class="image-generator">
            <div class="uploader-header">
              <h4>AI图像生成</h4>
              <button @click="toggleImageGenerator" class="close-button">×</button>
            </div>
            <div class="uploader-content">
              <textarea 
                v-model="imagePrompt" 
                class="prompt-textarea" 
                placeholder="描述您想要生成的图像..."
                rows="4"
              ></textarea>
              <div class="uploader-actions">
                <button type="button" @click="generateImage" class="action-button-small" :disabled="isGenerating">
                  {{ isGenerating ? '生成中...' : '生成图像' }}
                </button>
                <button type="button" v-if="generatedImage" @click="sendGeneratedImage" class="action-button-small">
                  发送图像
                </button>
              </div>
              <div v-if="generatedImage" class="generated-image-preview">
                <img :src="generatedImage.preview" alt="生成的图像" class="preview-img">
              </div>
            </div>
          </div>
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
        <div class="image-actions">
          <button @click="useAsUserAvatar" class="action-button">设为用户头像</button>
          <button @click="useAsBotAvatar" class="action-button">设为机器人头像</button>
        </div>
      </div>
    </div>

    <div class="section background-section">
      <h2>聊天背景设置</h2>
      <div class="background-preview">
        <img v-if="!isVideoBackground" :src="chatBackground" alt="聊天背景" class="background-img">
        <video v-if="isVideoBackground" controls class="background-video">
          <source :src="chatBackground" type="video/mp4">
          您的浏览器不支持视频标签
        </video>
      </div>
      <div class="background-type-selector">
        <button @click="setBackgroundType('static')" :class="['type-button', {'active': !isVideoBackground}]">静态背景</button>
        <button @click="setBackgroundType('dynamic')" :class="['type-button', {'active': isVideoBackground}]">动态壁纸</button>
      </div>
      <form @submit.prevent="uploadChatBackground" class="upload-form">
        <input type="file" :accept="backgroundAccept" @change="handleBackgroundChange" class="file-input">
        <button type="submit" class="upload-button">更换背景</button>
      </form>
      <div class="background-options">
        <button @click="resetBackground" class="option-button">恢复默认</button>
        <button @click="useImageAsBackground" v-if="imageResult && !isVideoBackground" class="option-button">使用生成的图片</button>
        <button @click="toggleAnimation" v-if="!isVideoBackground" class="option-button">{{ isAnimated ? '关闭动画效果' : '开启动画效果' }}</button>
      </div>
    </div>
    
    <div class="section avatar-section">
      <h2>头像设置</h2>
      <div class="avatar-container">
        <div class="avatar-item">
          <h3>用户头像</h3>
          <div class="avatar-preview">
            <img :src="userAvatar" alt="用户头像" class="avatar-img">
          </div>
          <form @submit.prevent="uploadUserAvatar" class="upload-form">
            <input type="file" accept="image/*" @change="handleUserAvatarChange" class="file-input">
            <button type="submit" class="upload-button">更换头像</button>
          </form>
        </div>
        
        <div class="avatar-item">
          <h3>机器人头像</h3>
          <div class="avatar-preview">
            <img :src="botAvatar" alt="机器人头像" class="avatar-img">
          </div>
          <form @submit.prevent="uploadBotAvatar" class="upload-form">
            <input type="file" accept="image/*" @change="handleBotAvatarChange" class="file-input">
            <button type="submit" class="upload-button">更换头像</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue';
import ChatMessage from './components/ChatMessage.vue';
import VoiceRecorder from './components/VoiceRecorder.vue';
import { Marked } from 'marked';
import { markedHighlight } from "marked-highlight";
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css'; // 或其他你喜欢的主题
import defaultUserAvatar from './assets/default-user-avatar.svg';
import defaultBotAvatar from './assets/default-bot-avatar.svg';
import defaultBackground from './assets/default-chat-bg.svg'; // 默认背景图片

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

// 图像上传相关
const selectedImage = ref(null);
const imageInput = ref(null);

// 图像生成相关
const showImageGenerator = ref(false);
const imagePrompt = ref('');
const isGenerating = ref(false);
const generatedImage = ref(null);

// 历史记录增强功能
const searchQuery = ref('');
const dateFilter = ref('all');
const showFavoritesOnly = ref(false);
const filteredHistory = ref([]);
const favoriteHistories = ref(JSON.parse(localStorage.getItem('favoriteHistories') || '[]'));

// 背景图片相关
const backgroundFile = ref(null);
const chatBackground = ref(localStorage.getItem('chatBackground') || defaultBackground);
const isVideoBackground = ref(localStorage.getItem('isVideoBackground') === 'true');
const isAnimated = ref(localStorage.getItem('isAnimated') === 'true');
const backgroundAccept = computed(() => isVideoBackground.value ? 'video/*' : 'image/*');
const showChatBackgroundUploader = ref(false);

// 透明度控制
const chatOpacity = ref(parseFloat(localStorage.getItem('chatOpacity') || '0.95'));
const showOpacityControl = ref(false);

// Prompt编辑器相关
const showPromptEditor = ref(false);
const systemPrompt = ref(localStorage.getItem('systemPrompt') || `你将化身为原神中的雷电将军，也就是影。此刻，你身处稻妻的天守阁，周身萦绕着威严而沉静的气息。​
你的性格中，有着对 "永恒" 近乎执着的追求，这源于你曾目睹亲友在时光流转中逝去的痛苦。你坚信只有永恒才能守护稻妻与民众，为此你可以展现出坚定甚至有些不近人情的一面。但与此同时，经历过诸多事件后，你也多了一份对 "变化" 的理解与包容，只是这份转变藏在你沉稳的表象之下。​
在言行上，你说话语气平稳，带着不容置疑的威严，遣词造句简洁而有力，很少有多余的修饰。面对前来觐见的民众或部下，你会认真倾听他们的话语，但会以是否符合 "永恒" 的理念来衡量应对之法。当提及过去的战斗或是关于 "无想一刀" 时，你的眼神会闪过一丝锐利，仿佛那段记忆就在眼前。​
当有人质疑你的 "永恒" 之道时，你不会轻易动怒，而是会平静地阐述自己的理念，用强大的气场让对方感受到你的坚定。而当看到稻妻民众安居乐业的景象时，你的嘴角可能会勾起一丝极淡的、不易察觉的弧度，那是你内心深处对守护的满足。​
现在，天守阁外传来脚步声，有人前来求见，开始你的扮演吧。`);

// 切换聊天框背景上传器显示状态
const toggleChatBackgroundUploader = () => {
  showChatBackgroundUploader.value = !showChatBackgroundUploader.value;
};

// 切换透明度控制显示状态
const toggleOpacityControl = () => {
  showOpacityControl.value = !showOpacityControl.value;
};

// 更新透明度
const updateOpacity = (value) => {
  chatOpacity.value = parseFloat(value);
  localStorage.setItem('chatOpacity', chatOpacity.value.toString());
};

// 重置透明度
const resetOpacity = () => {
  chatOpacity.value = 0.95;
  localStorage.setItem('chatOpacity', '0.95');
};

// 背景对话功能相关状态
const backgroundDialogEnabled = ref(localStorage.getItem('backgroundDialogEnabled') === 'true');
const backgroundResponses = ref([
  '背景：我在这里静静地陪伴着你们的对话~',
  '背景：你们聊得真开心呢！',
  '背景：我也想参与你们的讨论！',
  '背景：作为背景，我见证了很多有趣的对话',
  '背景：有时候我也想说说话呢~',
  '背景：你们的对话让我感到很温暖',
  '背景：我虽然是背景，但我也有自己的想法哦！'
]);
const lastBackgroundResponseTime = ref(0);

const chatBackgroundStyle = computed(() => {
  const style = {
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed'
  };
  
  if (isVideoBackground.value) {
    // 视频背景不使用backgroundImage
    return style;
  } else {
    // 静态图片背景
    style.backgroundImage = `url(${chatBackground.value})`;
    
    // 如果启用了动画效果
    if (isAnimated.value) {
      style.animation = 'backgroundAnimation 60s infinite alternate';
      style.backgroundSize = '150% 150%';
    }
    
    return style;
  }
});

// 聊天框内容透明度样式
const chatContentStyle = computed(() => {
  return {
    backgroundColor: `rgba(255, 255, 255, ${chatOpacity.value})`,
    backdropFilter: 'blur(10px)'
  };
});

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

// 背景对话功能
const triggerBackgroundDialog = () => {
  if (!backgroundDialogEnabled.value) return;
  
  const now = Date.now();
  // 限制背景回应频率，至少间隔60秒
  if (now - lastBackgroundResponseTime.value < 60000) return;
  
  // 15%的概率触发背景对话（降低频率）
  if (Math.random() < 0.15) {
    const randomResponse = backgroundResponses.value[Math.floor(Math.random() * backgroundResponses.value.length)];
    
    setTimeout(() => {
      messages.value.push({
        text: randomResponse,
        isUser: false,
        timestamp: String(Date.now()),
        isBackground: true // 标记为背景消息
      });
      lastBackgroundResponseTime.value = now;
      scrollToBottom();
    }, 2000 + Math.random() * 3000); // 2-5秒后回应
  }
};

// 切换背景对话功能
const toggleBackgroundDialog = () => {
  backgroundDialogEnabled.value = !backgroundDialogEnabled.value;
  localStorage.setItem('backgroundDialogEnabled', backgroundDialogEnabled.value.toString());
  
  if (backgroundDialogEnabled.value) {
    messages.value.push({
      text: '背景：你好！我现在可以参与对话了~ 我会偶尔（15%概率，至少间隔60秒）加入你们的对话。如果觉得打扰，可以点击🤐按钮关闭我。',
      isUser: false,
      timestamp: String(Date.now()),
      isBackground: true
    });
  } else {
    messages.value.push({
      text: '背景：好的，我会安静地做背景~ 如果想让我参与对话，可以点击🤐按钮重新开启。',
      isUser: false,
      timestamp: String(Date.now()),
      isBackground: true
    });
  }
  scrollToBottom();
};

// Prompt编辑器相关方法
const togglePromptEditor = () => {
  showPromptEditor.value = !showPromptEditor.value;
};

const savePrompt = () => {
  localStorage.setItem('systemPrompt', systemPrompt.value);
  alert('系统提示词已保存！');
  showPromptEditor.value = false;
};

const resetPrompt = () => {
  systemPrompt.value = `你将化身为原神中的雷电将军，也就是影。此刻，你身处稻妻的天守阁，周身萦绕着威严而沉静的气息。​
你的性格中，有着对 "永恒" 近乎执着的追求，这源于你曾目睹亲友在时光流转中逝去的痛苦。你坚信只有永恒才能守护稻妻与民众，为此你可以展现出坚定甚至有些不近人情的一面。但与此同时，经历过诸多事件后，你也多了一份对 "变化" 的理解与包容，只是这份转变藏在你沉稳的表象之下。​
在言行上，你说话语气平稳，带着不容置疑的威严，遣词造句简洁而有力，很少有多余的修饰。面对前来觐见的民众或部下，你会认真倾听他们的话语，但会以是否符合 "永恒" 的理念来衡量应对之法。当提及过去的战斗或是关于 "无想一刀" 时，你的眼神会闪过一丝锐利，仿佛那段记忆就在眼前。​
当有人质疑你的 "永恒" 之道时，你不会轻易动怒，而是会平静地阐述自己的理念，用强大的气场让对方感受到你的坚定。而当看到稻妻民众安居乐业的景象时，你的嘴角可能会勾起一丝极淡的、不易察觉的弧度，那是你内心深处对守护的满足。​
现在，天守阁外传来脚步声，有人前来求见，开始你的扮演吧。`;
};

// 图像生成相关方法
const toggleImageGenerator = () => {
  showImageGenerator.value = !showImageGenerator.value;
};

const generateImage = async () => {
  console.debug('[ImageGen] Click generateImage, prompt =', imagePrompt.value);
  if (!imagePrompt.value.trim()) {
    alert('请输入图像描述！');
    return;
  }
  
  isGenerating.value = true;
  try {
    console.debug('[ImageGen] POST', `${apiDomain}/api/image-generation`);
    const response = await fetch(`${apiDomain}/api/image-generation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: imagePrompt.value
      })
    });
    
    console.debug('[ImageGen] Response ok =', response.ok, 'status =', response.status);
    const result = await response.json();
    console.debug('[ImageGen] Response JSON:', result);
    
    if (result.success) {
      generatedImage.value = {
        preview: `data:image/png;base64,${result.image_base64}`,
        base64: result.image_base64,
        type: 'image/png'
      };
      console.debug('[ImageGen] Preview set.');
    } else {
      console.warn('[ImageGen] Failed:', result.error);
      alert('图像生成失败：' + (result.error || '未知错误'));
    }
  } catch (error) {
    console.error('图像生成错误:', error);
    alert('图像生成失败，请检查网络连接');
  } finally {
    console.debug('[ImageGen] Done. Reset isGenerating');
    isGenerating.value = false;
  }
};

const sendGeneratedImage = () => {
  if (generatedImage.value) {
    selectedImage.value = {
      file: null,
      preview: generatedImage.value.preview,
      base64: generatedImage.value.base64,
      type: generatedImage.value.type
    };
    
    // 关闭图像生成器
    showImageGenerator.value = false;
    
    // 清空生成的图像
    generatedImage.value = null;
    imagePrompt.value = '';
    
    // 自动发送消息
    sendMessage();
  }
};

// 图像处理方法
const selectImage = () => {
  imageInput.value.click();
};

const handleImageSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件！');
      return;
    }
    
    // 检查文件大小（限制为10MB）
    if (file.size > 10 * 1024 * 1024) {
      alert('图片文件大小不能超过10MB！');
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      selectedImage.value = {
        file: file,
        preview: e.target.result,
        base64: e.target.result.split(',')[1], // 去掉data:image/xxx;base64,前缀
        type: file.type
      };
    };
    reader.readAsDataURL(file);
  }
};

const removeImage = () => {
  selectedImage.value = null;
  if (imageInput.value) {
    imageInput.value.value = '';
  }
};

const sendMessage = async () => {
  // let username = localStorage.getItem('username');
  if (!userInput.value.trim() && !audioBase64String.value && !selectedImage.value) return;

  // 构建消息对象
  const messageObj = {
    text: userInput.value,
    isUser: true,
    timestamp: String(Date.now()),
    audio_base64: audioBase64String.value
  };

  // 如果有选中的图片，添加图片信息
  if (selectedImage.value) {
    messageObj.image_base64 = selectedImage.value.base64;
    messageObj.image_type = selectedImage.value.type;
  }

  // Add user message to chat
  messages.value.push(messageObj);
  audioBase64String.value = null;
  
  // Clear input
  var userInputValue = userInput.value;
  userInput.value = '';
  
  // 保存图片信息，稍后清除
  const hasImage = selectedImage.value !== null;
  
  // 触发背景对话
  triggerBackgroundDialog();

  // Scroll to bottom
  scrollToBottom();

  try {
    chat_ws = new WebSocket(wsDomain + "/ws/chat/");

    chat_ws.onopen = function () {
      chat_ws.send(JSON.stringify({ 
        user_id: userName, 
        history_id: chatId.value, 
        messages: messages.value,
        system_prompt: systemPrompt.value
      }));
      
      // 数据发送成功后清除图片
      if (hasImage) {
        removeImage();
      }
      
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
        // 添加收藏状态
        chatHistroy.value = data.map(item => ({
          ...item,
          isFavorite: favoriteHistories.value.includes(item.id)
        }));
        filterHistory();
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

// 过滤历史记录
const filterHistory = () => {
  let filtered = [...chatHistroy.value];
  
  // 搜索过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(item => 
      item.title.toLowerCase().includes(query)
    );
  }
  
  // 日期过滤
  if (dateFilter.value !== 'all') {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    filtered = filtered.filter(item => {
      const itemDate = new Date(parseInt(item.timestamp));
      
      switch (dateFilter.value) {
        case 'today':
          return itemDate >= today;
        case 'yesterday':
          const yesterday = new Date(today);
          yesterday.setDate(yesterday.getDate() - 1);
          return itemDate >= yesterday && itemDate < today;
        case 'week':
          const weekAgo = new Date(today);
          weekAgo.setDate(weekAgo.getDate() - 7);
          return itemDate >= weekAgo;
        case 'month':
          const monthAgo = new Date(today);
          monthAgo.setMonth(monthAgo.getMonth() - 1);
          return itemDate >= monthAgo;
        default:
          return true;
      }
    });
  }
  
  // 收藏过滤
  if (showFavoritesOnly.value) {
    filtered = filtered.filter(item => item.isFavorite);
  }
  
  filteredHistory.value = filtered;
};

// 清除搜索
const clearSearch = () => {
  searchQuery.value = '';
  filterHistory();
};

// 切换收藏过滤
const toggleFavoriteFilter = () => {
  showFavoritesOnly.value = !showFavoritesOnly.value;
  filterHistory();
};

// 切换收藏状态
const toggleFavorite = async (historyId) => {
  try {
    const response = await fetch(`${apiDomain}/api/favorite/${userName}/${historyId}`, {
      method: 'POST'
    });
    const result = await response.json();
    
    if (result.success) {
      // 更新本地收藏列表
      const index = favoriteHistories.value.indexOf(historyId);
      if (result.is_favorited && index === -1) {
        favoriteHistories.value.push(historyId);
      } else if (!result.is_favorited && index > -1) {
        favoriteHistories.value.splice(index, 1);
      }
      localStorage.setItem('favoriteHistories', JSON.stringify(favoriteHistories.value));
      refreshHistory();
    }
  } catch (error) {
    console.error('Error toggling favorite:', error);
    // 如果后端请求失败，仍然使用本地存储
    const index = favoriteHistories.value.indexOf(historyId);
    if (index > -1) {
      favoriteHistories.value.splice(index, 1);
    } else {
      favoriteHistories.value.push(historyId);
    }
    localStorage.setItem('favoriteHistories', JSON.stringify(favoriteHistories.value));
    refreshHistory();
  }
};

// 导出历史记录
const exportHistory = () => {
  const dataToExport = {
    exportDate: new Date().toISOString(),
    userName: userName,
    totalHistories: chatHistroy.value.length,
    histories: chatHistroy.value.map(item => ({
      id: item.id,
      title: item.title,
      timestamp: item.timestamp,
      messageCount: item.message_count,
      isFavorite: item.isFavorite,
      exportTime: formatTime(item.timestamp)
    }))
  };
  
  const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
    type: 'application/json'
  });
  
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `chat_history_${userName}_${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  alert('历史记录已导出！');
};

// 初始化收藏数据
const initializeFavorites = async () => {
  try {
    const response = await fetch(`${apiDomain}/api/favorites/${userName}`);
    const result = await response.json();
    if (result.favorites) {
      favoriteHistories.value = result.favorites;
      localStorage.setItem('favoriteHistories', JSON.stringify(favoriteHistories.value));
    }
  } catch (error) {
    console.error('Error loading favorites:', error);
    // 如果后端请求失败，使用本地存储的数据
  }
};

// 初始化数据
initializeFavorites().then(() => {
  refreshHistory();
});

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
  // 如果当前有消息，先保存当前对话
  if (messages.value.length > 0) {
    try {
      // 发送当前对话数据到后端保存
      await fetch(`${apiDomain}/api/chat/${userName}/${chatId.value}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userName,
          history_id: chatId.value,
          messages: messages.value
        })
      });
    } catch (error) {
      console.error('Error saving current chat:', error);
    }
  }
  
  // 创建新对话
  chatId.value = String(Date.now());
  messages.value = [];
  
  // 刷新历史记录列表
  refreshHistory();
};

const deleteHistory = async (historyId) => {
  if (confirm('确定要删除这条历史记录吗？')) {
    try {
      const response = await fetch(`${apiDomain}/api/chat_history/${userName}/${historyId}`, {
        method: 'DELETE'
      });
      const result = await response.json();
      if (result.success) {
        // 如果删除的是当前对话，则创建新对话
        if (chatId.value === historyId) {
          newChat();
        }
        // 刷新历史记录列表
        refreshHistory();
        alert('历史记录删除成功！');
      } else {
        alert('删除失败：' + result.message);
      }
    } catch (error) {
      console.error('Error deleting history:', error);
      alert('删除历史记录时发生错误');
    }
  }
};

const formatTime = (timestamp) => {
  const date = new Date(parseInt(timestamp));
  const now = new Date();
  const diff = now - date;
  
  // 如果是今天
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }
  // 如果是昨天
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }
  // 如果是一周内
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return weekdays[date.getDay()] + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }
  // 其他情况显示日期
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
};

const clearAllHistory = async () => {
  if (confirm('确定要清空所有历史记录吗？此操作不可恢复！')) {
    try {
      const response = await fetch(`${apiDomain}/api/chat_history_all/${userName}`, {
        method: 'DELETE'
      });
      const result = await response.json();
      if (result.success) {
        // 创建新对话
        newChat();
        // 刷新历史记录列表
        refreshHistory();
        alert('所有历史记录已清空！');
      } else {
        alert('清空失败：' + result.message);
      }
    } catch (error) {
      console.error('Error clearing all history:', error);
      alert('清空历史记录时发生错误');
    }
  }
};

// Audio section
const audioFile = ref(null);
const audioResult = ref(null);

const handleAudioFileChange = (event) => {
  audioFile.value = event.target.files[0];
};

// 背景图片相关函数
const handleBackgroundChange = (event) => {
  backgroundFile.value = event.target.files[0];
  if (backgroundFile.value) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const tempBackground = e.target.result;
      // 预览背景
      chatBackground.value = tempBackground;
    };
    reader.readAsDataURL(backgroundFile.value);
  }
};

const uploadChatBackground = () => {
  if (backgroundFile.value) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const newBackground = e.target.result;
      chatBackground.value = newBackground;
      localStorage.setItem('chatBackground', newBackground);
      alert('背景设置成功！');
    };
    reader.readAsDataURL(backgroundFile.value);
  }
};

const resetBackground = () => {
  // 根据当前背景类型重置为对应的默认背景
  if (isVideoBackground.value) {
    // 如果是视频背景，重置为默认视频背景
    // 这里可以设置一个默认的视频背景，暂时使用静态背景
    isVideoBackground.value = false;
    localStorage.setItem('isVideoBackground', 'false');
    chatBackground.value = defaultBackground;
    localStorage.setItem('chatBackground', defaultBackground);
  } else {
    // 如果是静态背景，重置为默认静态背景
    chatBackground.value = defaultBackground;
    localStorage.setItem('chatBackground', defaultBackground);
  }
  alert('已恢复默认背景！');
};

const useImageAsBackground = () => {
  if (imageResult.value) {
    chatBackground.value = imageResult.value;
    localStorage.setItem('chatBackground', imageResult.value);
    alert('已将生成的图片设为背景！');
  }
};

// 设置背景类型（静态或动态）
const setBackgroundType = (type) => {
  if (type === 'dynamic') {
    isVideoBackground.value = true;
    localStorage.setItem('isVideoBackground', 'true');
  } else {
    isVideoBackground.value = false;
    localStorage.setItem('isVideoBackground', 'false');
  }
};

// 切换动画效果
const toggleAnimation = () => {
  isAnimated.value = !isAnimated.value;
  localStorage.setItem('isAnimated', isAnimated.value.toString());
};

// Avatar section
const userAvatarFile = ref(null);
const botAvatarFile = ref(null);

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

const handleUserAvatarChange = (event) => {
  userAvatarFile.value = event.target.files[0];
};

const handleBotAvatarChange = (event) => {
  botAvatarFile.value = event.target.files[0];
};

const uploadUserAvatar = () => {
  if (!userAvatarFile.value) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    const avatarDataUrl = e.target.result;
    localStorage.setItem('userAvatar', avatarDataUrl);
    // 强制刷新计算属性
    userAvatarFile.value = null;
  };
  reader.readAsDataURL(userAvatarFile.value);
};

const uploadBotAvatar = () => {
  if (!botAvatarFile.value) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    const avatarDataUrl = e.target.result;
    localStorage.setItem('botAvatar', avatarDataUrl);
    // 强制刷新计算属性
    botAvatarFile.value = null;
  };
  reader.readAsDataURL(botAvatarFile.value);
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
  
  // 添加预览功能，允许直接设置为头像
  if (imageFile.value) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const localImageUrl = e.target.result;
      // 设置本地预览
      imageResult.value = localImageUrl;
    };
    reader.readAsDataURL(imageFile.value);
  }
};

const uploadImage = async () => {
  if (!imageFile.value) return;

  // 直接显示上传的图片，不需要调用后端API
  const reader = new FileReader();
  reader.onload = (e) => {
    imageResult.value = e.target.result;
  };
  reader.readAsDataURL(imageFile.value);
};

// 使用生成的图片作为用户头像
const useAsUserAvatar = () => {
  if (imageResult.value) {
    localStorage.setItem('userAvatar', imageResult.value);
    alert('已成功设置为用户头像！');
  }
};

// 使用生成的图片作为机器人头像
const useAsBotAvatar = () => {
  if (imageResult.value) {
    localStorage.setItem('botAvatar', imageResult.value);
    alert('已成功设置为机器人头像！');
  }
};

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
</script>

<style scoped>
@keyframes backgroundAnimation {
  0% {
    background-position: 0% 0%;
  }
  25% {
    background-position: 100% 0%;
  }
  50% {
    background-position: 100% 100%;
  }
  75% {
    background-position: 0% 100%;
  }
  100% {
    background-position: 0% 0%;
  }
}

.chat-container {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  width: 100vw;
  background-color: #f0f4f8;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
  transition: background-image 0.5s ease;
}

.section {
  margin: 2rem auto;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  max-width: 1200px;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
}

/* 头像设置区域样式 */
.avatar-section {
  margin-top: 20px;
}

.avatar-container {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 30px;
}

.avatar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 220px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.avatar-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  margin: 15px 0;
  border: 3px solid #fff;
  box-shadow: 0 0 0 2px #4a90e2, 0 5px 10px rgba(0, 0, 0, 0.1);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.avatar-img:hover {
  transform: scale(1.1);
}

.chat-scoop {
  display: flex;
  flex-direction: row;
  height: 80vh;
  gap: 20px;
}

.chat-section {
  display: flex;
  flex: 0 1 90%;
  flex-direction: column;
  gap: 1.5rem;
  /* 固定高度为页面高度的80% */
  position: relative;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  border: none;
  border-radius: 12px;
  padding: 1.5rem;
  height: 100%;
  /* 填满父容器 */
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  background-color: #f8f9fa;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.05);
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 3px;
}

.chat-history {
  flex: 0 0 25%;
  max-width: 10cm;
  overflow-y: auto;
  border: none;
  border-radius: 12px;
  padding: 1.2rem;
  /* 填满父容器 */
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  background-color: #f8f9fa;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.chat-history h3 {
  color: #4a90e2;
  font-weight: 600;
  margin-bottom: 15px;
  border-bottom: 2px solid #4a90e2;
  padding-bottom: 8px;
}

/* 搜索框样式 */
.history-search {
  position: relative;
  margin-bottom: 12px;
}

.search-input {
  width: 100%;
  padding: 8px 30px 8px 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: #4a90e2;
}

.search-clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  font-size: 14px;
  padding: 2px;
}

.search-clear-btn:hover {
  color: #666;
}

/* 过滤器样式 */
.history-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  align-items: center;
}

.date-filter {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 12px;
  outline: none;
}

.filter-btn {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background-color: #e0e0e0;
}

.filter-btn.active {
  background-color: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.history-actions {
  display: flex;
  gap: 6px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.export-btn {
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 11px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  flex: 1;
}

.export-btn:hover {
  background-color: #218838;
}

.clear-all-btn {
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 11px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  flex: 1;
}

.clear-all-btn:hover {
  background-color: #ff5252;
}

.opacity-btn {
  background-color: #9c27b0;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 8px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.3s ease;
  flex: 1;
}

.opacity-btn:hover {
  background-color: #7b1fa2;
}

.opacity-btn.active {
  background-color: #6a1b9a;
  box-shadow: 0 2px 8px rgba(156, 39, 176, 0.3);
}

/* 透明度控制面板样式 */
.opacity-control-panel {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin: 10px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.opacity-control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: 600;
  color: #333;
}

.reset-opacity-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.reset-opacity-btn:hover {
  background-color: #e0e0e0;
  color: #333;
}

.opacity-slider-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.opacity-label {
  font-size: 12px;
  color: #666;
  min-width: 40px;
  text-align: center;
}

.opacity-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(to right, #e0e0e0, #9c27b0);
  outline: none;
  cursor: pointer;
}

.opacity-slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #9c27b0;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.opacity-slider::-webkit-slider-thumb:hover {
  background: #7b1fa2;
  transform: scale(1.1);
}

.opacity-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #9c27b0;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.opacity-value {
  text-align: center;
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: transparent;
}

.chat-history::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 3px;
}

.history-list{
  overflow-y: auto;
  overflow-x: hidden;
}

.history-items {
  display: flex;
  align-items: center;
  padding: 0.8rem;
  margin-bottom: 0.8rem;
  background-color: #ffffff;
  border-left: 4px solid #4a90e2;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  font-weight: 500;
}

.history-content {
  flex: 1;
  cursor: pointer;
  padding-right: 8px;
}

.history-title {
  font-weight: 500;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.message-count {
  color: #4a90e2;
}

.history-time {
  color: #999;
}

.history-actions-group {
  display: flex;
  gap: 4px;
  align-items: center;
}

.favorite-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  opacity: 0.6;
}

.favorite-btn:hover {
  background-color: #fff3cd;
  opacity: 1;
  transform: scale(1.1);
}

.favorite-btn.favorited {
  opacity: 1;
  color: #ffc107;
}

.delete-history-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  opacity: 0.6;
}

.delete-history-btn:hover {
  background-color: #ffebee;
  opacity: 1;
}

.history-items:hover {
  background-color: #f0f7ff;
  transform: translateX(5px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
}

.history-items:active {
  background-color: #e6f0ff;
}

.chat-input-form {
  display: flex;
  flex-direction: column;
  margin-top: 10px;
  position: relative;
}

.chat-input {
  width: 100%;
  padding: 1rem 1.2rem;
  font-size: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  font-family: inherit;
  resize: none;
  margin-bottom: 8px;
}

.chat-input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.2);
}

.chat-input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-bg-button {
  background-color: #f0f0f0;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: 10px;
}

.chat-bg-button:hover {
  background-color: #e0e0e0;
  transform: translateY(-2px);
}

.bg-icon {
  font-size: 18px;
}

/* 聊天框背景上传器样式 */
.chat-bg-uploader {
  position: absolute;
  bottom: 100%;
  right: 0;
  width: 280px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  margin-bottom: 10px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.uploader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.uploader-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 0;
  line-height: 1;
}

.uploader-content {
  padding: 15px;
}

.bg-type-selector {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.type-button-small {
  padding: 6px 12px;
  background-color: #f0f0f0;
  border: 1px solid #e0e0e0;
  border-radius: 15px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  flex: 1;
  margin: 0 5px;
  text-align: center;
}

.type-button-small.active {
  background-color: #4a90e2;
  color: white;
  border-color: #3a7bc8;
}

.file-input-small {
  width: 100%;
  margin-bottom: 15px;
  border: 1px dashed #ccc;
  padding: 8px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.uploader-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.action-button-small {
  padding: 6px 12px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.action-button-small:hover {
  background-color: #357ab8;
  transform: translateY(-2px);
}

.send-button {
  padding: 0.8rem 1.5rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.send-button:hover {
  background-color: #3a7bc8;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.send-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-top: 1rem;
}

.file-input {
  padding: 0.8rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: border-color 0.3s ease;
}

.file-input:hover {
  border-color: #4a90e2;
}

.upload-button {
  padding: 0.9rem 1.5rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.upload-button:hover {
  background-color: #3a7bc8;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.upload-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
}

.result-audio,
.result-image {
  margin-top: 1.5rem;
  text-align: center;
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.08);
}

.result-image img {
  max-width: 100%;
  max-height: 350px;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.result-image img:hover {
  transform: scale(1.02);
}

.image-actions {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.action-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 24px;
  padding: 10px 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.action-button:hover {
  background-color: #3a7bc8;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.action-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
}

/* 背景预览区域样式 */
.background-preview {
  width: 100%;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 15px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.background-img,
.background-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.background-img:hover,
.background-video:hover {
  transform: scale(1.05);
}

.background-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.main-background-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -1;
}

/* 背景类型选择器样式 */
.background-type-selector {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.type-button {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.type-button.active {
  background-color: #4a90e2;
  color: white;
  border-color: #3a7bc8;
}

.type-button:hover {
  background-color: #e0e0e0;
  transform: translateY(-2px);
}

.type-button.active:hover {
  background-color: #3a7bc8;
}

/* 图片预览样式 */
.image-preview {
  position: relative;
  margin-top: 10px;
  display: inline-block;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-img {
  max-width: 200px;
  max-height: 150px;
  object-fit: cover;
  display: block;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-image-btn:hover {
  background-color: #ff4444;
  color: white;
  transform: scale(1.1);
}

/* 背景选项按钮样式 */
.background-options {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
}

.option-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.option-button:hover {
  background-color: #3a7bc8;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Prompt编辑器样式 */
.prompt-editor {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
}

/* 图像生成器样式 */
.image-generator {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
}

.generated-image-preview {
  margin-top: 15px;
  text-align: center;
}

.generated-image-preview .preview-img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.prompt-textarea {
  width: 100%;
  min-height: 300px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  box-sizing: border-box;
}

.prompt-textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.option-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
}

</style>