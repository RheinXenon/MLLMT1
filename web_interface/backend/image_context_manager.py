"""
图片上下文管理器 - 优化多模态对话中的图片处理性能

核心策略：
1. 仅当前轮对话处理实际图片
2. 历史图片转换为文本描述（图片摘要）
3. 避免重复编码历史图片，大幅降低显存和计算压力
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import os
import hashlib

logger = logging.getLogger(__name__)


class ImageContextStrategy:
    """图片上下文策略枚举"""
    
    # 策略1：仅使用当前图片（默认，性能最优）
    CURRENT_ONLY = "current_only"
    
    # 策略2：当前图片 + 历史图片的文本描述（推荐，平衡性能和上下文）
    CURRENT_WITH_TEXT_HISTORY = "current_with_text_history"
    
    # 策略3：当前图片 + 最近N张历史图片（高质量，但性能较差）
    CURRENT_WITH_RECENT_IMAGES = "current_with_recent_images"


class ImageContextManager:
    """图片上下文管理器"""
    
    def __init__(
        self, 
        strategy: str = ImageContextStrategy.CURRENT_WITH_TEXT_HISTORY,
        max_recent_images: int = 2,
        enable_summary: bool = True
    ):
        """
        初始化图片上下文管理器
        
        Args:
            strategy: 图片上下文策略
            max_recent_images: 策略3中保留的最近图片数量
            enable_summary: 是否启用图片摘要功能
        """
        self.strategy = strategy
        self.max_recent_images = max_recent_images
        self.enable_summary = enable_summary
        
        # 图片摘要缓存 {image_hash: summary}
        self.summary_cache = {}
        
        logger.info(f"📊 图片上下文管理器初始化:")
        logger.info(f"   • 策略: {strategy}")
        logger.info(f"   • 最大历史图片数: {max_recent_images}")
        logger.info(f"   • 图片摘要: {'开启' if enable_summary else '关闭'}")
    
    def get_image_hash(self, image_path: str) -> str:
        """
        计算图片的哈希值（用于缓存）
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片的MD5哈希值
        """
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"❌ 计算图片哈希失败: {e}")
            return image_path  # 降级为使用路径
    
    def save_image_summary(self, image_path: str, summary: str):
        """
        保存图片摘要到缓存
        
        Args:
            image_path: 图片路径
            summary: 图片摘要
        """
        if not self.enable_summary:
            return
        
        image_hash = self.get_image_hash(image_path)
        self.summary_cache[image_hash] = summary
        logger.info(f"💾 已缓存图片摘要: {image_path[:50]}... -> {summary[:100]}...")
    
    def get_image_summary(self, image_path: str) -> Optional[str]:
        """
        获取图片的摘要（如果有缓存）
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片摘要，如果没有缓存则返回None
        """
        if not self.enable_summary:
            return None
        
        image_hash = self.get_image_hash(image_path)
        return self.summary_cache.get(image_hash)
    
    def process_conversation_images(
        self,
        current_image_paths: List[str],
        history: List[Dict[str, Any]],
        processor,
        model
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        处理对话中的图片（核心方法）
        
        根据策略决定：
        - 哪些图片需要实际编码
        - 哪些图片转换为文本描述
        
        Args:
            current_image_paths: 当前轮的图片路径列表
            history: 对话历史
            processor: 模型处理器
            model: 模型实例
            
        Returns:
            (处理后的消息列表, 需要编码的图片路径列表)
        """
        if self.strategy == ImageContextStrategy.CURRENT_ONLY:
            return self._process_current_only(current_image_paths, history)
        
        elif self.strategy == ImageContextStrategy.CURRENT_WITH_TEXT_HISTORY:
            return self._process_with_text_history(
                current_image_paths, history, processor, model
            )
        
        elif self.strategy == ImageContextStrategy.CURRENT_WITH_RECENT_IMAGES:
            return self._process_with_recent_images(
                current_image_paths, history, self.max_recent_images
            )
        
        else:
            logger.warning(f"⚠️ 未知策略 {self.strategy}，降级为 current_only")
            return self._process_current_only(current_image_paths, history)
    
    def _process_current_only(
        self,
        current_image_paths: List[str],
        history: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        策略1：仅使用当前图片
        
        这是性能最优的策略，历史图片完全不参与编码
        """
        logger.info("📊 使用策略: 仅当前图片 (性能最优)")
        
        messages = []
        
        # 添加历史消息（不包含图片）
        for hist in history:
            role = hist.get('role')
            content = hist.get('content')
            
            if role and content:
                # 构建纯文本消息
                text_content = content
                
                # 如果历史消息原本有图片，添加提示信息
                if role == "user" and hist.get('has_images'):
                    image_count = hist.get('image_count', 0)
                    text_content = f"[📎 此消息包含{image_count}张图片]\n{content}"
                
                messages.append({
                    "role": role,
                    "content": [{"type": "text", "text": text_content}]
                })
        
        logger.info(f"✅ 已添加{len(messages)}条历史消息（纯文本）")
        
        # 返回消息和需要编码的图片（仅当前图片）
        return messages, current_image_paths
    
    def _process_with_text_history(
        self,
        current_image_paths: List[str],
        history: List[Dict[str, Any]],
        processor,
        model
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        策略2：当前图片 + 历史图片的文本描述（推荐）
        
        为历史图片生成/使用缓存的文本描述，只编码当前图片
        """
        logger.info("📊 使用策略: 当前图片 + 历史图片文本描述 (推荐)")
        
        messages = []
        
        # 添加历史消息（图片转换为文本描述）
        for hist_idx, hist in enumerate(history):
            role = hist.get('role')
            content = hist.get('content')
            
            if role and content:
                text_content = content
                
                # 如果历史消息包含图片，添加图片描述
                if role == "user" and hist.get('has_images'):
                    hist_image_paths = hist.get('image_paths', [])
                    image_descriptions = []
                    
                    for img_idx, img_path in enumerate(hist_image_paths):
                        if os.path.exists(img_path):
                            # 尝试从缓存获取摘要
                            summary = self.get_image_summary(img_path)
                            
                            if summary:
                                logger.info(f"💡 使用缓存的图片摘要: {img_path[:50]}...")
                                image_descriptions.append(f"图片{img_idx+1}: {summary}")
                            else:
                                # 如果没有缓存，使用简单描述
                                # 注意：真正的摘要生成会在首次上传时进行
                                image_descriptions.append(
                                    f"图片{img_idx+1}: [图片文件: {os.path.basename(img_path)}]"
                                )
                    
                    if image_descriptions:
                        descriptions_text = "\n".join(image_descriptions)
                        text_content = f"[📎 历史图片描述]\n{descriptions_text}\n\n[用户问题]\n{content}"
                
                messages.append({
                    "role": role,
                    "content": [{"type": "text", "text": text_content}]
                })
        
        logger.info(f"✅ 已添加{len(messages)}条历史消息（图片已转文本描述）")
        
        # 返回消息和需要编码的图片（仅当前图片）
        return messages, current_image_paths
    
    def _process_with_recent_images(
        self,
        current_image_paths: List[str],
        history: List[Dict[str, Any]],
        max_recent: int
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        策略3：当前图片 + 最近N张历史图片
        
        保留最近的N张历史图片，其余转换为文本提示
        """
        logger.info(f"📊 使用策略: 当前图片 + 最近{max_recent}张历史图片")
        
        messages = []
        recent_images = []  # 需要编码的历史图片
        
        # 收集所有历史图片路径（反向，因为我们要保留最近的）
        all_hist_images = []
        for hist in reversed(history):
            if hist.get('role') == 'user' and hist.get('has_images'):
                hist_image_paths = hist.get('image_paths', [])
                for img_path in reversed(hist_image_paths):
                    if os.path.exists(img_path):
                        all_hist_images.append(img_path)
                        if len(all_hist_images) >= max_recent:
                            break
                if len(all_hist_images) >= max_recent:
                    break
        
        # 反转回正常顺序
        all_hist_images.reverse()
        recent_images = all_hist_images
        
        logger.info(f"📸 保留{len(recent_images)}张历史图片用于编码")
        
        # 添加历史消息
        for hist_idx, hist in enumerate(history):
            role = hist.get('role')
            content = hist.get('content')
            
            if role and content:
                hist_content = [{"type": "text", "text": content}]
                
                # 如果历史消息包含图片
                if role == "user" and hist.get('has_images'):
                    hist_image_paths = hist.get('image_paths', [])
                    
                    for img_path in hist_image_paths:
                        if os.path.exists(img_path):
                            # 如果在recent_images中，添加图片
                            if img_path in recent_images:
                                hist_content.insert(0, {"type": "image", "image": img_path})
                            else:
                                # 否则添加文本提示
                                pass  # 旧图片不处理，减少token消耗
                
                messages.append({
                    "role": role,
                    "content": hist_content
                })
        
        logger.info(f"✅ 已添加{len(messages)}条历史消息（保留{len(recent_images)}张最近图片）")
        
        # 返回消息和需要编码的图片（最近的历史图片 + 当前图片）
        all_images_to_encode = recent_images + current_image_paths
        return messages, all_images_to_encode
    
    def generate_image_summary(
        self,
        image_path: str,
        processor,
        model,
        device
    ) -> str:
        """
        为图片生成摘要描述（首次上传时调用）
        
        Args:
            image_path: 图片路径
            processor: 模型处理器
            model: 模型实例
            device: 设备
            
        Returns:
            图片摘要
        """
        if not self.enable_summary:
            return f"[图片: {os.path.basename(image_path)}]"
        
        # 检查缓存
        cached_summary = self.get_image_summary(image_path)
        if cached_summary:
            logger.info(f"💡 使用缓存的图片摘要")
            return cached_summary
        
        try:
            logger.info(f"🔍 正在生成图片摘要...")
            
            # 构建简单的图片描述提示
            from qwen_vl_utils import process_vision_info
            
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {
                        "type": "text", 
                        "text": "请用一句简洁的话描述这张图片的主要内容（不超过50字）。"
                    }
                ]
            }]
            
            # 应用聊天模板
            text = processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理视觉信息
            image_inputs, video_inputs = process_vision_info(messages)
            
            # 处理输入
            inputs = processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(device)
            
            # 生成摘要（使用较短的token限制）
            import torch
            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.3,
                    do_sample=False
                )
            
            # 解码
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            summary = processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0].strip()
            
            # 保存到缓存
            self.save_image_summary(image_path, summary)
            
            logger.info(f"✅ 图片摘要已生成: {summary[:100]}...")
            return summary
            
        except Exception as e:
            logger.error(f"❌ 生成图片摘要失败: {e}")
            # 降级为文件名
            return f"[图片: {os.path.basename(image_path)}]"
    
    def batch_generate_image_summaries(
        self,
        image_paths: List[str],
        processor,
        model,
        device
    ) -> List[str]:
        """
        批量生成图片摘要
        
        Args:
            image_paths: 图片路径列表
            processor: 模型处理器
            model: 模型实例
            device: 设备
            
        Returns:
            图片摘要列表
        """
        summaries = []
        for img_path in image_paths:
            summary = self.generate_image_summary(img_path, processor, model, device)
            summaries.append(summary)
        return summaries

