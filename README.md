# WallBreaking 安装指南

本项目为前后端分离项目，前端使用 Vue 3 编写，后端使用 FastAPI 完成。

使用前，请现将阿里云百炼 Key 放置于环境变量参数 `DASHSCOPE_API_KEY` 中，以便程序自动读取。

## 后端环境配置指南

后端所需所有 conda 依赖保存在 requirements.txt 文件中，请依照该文件开头所述的 conda 环境安装提示进行安装。

安装完成后，可以使用 `fastapi.exe dev main.py` 命令运行 wb-backend 文件夹下的 main.py 文件，以启动后端服务。

## 前端配置指南

请安装 nodejs ，并在 wb-frontend 目录下执行 `npm install` 命令。安装完成后在 wb-frontend 目录下执行 
`npm run dev` 命令启动前端服务。

至此，前后端服务均启动，可以正常对话。

