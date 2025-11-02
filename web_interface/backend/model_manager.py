"""
模型管理器 - 负责加载和管理Lingshu-7B模型
"""

import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig, TextIteratorStreamer
from qwen_vl_utils import process_vision_info
import logging
from typing import Optional, Dict, Any, List, Generator
import gc
from threading import Thread

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器类"""
    
    def __init__(self, model_path: str, quantization: str = "4bit"):
        """
        初始化模型管理器
        
        Args:
            model_path: 模型路径
            quantization: 量化模式 (4bit, 8bit, standard, cpu)
        """
        self.model_path = model_path
        self.quantization = quantization
        self.model = None
        self.processor = None
        self.device = None
        
    def check_gpu(self) -> tuple[bool, float]:
        """检查GPU可用性"""
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"✅ GPU: {gpu_name}")
            logger.info(f"✅ 显存: {gpu_memory:.2f} GB")
            return True, gpu_memory
        else:
            logger.warning("⚠️ 未检测到GPU，将使用CPU模式")
            return False, 0
    
    def load_model(self) -> bool:
        """
        加载模型
        
        Returns:
            是否加载成功
        """
        try:
            logger.info(f"🔧 开始加载模型 (量化模式: {self.quantization})...")
            
            # 加载处理器
            logger.info("📖 加载处理器...")
            self.processor = AutoProcessor.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # 根据量化模式加载模型
            if self.quantization == "4bit":
                logger.info("使用4-bit量化模式")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    quantization_config=quantization_config,
                    device_map="auto",
                    trust_remote_code=True
                )
                
            elif self.quantization == "8bit":
                logger.info("使用8-bit量化模式")
                self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    load_in_8bit=True,
                    device_map="auto",
                    trust_remote_code=True
                )
                
            elif self.quantization == "cpu":
                logger.info("使用CPU模式")
                self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float32,
                    device_map="cpu",
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                
            else:
                logger.info("使用标准模式")
                self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                    trust_remote_code=True
                )
            
            self.device = self.model.device
            logger.info(f"✅ 模型加载完成! 设备: {self.device}")
            
            # 显示设备分配信息
            if hasattr(self.model, 'hf_device_map'):
                logger.info(f"📊 设备映射: {self.model.hf_device_map}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_response(
        self, 
        prompt: str, 
        image_path: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成回复（不带历史记录）
        
        Args:
            prompt: 用户输入的问题
            image_path: 图片路径（可选）
            generation_config: 生成配置（可选）
            
        Returns:
            包含生成结果的字典
        """
        return self.generate_response_with_history(
            prompt=prompt,
            image_path=image_path,
            history=[],
            generation_config=generation_config
        )
    
    def generate_response_with_history(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成回复（支持对话历史）
        
        Args:
            prompt: 用户输入的问题
            image_path: 图片路径（可选）
            history: 对话历史（可选）
            generation_config: 生成配置（可选）
            
        Returns:
            包含生成结果的字典
        """
        if self.model is None or self.processor is None:
            return {
                "success": False,
                "error": "模型未加载"
            }
        
        try:
            if history is None:
                history = []
            
            logger.info(f"🤔 生成回复: {prompt[:50]}... (历史消息数: {len(history)})")
            
            # 构建消息列表，包含历史对话
            messages = []
            
            # 添加历史消息
            for hist in history:
                role = hist.get('role')
                content = hist.get('content')
                
                if role and content:
                    # 历史消息只包含文本（图片不重复发送）
                    messages.append({
                        "role": role,
                        "content": [{"type": "text", "text": content}]
                    })
            
            # 添加当前用户消息
            current_content = []
            if image_path:
                current_content.append({
                    "type": "image",
                    "image": image_path
                })
                logger.info(f"🖼️ 包含图片: {image_path}")
            
            current_content.append({"type": "text", "text": prompt})
            
            messages.append({
                "role": "user",
                "content": current_content
            })
            
            logger.info(f"📝 消息总数: {len(messages)}")
            
            # 应用聊天模板
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理视觉信息（只处理当前消息）
            image_inputs = None
            video_inputs = None
            if image_path:
                # 只处理当前的图片消息
                current_messages = [messages[-1]]
                image_inputs, video_inputs = process_vision_info(current_messages)
            
            # 处理输入
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.model.device)
            
            # 默认生成配置
            default_config = {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "repetition_penalty": 1.1
            }
            
            # 合并用户配置
            if generation_config:
                default_config.update(generation_config)
            
            # 生成回答
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    **default_config
                )
            
            # 提取生成的文本
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            # 解码输出
            response = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            logger.info(f"✅ 生成完成，长度: {len(response)}")
            
            return {
                "success": True,
                "response": response,
                "has_image": image_path is not None
            }
            
        except Exception as e:
            logger.error(f"❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def unload_model(self):
        """卸载模型，释放内存"""
        try:
            if self.model is not None:
                del self.model
                self.model = None
            if self.processor is not None:
                del self.processor
                self.processor = None
            
            # 清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # 强制垃圾回收
            gc.collect()
            
            logger.info("✅ 模型已卸载")
            return True
        except Exception as e:
            logger.error(f"❌ 卸载模型失败: {e}")
            return False
    
    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None and self.processor is not None
    
    def generate_response_stream(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """
        生成回复（流式输出，支持对话历史）
        
        Args:
            prompt: 用户输入的问题
            image_path: 图片路径（可选）
            history: 对话历史（可选）
            generation_config: 生成配置（可选）
            
        Yields:
            生成的文本片段
        """
        if self.model is None or self.processor is None:
            yield "[错误] 模型未加载"
            return
        
        try:
            if history is None:
                history = []
            
            logger.info(f"🤔 流式生成回复: {prompt[:50]}... (历史消息数: {len(history)})")
            
            # 构建消息列表，包含历史对话
            messages = []
            
            # 添加历史消息
            for hist in history:
                role = hist.get('role')
                content = hist.get('content')
                
                if role and content:
                    # 历史消息只包含文本（图片不重复发送）
                    messages.append({
                        "role": role,
                        "content": [{"type": "text", "text": content}]
                    })
            
            # 添加当前用户消息
            current_content = []
            if image_path:
                current_content.append({
                    "type": "image",
                    "image": image_path
                })
                logger.info(f"🖼️ 包含图片: {image_path}")
            
            current_content.append({"type": "text", "text": prompt})
            
            messages.append({
                "role": "user",
                "content": current_content
            })
            
            logger.info(f"📝 消息总数: {len(messages)}")
            
            # 应用聊天模板
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理视觉信息（只处理当前消息）
            image_inputs = None
            video_inputs = None
            if image_path:
                # 只处理当前的图片消息
                current_messages = [messages[-1]]
                image_inputs, video_inputs = process_vision_info(current_messages)
            
            # 处理输入
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.model.device)
            
            # 默认生成配置
            default_config = {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "repetition_penalty": 1.1
            }
            
            # 合并用户配置
            if generation_config:
                default_config.update(generation_config)
            
            # 创建流式输出器
            streamer = TextIteratorStreamer(
                self.processor.tokenizer,
                skip_prompt=True,
                skip_special_tokens=True
            )
            
            # 添加streamer到生成配置
            generation_kwargs = {
                **inputs,
                **default_config,
                "streamer": streamer
            }
            
            # 在单独的线程中生成
            thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()
            
            # 流式输出生成的文本
            for text_chunk in streamer:
                yield text_chunk
            
            thread.join()
            
            logger.info("✅ 流式生成完成")
            
        except Exception as e:
            logger.error(f"❌ 流式生成失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"[错误] {str(e)}"

