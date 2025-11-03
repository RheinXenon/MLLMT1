"""
模型管理器 - 负责加载和管理Lingshu-7B模型

重大更新：集成图片上下文管理器
- 优化多图片场景的性能
- 避免重复编码历史图片
- 大幅降低显存和计算压力
"""

import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig, TextIteratorStreamer
from qwen_vl_utils import process_vision_info
import logging
from typing import Optional, Dict, Any, List, Generator
import gc
from threading import Thread
from PIL import Image
import os

from image_context_manager import ImageContextManager, ImageContextStrategy

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器类"""
    
    def __init__(
        self, 
        model_path: str, 
        quantization: str = "4bit", 
        max_pixels: int = 1003520,
        image_context_strategy: str = ImageContextStrategy.CURRENT_WITH_TEXT_HISTORY,
        max_recent_images: int = 2,
        enable_image_summary: bool = True
    ):
        """
        初始化模型管理器
        
        Args:
            model_path: 模型路径
            quantization: 量化模式 (4bit, 8bit, standard, cpu)
            max_pixels: 最大像素数，默认1003520(约100万像素，适合8GB显存)
            image_context_strategy: 图片上下文策略
            max_recent_images: 保留的最近图片数量
            enable_image_summary: 是否启用图片摘要
        """
        self.model_path = model_path
        self.quantization = quantization
        self.max_pixels = max_pixels
        self.model = None
        self.processor = None
        self.device = None
        
        # 初始化图片上下文管理器
        self.image_context_manager = ImageContextManager(
            strategy=image_context_strategy,
            max_recent_images=max_recent_images,
            enable_summary=enable_image_summary
        )
        logger.info(f"🎯 图片上下文策略: {image_context_strategy}")
        
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
            
            # 设置自定义的max_pixels以节省显存
            if hasattr(self.processor, 'image_processor') and self.max_pixels:
                self.processor.image_processor.max_pixels = self.max_pixels
                logger.info(f"✅ 已设置 max_pixels = {self.max_pixels} (约{self.max_pixels/1e6:.1f}M像素)")
                logger.info(f"💡 这可以减少显存占用，适合处理复杂图片")
            
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
        image_paths: Optional[List[str]] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成回复（不带历史记录）
        
        Args:
            prompt: 用户输入的问题
            image_paths: 图片路径列表（可选）
            generation_config: 生成配置（可选）
            
        Returns:
            包含生成结果的字典
        """
        return self.generate_response_with_history(
            prompt=prompt,
            image_paths=image_paths,
            history=[],
            generation_config=generation_config
        )
    
    def generate_response_with_history(
        self,
        prompt: str,
        image_paths: Optional[List[str]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成回复（支持对话历史和多图片）
        
        Args:
            prompt: 用户输入的问题
            image_paths: 图片路径列表（可选）
            history: 对话历史（可选）
            generation_config: 生成配置（可选）
            
        Returns:
            包含生成结果的字典，包含压缩后的图片路径用于清理
        """
        if self.model is None or self.processor is None:
            return {
                "success": False,
                "error": "模型未加载"
            }
        
        # 记录压缩后的图片路径（用于清理）
        compressed_paths = []
        
        try:
            if history is None:
                history = []
            
            if image_paths is None:
                image_paths = []
            
            logger.info(f"🤔 生成回复: {prompt[:50]}... (图片数: {len(image_paths)}, 历史消息数: {len(history)})")
            
            # 统一预处理当前图片（压缩以节省显存）
            if image_paths and len(image_paths) > 0:
                logger.info("🖼️ 开始预处理当前图片...")
                processed_paths = []
                for img_path in image_paths:
                    processed_path = self.preprocess_image(img_path, max_size=1024)
                    processed_paths.append(processed_path)
                    # 如果生成了压缩文件（路径不同），记录下来
                    if processed_path != img_path:
                        compressed_paths.append(processed_path)
                image_paths = processed_paths
                logger.info(f"✅ 当前图片预处理完成，生成了{len(compressed_paths)}个压缩文件")
            
            # 清理CUDA缓存
            self.clear_cuda_cache()
            
            # 🎯 核心改进：使用图片上下文管理器处理历史图片
            # 根据策略决定如何处理历史图片（转文本描述 or 保留部分图片）
            logger.info("=" * 60)
            logger.info("🚀 使用智能图片上下文管理器")
            
            messages_from_manager, images_to_encode = self.image_context_manager.process_conversation_images(
                current_image_paths=image_paths,
                history=history,
                processor=self.processor,
                model=self.model
            )
            
            logger.info(f"📊 上下文处理结果:")
            logger.info(f"   • 历史消息数: {len(messages_from_manager)}")
            logger.info(f"   • 需编码图片数: {len(images_to_encode)}")
            logger.info(f"   • 策略: {self.image_context_manager.strategy}")
            logger.info("=" * 60)
            
            # 添加当前用户消息（包含当前图片）
            current_content = []
            
            # 添加当前图片
            current_image_count = len(image_paths)
            if image_paths and len(image_paths) > 0:
                for idx, image_path in enumerate(image_paths):
                    current_content.append({
                        "type": "image",
                        "image": image_path
                    })
                    logger.info(f"🖼️ 当前消息图片 #{idx+1}: {image_path}")
                logger.info(f"📸 当前消息包含 {len(image_paths)} 张新图片")
            
            # 构建提示词
            enhanced_prompt = prompt
            if current_image_count > 1:
                enhanced_prompt += "\n\n请仔细分析每一张图片，对比它们之间的差异和联系，并给出综合的分析结果。"
            
            current_content.append({"type": "text", "text": enhanced_prompt})
            
            # 构建最终消息列表
            messages = messages_from_manager + [{
                "role": "user",
                "content": current_content
            }]
            
            logger.info(f"📝 最终消息总数: {len(messages)}, 需编码图片总数: {len(images_to_encode)}")
            
            # 应用聊天模板
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理视觉信息（处理所有消息，包括历史中的图片）
            image_inputs = None
            video_inputs = None
            # 检查是否有任何消息包含图片
            has_any_images = any(
                any(item.get('type') == 'image' for item in msg.get('content', []))
                for msg in messages
            )
            if has_any_images:
                # 处理所有消息中的图片（包括历史消息）
                image_inputs, video_inputs = process_vision_info(messages)
            
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
            
            # 统计token消耗
            input_tokens = inputs.input_ids.shape[1]  # 输入token数量
            output_tokens = len(generated_ids_trimmed[0])  # 输出token数量
            total_tokens = input_tokens + output_tokens  # 总token数量
            
            logger.info(f"✅ 生成完成，响应长度: {len(response)} 字符")
            logger.info(f"📊 Token消耗统计:")
            logger.info(f"   • 输入Token: {input_tokens}")
            logger.info(f"   • 输出Token: {output_tokens}")
            logger.info(f"   • 总Token数: {total_tokens}")
            logger.info(f"=" * 60)
            
            # 🔥 修复：为新上传的图片生成摘要（用于后续对话）
            if image_paths and len(image_paths) > 0 and self.image_context_manager.enable_summary:
                logger.info("🔍 开始为新上传的图片生成摘要...")
                try:
                    summaries = self.image_context_manager.batch_generate_image_summaries(
                        image_paths=image_paths,
                        processor=self.processor,
                        model=self.model,
                        device=self.device
                    )
                    logger.info(f"✅ 已生成 {len(summaries)} 个图片摘要，已缓存供后续对话使用")
                except Exception as e:
                    logger.warning(f"⚠️ 生成图片摘要失败（不影响当前对话）: {e}")
            
            return {
                "success": True,
                "response": response,
                "has_images": len(image_paths) > 0,
                "image_count": len(image_paths),
                "compressed_paths": compressed_paths  # 返回压缩文件路径用于清理
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
    
    def preprocess_image(self, image_path: str, max_size: int = 1024) -> str:
        """
        预处理图片：压缩分辨率以节省显存
        
        Args:
            image_path: 原始图片路径
            max_size: 最大边长（像素）
            
        Returns:
            处理后的图片路径
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                logger.warning(f"⚠️ 图片文件不存在: {image_path}")
                return image_path
            
            with Image.open(image_path) as img:
                # 获取图片格式
                img_format = img.format or 'JPEG'  # 默认使用JPEG格式
                
                # 获取原始尺寸
                orig_width, orig_height = img.size
                
                # 如果图片不需要压缩，直接返回
                if max(orig_width, orig_height) <= max_size:
                    logger.info(f"📷 图片尺寸合适 {orig_width}x{orig_height}，无需压缩")
                    return image_path
                
                # 计算新尺寸（保持宽高比）
                if orig_width > orig_height:
                    new_width = max_size
                    new_height = int(orig_height * max_size / orig_width)
                else:
                    new_height = max_size
                    new_width = int(orig_width * max_size / orig_height)
                
                # 压缩图片
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 保存压缩后的图片
                base, ext = os.path.splitext(image_path)
                
                # 如果没有扩展名，根据图片格式添加
                if not ext:
                    format_ext_map = {
                        'PNG': '.png',
                        'JPEG': '.jpg',
                        'JPG': '.jpg',
                        'GIF': '.gif',
                        'BMP': '.bmp',
                        'WEBP': '.webp'
                    }
                    ext = format_ext_map.get(img_format, '.jpg')  # 默认使用.jpg
                    logger.info(f"🔍 检测到格式: {img_format}, 添加扩展名: {ext}")
                
                compressed_path = f"{base}_compressed{ext}"
                
                # 根据格式保存，PNG不支持quality参数
                if img_format == 'PNG':
                    img_resized.save(compressed_path, format='PNG', optimize=True)
                else:
                    # JPEG等格式支持quality参数
                    img_resized.save(compressed_path, format=img_format, quality=95)
                
                logger.info(f"🔄 图片已压缩: {orig_width}x{orig_height} → {new_width}x{new_height}")
                logger.info(f"💾 压缩后路径: {compressed_path}")
                
                return compressed_path
                
        except Exception as e:
            logger.error(f"❌ 图片预处理失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return image_path  # 失败时返回原路径
    
    def clear_cuda_cache(self):
        """清理CUDA缓存"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
            logger.info("🧹 已清理CUDA缓存")
    
    
    def generate_response_stream(
        self,
        prompt: str,
        image_paths: Optional[List[str]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        compressed_paths_container: Optional[List[str]] = None
    ) -> Generator[str, None, None]:
        """
        生成回复（流式输出，支持对话历史和多图片）
        
        Args:
            prompt: 用户输入的问题
            image_paths: 图片路径列表（可选）
            history: 对话历史（可选）
            generation_config: 生成配置（可选）
            compressed_paths_container: 用于返回压缩文件路径的列表容器（可选）
            
        Yields:
            生成的文本片段
        """
        if self.model is None or self.processor is None:
            yield "[错误] 模型未加载"
            return
        
        try:
            if history is None:
                history = []
            
            if image_paths is None:
                image_paths = []
            
            logger.info(f"🤔 流式生成回复: {prompt[:50]}... (图片数: {len(image_paths)}, 历史消息数: {len(history)})")
            
            # 统一预处理当前图片（压缩以节省显存）
            if image_paths and len(image_paths) > 0:
                logger.info("🖼️ [流式] 开始预处理当前图片...")
                processed_paths = []
                for img_path in image_paths:
                    processed_path = self.preprocess_image(img_path, max_size=1024)
                    processed_paths.append(processed_path)
                    # 如果生成了压缩文件（路径不同），记录下来
                    if processed_path != img_path and compressed_paths_container is not None:
                        compressed_paths_container.append(processed_path)
                image_paths = processed_paths
                if compressed_paths_container is not None:
                    logger.info(f"✅ [流式] 当前图片预处理完成，生成了{len(compressed_paths_container)}个压缩文件")
            
            # 清理CUDA缓存
            self.clear_cuda_cache()
            
            # 🎯 核心改进：使用图片上下文管理器处理历史图片
            logger.info("=" * 60)
            logger.info("🚀 [流式] 使用智能图片上下文管理器")
            
            messages_from_manager, images_to_encode = self.image_context_manager.process_conversation_images(
                current_image_paths=image_paths,
                history=history,
                processor=self.processor,
                model=self.model
            )
            
            logger.info(f"📊 [流式] 上下文处理结果:")
            logger.info(f"   • 历史消息数: {len(messages_from_manager)}")
            logger.info(f"   • 需编码图片数: {len(images_to_encode)}")
            logger.info(f"   • 策略: {self.image_context_manager.strategy}")
            logger.info("=" * 60)
            
            # 添加当前用户消息（包含当前图片）
            current_content = []
            
            # 添加当前图片
            current_image_count = len(image_paths)
            if image_paths and len(image_paths) > 0:
                for idx, image_path in enumerate(image_paths):
                    current_content.append({
                        "type": "image",
                        "image": image_path
                    })
                    logger.info(f"🖼️ [流式] 当前消息图片 #{idx+1}: {image_path}")
                logger.info(f"📸 [流式] 当前消息包含 {len(image_paths)} 张新图片")
            
            # 构建提示词
            enhanced_prompt = prompt
            if current_image_count > 1:
                enhanced_prompt += "\n\n请仔细分析每一张图片，对比它们之间的差异和联系，并给出综合的分析结果。"
            
            current_content.append({"type": "text", "text": enhanced_prompt})
            
            # 构建最终消息列表
            messages = messages_from_manager + [{
                "role": "user",
                "content": current_content
            }]
            
            logger.info(f"📝 [流式] 最终消息总数: {len(messages)}, 需编码图片总数: {len(images_to_encode)}")
            
            # 应用聊天模板
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理视觉信息（处理所有消息，包括历史中的图片）
            image_inputs = None
            video_inputs = None
            # 检查是否有任何消息包含图片
            has_any_images = any(
                any(item.get('type') == 'image' for item in msg.get('content', []))
                for msg in messages
            )
            if has_any_images:
                # 处理所有消息中的图片（包括历史消息）
                image_inputs, video_inputs = process_vision_info(messages)
            
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
            
            # 用于保存生成的token IDs
            generated_ids_container = []
            
            # 定义生成函数，保存结果
            def generate_with_save():
                result = self.model.generate(**generation_kwargs)
                generated_ids_container.append(result)
            
            # 在单独的线程中生成
            thread = Thread(target=generate_with_save)
            thread.start()
            
            # 流式输出生成的文本
            generated_text = ""
            for text_chunk in streamer:
                generated_text += text_chunk
                yield text_chunk
            
            thread.join()
            
            # 统计token消耗
            input_tokens = inputs.input_ids.shape[1]  # 输入token数量
            
            # 从保存的结果中获取输出token数量
            if generated_ids_container:
                generated_ids = generated_ids_container[0]
                output_tokens = generated_ids.shape[1] - input_tokens  # 输出token数量
            else:
                # 如果无法获取生成的IDs，使用文本长度估算
                output_tokens = len(generated_text)  # 粗略估计
            
            total_tokens = input_tokens + output_tokens  # 总token数量
            
            logger.info("✅ 流式生成完成")
            logger.info(f"📊 Token消耗统计:")
            logger.info(f"   • 输入Token: {input_tokens}")
            logger.info(f"   • 输出Token: {output_tokens}")
            logger.info(f"   • 总Token数: {total_tokens}")
            logger.info(f"=" * 60)
            
            # 🔥 修复：为新上传的图片生成摘要（用于后续对话）
            if image_paths and len(image_paths) > 0 and self.image_context_manager.enable_summary:
                logger.info("🔍 [流式] 开始为新上传的图片生成摘要...")
                try:
                    summaries = self.image_context_manager.batch_generate_image_summaries(
                        image_paths=image_paths,
                        processor=self.processor,
                        model=self.model,
                        device=self.device
                    )
                    logger.info(f"✅ [流式] 已生成 {len(summaries)} 个图片摘要，已缓存供后续对话使用")
                except Exception as e:
                    logger.warning(f"⚠️ [流式] 生成图片摘要失败（不影响当前对话）: {e}")
            
        except Exception as e:
            logger.error(f"❌ 流式生成失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"[错误] {str(e)}"

