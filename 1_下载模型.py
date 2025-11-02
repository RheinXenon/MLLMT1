"""
Lingshu-7B 模型下载脚本
支持断点续传和进度显示
"""

import os
from huggingface_hub import snapshot_download
from tqdm import tqdm

def download_model():
    """下载 Lingshu-7B 模型"""
    
    print("=" * 60)
    print("Lingshu-7B 模型下载工具")
    print("=" * 60)
    print()
    
    # 配置参数
    repo_id = "lingshu-medical-mllm/Lingshu-7B"
    local_dir = "./models/Lingshu-7B"
    
    print(f"模型仓库: {repo_id}")
    print(f"本地保存路径: {local_dir}")
    print()
    
    # 确认下载
    print("⚠️  注意事项：")
    print("1. 模型大小约 13-15 GB，请确保有足够的存储空间")
    print("2. 下载时间取决于您的网络速度")
    print("3. 支持断点续传，可随时中断并重新运行此脚本")
    print()
    
    response = input("是否开始下载？(y/n): ").strip().lower()
    if response != 'y':
        print("已取消下载")
        return
    
    print("\n开始下载模型...")
    print("-" * 60)
    
    try:
        # 下载模型
        model_path = snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            resume_download=True,  # 支持断点续传
            local_dir_use_symlinks=False,  # 不使用符号链接
        )
        
        print("-" * 60)
        print("✅ 模型下载完成！")
        print(f"📁 模型位置: {os.path.abspath(model_path)}")
        print()
        print("下一步：运行 '2_测试模型.py' 来测试模型")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  下载被中断")
        print("💡 提示: 再次运行此脚本可继续下载（支持断点续传）")
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        print("\n可能的解决方案：")
        print("1. 检查网络连接")
        print("2. 确认是否需要配置代理")
        print("3. 尝试使用 Hugging Face Token（如果模型需要认证）")
        print("   - 访问 https://huggingface.co/settings/tokens")
        print("   - 创建 Token 并设置环境变量：")
        print("   - set HF_TOKEN=your_token_here")

if __name__ == "__main__":
    download_model()

