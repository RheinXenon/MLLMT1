"""
配置文件
"""

import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

# 模型配置
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "Lingshu-7B")
DEFAULT_QUANTIZATION = "4bit"  # 默认使用4bit量化

# 上传文件配置
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "web_interface", "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# 生成配置
GENERATION_CONFIG = {
    "max_new_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": True,
    "repetition_penalty": 1.1
}

# Flask配置
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

