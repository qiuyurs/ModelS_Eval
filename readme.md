# 大模型评测 ModelS_Eval平台
ModelS-Eval 多模型智能评测平台 是一款具备跨厂商、跨平台兼容性的综合性评测系统。该平台支持对私有化部署模型进行并行对比评估，用户仅需提交单份测试数据集（含多轮对话样本），即可实现多模型响应质量的同步自动化评测。其核心优势包括：
1. 多模态支持能力​：兼容文本、图像、视频等多种数据类型的输入评测
2. 全场景覆盖​：适配国内外主流公有云服务、私有云环境、本地化部署的大语言模型及智能体平台
3. 统一评测框架​：提供标准化的评估体系，实现异构模型间的性能横向对比
4. 安全可控的私有化部署​：支持本地化部署，代码开源且未加密，客户可在私有网络环境中独立运行，确保数据与模型评测过程的安全性和隐私性，避免敏感信息外泄
5. 灵活可扩展​：基于开源架构，用户可根据业务需求进行二次开发，定制专属评测流程

详细使用文档：[飞书文档](https://gwl1554ppni.feishu.cn/wiki/Z3t1w1514ix81AkeQirceTp6nww)

## 本地部署
目前Docker镜像已经托管到阿里云平台，国内用户可快速部署使用
在支持 Docker 的 服务器/电脑 上执行以下命令
```
docker run -d \
  -p 21222:26000 \   
  --name models_eval \    
  registry.cn-hangzhou.aliyuncs.com/qiuyus/models_eval:latest
  ```
其中21222为本地端口，26000为镜像内服务端口，可根据实际情况进行修改。
访问地址：[http://localhost:21222/](http://localhost:21222/)

## 开发文档
目录：
```
├── static  # 前端代码
├── /api    # 后端接口代码
├── requirements.txt # 依赖包
├── README.md # 项目说明
```

前端架构：Vue3 + Arco design + Vite
后端架构：FastAPI + Uvicorn + Sqlite3

启动服务：
前端
```
cd static
npm install
npm run dev
```
后端
```
uvicorn main:app --host 0.0.0.0 --port 26000 --reload
```

## 联系我们
如果您在使用过程中遇到任何问题，欢迎联系我们：
微信：qrecyc 
邮箱EMAIL邮箱：qiuyus@163.com