"""
Lingshu-7B 多模态模型测试脚本
支持图像输入和病症询问
"""

import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
import os
import sys

def check_gpu():
    """检查GPU可用性"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ 显存: {gpu_memory:.2f} GB")
        return True, gpu_memory
    else:
        print("⚠️  未检测到 GPU，将使用 CPU 模式（速度较慢）")
        return False, 0

def load_model(model_path, mode="auto"):
    """
    加载模型
    mode: auto, standard, 4bit, 8bit, cpu
    """
    print(f"\n加载模型中... (模式: {mode})")
    print("-" * 60)
    
    # 加载处理器（包含分词器和图像处理器）
    print("📖 加载处理器...")
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    
    # 根据模式加载模型
    print(f"🔧 加载模型 ({mode} 模式)...")
    
    if mode == "4bit":
        # 4-bit 量化加载（显存占用最小）
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        
    elif mode == "8bit":
        # 8-bit 量化加载（显存占用较小，精度比4bit高）
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path,
            load_in_8bit=True,
            device_map="auto",
            trust_remote_code=True
        )
        
    elif mode == "cpu":
        # CPU 模式（无需GPU）
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
    else:
        # 标准加载（需要足够显存）
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
    
    print("✅ 模型加载完成！")
    return model, processor

def test_multimodal_inference(model, processor, image_path):
    """测试多模态模型推理"""
    print("\n" + "=" * 60)
    print("开始多模态推理测试")
    print("=" * 60)
    
    # 检查图像文件是否存在
    if not os.path.exists(image_path):
        print(f"\n❌ 错误: 未找到图像文件")
        print(f"路径: {os.path.abspath(image_path)}")
        return
    
    print(f"\n🖼️  图像路径: {os.path.abspath(image_path)}")
    
    # 测试问题列表
    test_prompts = [
        "这张图像显示了什么病症？请详细描述。",
        "根据图像，患者可能出现哪些异常症状？",
        "请分析这张医学图像并给出诊断建议。",
        "这张图像中的主要发现是什么？"
    ]
    
    print("\n请选择测试方式：")
    print("1. 使用预设问题测试（自动使用所有问题）")
    print("2. 输入自定义问题")
    
    choice = input("\n请选择 (1/2): ").strip()
    
    if choice == "2":
        custom_prompt = input("\n请输入您的问题: ").strip()
        if custom_prompt:
            test_prompts = [custom_prompt]
    else:
        # 使用所有预设问题
        print(f"\n将使用 {len(test_prompts)} 个预设问题")
    
    # 执行推理
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}/{len(test_prompts)}")
        print(f"{'=' * 60}")
        print(f"❓ 问题: {prompt}")
        print(f"\n💭 生成中...")
        
        try:
            # 构建消息格式（包含图像和文本）
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": image_path,
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # 应用聊天模板
            text = processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
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
            inputs = inputs.to(model.device)
            
            # 生成回答
            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    repetition_penalty=1.1
                )
            
            # 提取生成的文本（去掉输入部分）
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            # 解码输出
            response = processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            print(f"\n✅ 回答:")
            print("-" * 60)
            print(response)
            print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ 推理失败: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("=" * 60)
    print("Lingshu-7B 多模态模型测试工具")
    print("=" * 60)
    
    # 检查模型路径
    model_path = "./models/Lingshu-7B"
    
    if not os.path.exists(model_path):
        print(f"\n❌ 错误: 未找到模型文件")
        print(f"路径: {os.path.abspath(model_path)}")
        print("\n请先运行 '1_下载模型.py' 下载模型")
        return
    
    print(f"\n✅ 找到模型: {os.path.abspath(model_path)}")
    
    # 设置默认图像路径
    default_image_path = "./test_images/示例.jpg"
    
    # 检查默认图像是否存在
    if not os.path.exists(default_image_path):
        print(f"\n⚠️  未找到默认图像: {default_image_path}")
        image_path = input("\n请输入图像路径: ").strip()
        if not image_path:
            print("\n未提供图像路径，退出")
            return
    else:
        print(f"\n✅ 找到默认图像: {default_image_path}")
        use_default = input("\n使用默认图像？(y/n，默认y): ").strip().lower()
        if use_default in ['', 'y', 'yes']:
            image_path = default_image_path
        else:
            image_path = input("请输入图像路径: ").strip()
            if not image_path:
                print("\n未提供图像路径，退出")
                return
    
    # 检查GPU
    has_gpu, gpu_memory = check_gpu()
    
    # 选择加载模式
    print("\n" + "=" * 60)
    print("请选择加载模式：")
    print("-" * 60)
    
    if has_gpu:
        print("1. 标准模式 (FP16) - 需要约 14GB 显存")
        print("2. 8-bit 量化 - 需要约 7-8GB 显存 (推荐)")
        print("3. 4-bit 量化 - 需要约 4-5GB 显存")
        print("4. CPU 模式 - 无需GPU，但速度很慢")
        
        if gpu_memory < 14:
            print(f"\n💡 建议: 您的显存为 {gpu_memory:.2f}GB，推荐使用 8-bit 或 4-bit 模式")
            default_choice = "2"
        else:
            default_choice = "1"
    else:
        print("1. CPU 模式 - 无需GPU（唯一可用选项）")
        default_choice = "1"
    
    choice = input(f"\n请选择 (默认 {default_choice}): ").strip() or default_choice
    
    # 映射选择到模式
    mode_map = {
        "1": "standard" if has_gpu else "cpu",
        "2": "8bit",
        "3": "4bit",
        "4": "cpu"
    }
    
    mode = mode_map.get(choice, "auto")
    
    try:
        # 加载模型
        model, processor = load_model(model_path, mode)
        
        # 显示设备信息
        if hasattr(model, 'hf_device_map'):
            print(f"\n📊 模型设备分配: {model.hf_device_map}")
        
        # 测试多模态推理
        test_multimodal_inference(model, processor, image_path)
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n可能的解决方案：")
        print("1. 如果是显存不足错误，请尝试更低的量化模式")
        print("2. 如果是依赖包错误，请运行:")
        print("   pip install accelerate bitsandbytes qwen-vl-utils")
        print("3. 如果导入 qwen_vl_utils 失败，请运行:")
        print("   pip install qwen-vl-utils")
        print("4. 查看完整错误信息:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

