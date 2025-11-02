# Lingshu-7B Web 界面

基于 Flask 的 Lingshu-7B 医学多模态对话系统 Web 界面。

## ✨ 功能特性

- 🤖 **智能对话**: 专业的医学知识问答
- 🖼️ **多模态支持**: 支持图像上传和分析
- ⚡ **4-bit量化**: 默认使用4-bit量化，显存占用低
- 🎨 **现代化UI**: 美观友好的用户界面
- 🔧 **可配置**: 可调节温度、最大Token数等参数
- 📱 **响应式设计**: 支持多种屏幕尺寸

## 📁 项目结构

```
web_interface/
├── backend/                # 后端服务
│   ├── app.py             # Flask应用主文件
│   ├── model_manager.py   # 模型管理器
│   └── config.py          # 配置文件
├── frontend/              # 前端界面
│   ├── index.html         # 主页面
│   └── static/            # 静态资源
│       ├── css/
│       │   └── style.css  # 样式文件
│       └── js/
│           ├── api.js     # API调用封装
│           └── main.js    # 主要逻辑
├── uploads/               # 临时上传文件夹（自动创建）
├── requirements.txt       # Python依赖
└── README.md             # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd web_interface
pip install -r requirements.txt
```

**注意**: 
- 需要 Python 3.8+ 
- 建议使用虚拟环境
- 如果有CUDA支持，确保安装对应版本的PyTorch

### 2. 检查模型路径

确保模型文件位于 `../models/Lingshu-7B` 目录下。如果路径不同，请修改 `backend/config.py` 中的 `MODEL_PATH`。

### 3. 启动服务

```bash
cd backend
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 4. 访问界面

在浏览器中打开 `http://localhost:5000`

## 📖 使用说明

### 基本流程

1. **加载模型**: 点击左侧"加载模型"按钮
2. **输入问题**: 在底部输入框输入医学相关问题
3. **上传图片**（可选）: 点击📎按钮上传医学图像
4. **发送消息**: 点击发送按钮或按 `Ctrl+Enter`
5. **查看回复**: 等待模型生成回复

### 参数调节

在左侧边栏可以调节以下参数：

- **温度 (Temperature)**: 0.1-1.5，控制生成的随机性
  - 较低值：更确定、保守的回答
  - 较高值：更有创造性的回答
  
- **最大Token数**: 128-2048，控制回复的最大长度

### 图像上传

支持的图像格式：
- PNG
- JPG/JPEG
- GIF
- BMP
- WEBP

最大文件大小：16MB

## 🔧 配置说明

### 修改端口

编辑 `backend/config.py`：

```python
FLASK_HOST = "0.0.0.0"  # 监听地址
FLASK_PORT = 5000       # 端口号
```

### 修改量化模式

编辑 `backend/config.py`：

```python
DEFAULT_QUANTIZATION = "4bit"  # 可选: 4bit, 8bit, standard, cpu
```

量化模式说明：
- `4bit`: 4-bit量化，显存占用约 4-5GB
- `8bit`: 8-bit量化，显存占用约 7-8GB
- `standard`: 标准FP16，显存占用约 14GB
- `cpu`: CPU模式，无需GPU但速度慢

### 修改生成参数

编辑 `backend/config.py` 中的 `GENERATION_CONFIG`：

```python
GENERATION_CONFIG = {
    "max_new_tokens": 512,      # 最大生成token数
    "temperature": 0.7,         # 温度
    "top_p": 0.9,              # 核采样参数
    "do_sample": True,          # 是否采样
    "repetition_penalty": 1.1   # 重复惩罚
}
```

## 📡 API 接口

### 获取状态

```http
GET /api/status
```

响应示例：
```json
{
  "service": "running",
  "model_loaded": true,
  "quantization": "4bit",
  "gpu_available": true,
  "gpu_name": "NVIDIA GeForce RTX 3090"
}
```

### 加载模型

```http
POST /api/load_model
```

### 卸载模型

```http
POST /api/unload_model
```

### 聊天

```http
POST /api/chat
Content-Type: multipart/form-data

prompt: "这张图片显示了什么病症？"
image: [图片文件]
```

响应示例：
```json
{
  "success": true,
  "response": "根据图像分析...",
  "has_image": true
}
```

## 🐛 常见问题

### 1. 显存不足

**错误**: CUDA out of memory

**解决方案**:
- 使用更低的量化模式（4-bit）
- 减少 `max_new_tokens` 参数
- 使用CPU模式（较慢）

### 2. 模块导入错误

**错误**: ModuleNotFoundError: No module named 'qwen_vl_utils'

**解决方案**:
```bash
pip install qwen-vl-utils
```

### 3. 模型加载失败

**检查清单**:
- 确认模型文件存在
- 检查磁盘空间是否充足
- 确认有足够的显存/内存
- 查看后端日志获取详细错误信息

### 4. 连接失败

**检查清单**:
- 确认后端服务已启动
- 检查端口是否被占用
- 查看防火墙设置
- 确认浏览器控制台是否有CORS错误

## 🔒 安全注意事项

1. **生产环境部署**:
   - 修改 `config.py` 中的 `FLASK_DEBUG = False`
   - 添加身份验证机制
   - 使用 HTTPS
   - 配置防火墙规则

2. **文件上传**:
   - 已限制文件类型和大小
   - 上传的文件会自动清理
   - 建议添加病毒扫描

3. **API 安全**:
   - 考虑添加 API 密钥验证
   - 实施请求频率限制
   - 记录访问日志

## 🚀 性能优化

### 模型层面

1. **量化选择**:
   - 4-bit: 最省显存，略微降低精度
   - 8-bit: 平衡选项
   - FP16: 最高精度，需要更多显存

2. **批处理**:
   - 当前实现为单次请求
   - 可以修改为支持批量推理

### 服务层面

1. **使用生产级WSGI服务器**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **使用Nginx反向代理**

3. **添加缓存机制**

## 📝 开发计划

### 即将添加的功能

- [ ] 对话历史保存和加载
- [ ] 多用户支持
- [ ] 模型切换功能
- [ ] 更多的生成参数控制
- [ ] 导出对话记录
- [ ] 语音输入支持
- [ ] 更好的错误处理和提示
- [ ] 实时生成流式输出
- [ ] 多语言支持

### 代码改进

- [ ] 添加单元测试
- [ ] 添加集成测试
- [ ] 改进日志系统
- [ ] 添加性能监控
- [ ] 优化前端性能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目遵循原 Lingshu-7B 模型的许可证。

## 🙏 致谢

- 基于 [Qwen2.5-VL](https://github.com/QwenLM/Qwen2-VL) 模型
- 使用 [Flask](https://flask.palletsprojects.com/) Web框架
- UI设计参考了现代化的聊天界面

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件到项目维护者

---

**享受使用 Lingshu-7B! 🎉**

