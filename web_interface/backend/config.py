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

# 显存优化配置 - 针对8GB显存优化
MAX_PIXELS = 1003520  # 约100万像素 (原始1280万 -> 100万，减少约12倍显存占用)
IMAGE_COMPRESSION_MAX_SIZE = 1024  # 图片预处理最大边长（像素）

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

# 并发控制配置
MAX_CONCURRENT_REQUESTS = 3  # 最大并发请求数（防止服务器过载）
REQUEST_TIMEOUT = 300  # 请求超时时间（秒）

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
