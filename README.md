# Wall Breaking - AI聊天应用

一个基于Vue 3和FastAPI的AI聊天应用，支持文本对话、图像生成和语音交互。

## 功能特性

- 🤖 AI文本对话（基于通义千问）
- 🎨 AI图像生成（阿里云百炼）
- 🎵 语音交互
- 📷 图片上传和处理
- 🎭 角色扮演（雷电将军）
- 🖼️ 自定义聊天背景

## 技术栈

### 前端
- Vue 3
- Vite
- JavaScript

### 后端
- FastAPI
- Python
- WebSocket
- 阿里云百炼API

## 安装和运行

### 环境要求
- Node.js 16+
- Python 3.8+
- 阿里云百炼API密钥

### 后端设置

1. 进入后端目录：
```bash
cd wb-backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置环境变量：
```bash
# 创建.env文件并添加你的API密钥
echo "DASHSCOPE_API_KEY=your_api_key_here" > .env
```

4. 启动后端服务：
```bash
python main.py
```

### 前端设置

1. 进入前端目录：
```bash
cd wb-frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

## 使用说明

1. 启动后端和前端服务
2. 访问 http://localhost:5173（或显示的端口）
3. 开始与AI对话
4. 使用🎨按钮生成图像
5. 使用📷按钮上传图片

## 注意事项

- 请确保已设置有效的阿里云百炼API密钥
- 图像生成功能需要网络连接
- 建议在生产环境中使用HTTPS

## 许可证

MIT License

