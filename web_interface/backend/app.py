"""
Lingshu-7B Web 服务 - Flask应用主文件
"""

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import traceback
from pathlib import Path
import uuid
from datetime import datetime

from model_manager import ModelManager
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置前端目录路径
FRONTEND_DIR = os.path.join(config.PROJECT_ROOT, 'web_interface', 'frontend')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

# 创建Flask应用，指定静态文件夹和模板文件夹
app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    static_url_path='/static',
    template_folder=FRONTEND_DIR
)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'lingshu-7b-secret-key-' + str(uuid.uuid4())  # 用于session加密

# 启用CORS（允许跨域请求）
CORS(app, supports_credentials=True)  # 支持session cookie

# 全局模型管理器
model_manager = None

# 会话存储 - 存储每个会话的对话历史
# 格式: {session_id: [{"role": "user/assistant", "content": [...], "timestamp": ...}, ...]}
conversation_sessions = {}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页 - 返回前端页面"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取服务状态"""
    try:
        status = {
            "service": "running",
            "model_loaded": model_manager is not None and model_manager.is_loaded(),
            "quantization": config.DEFAULT_QUANTIZATION if model_manager else None
        }
        
        # 如果模型已加载，添加GPU信息
        if model_manager and model_manager.is_loaded():
            import torch
            if torch.cuda.is_available():
                status["gpu_available"] = True
                status["gpu_name"] = torch.cuda.get_device_name(0)
                status["gpu_memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB"
                status["gpu_memory_reserved"] = f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB"
            else:
                status["gpu_available"] = False
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/load_model', methods=['POST'])
def load_model():
    """加载模型"""
    global model_manager
    
    try:
        # 如果模型已加载，先卸载
        if model_manager and model_manager.is_loaded():
            logger.info("模型已加载，先卸载...")
            model_manager.unload_model()
        
        # 检查模型路径是否存在
        if not os.path.exists(config.MODEL_PATH):
            return jsonify({
                "success": False,
                "error": f"模型路径不存在: {config.MODEL_PATH}"
            }), 404
        
        # 创建模型管理器
        logger.info(f"开始加载模型: {config.MODEL_PATH}")
        model_manager = ModelManager(
            model_path=config.MODEL_PATH,
            quantization=config.DEFAULT_QUANTIZATION
        )
        
        # 加载模型
        success = model_manager.load_model()
        
        if success:
            return jsonify({
                "success": True,
                "message": "模型加载成功",
                "quantization": config.DEFAULT_QUANTIZATION
            })
        else:
            return jsonify({
                "success": False,
                "error": "模型加载失败，请查看服务器日志"
            }), 500
            
    except Exception as e:
        logger.error(f"加载模型时出错: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求（支持上下文记忆）"""
    if not model_manager or not model_manager.is_loaded():
        return jsonify({
            "success": False,
            "error": "模型未加载，请先加载模型"
        }), 400
    
    try:
        # 获取或创建会话ID
        session_id = request.form.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"创建新会话: {session_id}")
        
        # 初始化会话历史
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []
            logger.info(f"初始化会话历史: {session_id}")
        
        # 获取请求数据
        prompt = request.form.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "请输入问题"
            }), 400
        
        # 处理图片（如果有）
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                if allowed_file(file.filename):
                    # 保存文件
                    filename = secure_filename(file.filename)
                    image_path = os.path.join(config.UPLOAD_FOLDER, filename)
                    file.save(image_path)
                    logger.info(f"保存图片: {image_path}")
                else:
                    return jsonify({
                        "success": False,
                        "error": "不支持的文件格式"
                    }), 400
        
        # 获取会话历史
        history = conversation_sessions[session_id]
        
        # 生成回复（带历史记录）
        logger.info(f"处理请求 [会话:{session_id[:8]}]: {prompt[:50]}... (图片: {image_path is not None}, 历史消息数: {len(history)})")
        result = model_manager.generate_response_with_history(
            prompt=prompt,
            image_path=image_path,
            history=history,
            generation_config=config.GENERATION_CONFIG
        )
        
        # 如果生成成功，保存到历史记录
        if result.get('success'):
            # 保存用户消息
            user_message = {
                "role": "user",
                "content": prompt,
                "has_image": image_path is not None,
                "timestamp": datetime.now().isoformat()
            }
            conversation_sessions[session_id].append(user_message)
            
            # 保存助手回复
            assistant_message = {
                "role": "assistant",
                "content": result['response'],
                "timestamp": datetime.now().isoformat()
            }
            conversation_sessions[session_id].append(assistant_message)
            
            # 添加会话ID到返回结果
            result['session_id'] = session_id
            
            logger.info(f"对话已保存到历史 [会话:{session_id[:8]}], 当前消息数: {len(conversation_sessions[session_id])}")
        
        # 清理上传的临时图片
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                logger.info(f"删除临时图片: {image_path}")
            except Exception as e:
                logger.warning(f"删除临时图片失败: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"处理聊天请求时出错: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """清除对话历史"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        
        if session_id:
            # 清除特定会话的历史
            if session_id in conversation_sessions:
                del conversation_sessions[session_id]
                logger.info(f"已清除会话历史: {session_id[:8]}")
                return jsonify({
                    "success": True,
                    "message": "对话历史已清除"
                })
            else:
                return jsonify({
                    "success": True,
                    "message": "会话不存在或已清除"
                })
        else:
            # 清除所有会话历史
            conversation_sessions.clear()
            logger.info("已清除所有会话历史")
            return jsonify({
                "success": True,
                "message": "所有对话历史已清除"
            })
            
    except Exception as e:
        logger.error(f"清除历史时出错: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/unload_model', methods=['POST'])
def unload_model():
    """卸载模型"""
    global model_manager
    
    try:
        if model_manager and model_manager.is_loaded():
            success = model_manager.unload_model()
            if success:
                model_manager = None
                return jsonify({
                    "success": True,
                    "message": "模型已卸载"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "卸载模型失败"
                }), 500
        else:
            return jsonify({
                "success": True,
                "message": "模型未加载"
            })
            
    except Exception as e:
        logger.error(f"卸载模型时出错: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """处理文件过大错误"""
    return jsonify({
        "success": False,
        "error": f"文件过大，最大允许 {config.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
    }), 413


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Lingshu-7B Web 服务")
    logger.info("=" * 60)
    logger.info(f"模型路径: {config.MODEL_PATH}")
    logger.info(f"量化模式: {config.DEFAULT_QUANTIZATION}")
    logger.info(f"上传文件夹: {config.UPLOAD_FOLDER}")
    logger.info(f"服务地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    logger.info("=" * 60)
    
    # 启动Flask应用
    # 注意：禁用use_reloader，避免在加载大模型时自动重启服务
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        use_reloader=False  # 禁用自动重载，防止加载模型时服务重启
    )

