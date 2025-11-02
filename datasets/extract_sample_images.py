"""
从MedMNIST的npz文件中提取示例图片
用于大模型测试
"""

import os
import numpy as np
from PIL import Image

def extract_samples_from_npz(npz_path, output_dir, num_samples=10, split='train'):
    """
    从npz文件中提取示例图片
    
    Args:
        npz_path: npz文件路径
        output_dir: 输出目录
        num_samples: 要提取的图片数量
        split: 数据集分割类型 ('train', 'val', 'test')
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"正在加载: {npz_path}")
    print("-" * 50)
    
    # 加载npz文件
    try:
        data = np.load(npz_path, allow_pickle=True)
        print(f"✓ 成功加载npz文件")
        print(f"  文件中的键: {list(data.keys())}")
    except Exception as e:
        print(f"✗ 加载npz文件失败: {str(e)}")
        return
    
    # 确定要使用的图像和标签数组键名
    images_key = f'{split}_images'
    labels_key = f'{split}_labels'
    
    # 如果找不到指定分割的数据，尝试其他常见格式
    if images_key not in data.keys():
        # 尝试其他可能的键名
        possible_keys = [k for k in data.keys() if 'image' in k.lower() or 'data' in k.lower()]
        if possible_keys:
            images_key = possible_keys[0]
            print(f"  注意: 使用键 '{images_key}' 作为图像数据")
        else:
            print(f"✗ 错误: 找不到图像数据")
            print(f"  可用的键: {list(data.keys())}")
            return
    
    if labels_key not in data.keys():
        possible_keys = [k for k in data.keys() if 'label' in k.lower()]
        if possible_keys:
            labels_key = possible_keys[0]
            print(f"  注意: 使用键 '{labels_key}' 作为标签数据")
        else:
            labels_key = None
            print(f"  注意: 未找到标签数据")
    
    # 获取图像和标签数据
    images = data[images_key]
    labels = data[labels_key] if labels_key and labels_key in data.keys() else None
    
    print(f"  图像形状: {images.shape}")
    print(f"  图像数据类型: {images.dtype}")
    if labels is not None:
        print(f"  标签形状: {labels.shape}")
    print("-" * 50)
    
    # 确保不超过可用图像数量
    total_images = len(images)
    num_samples = min(num_samples, total_images)
    
    print(f"准备提取 {num_samples} 张图片 (总共 {total_images} 张)")
    print("-" * 50)
    
    # 提取图片
    extracted_count = 0
    
    # 均匀采样，避免只提取前几张
    indices = np.linspace(0, total_images - 1, num_samples, dtype=int)
    
    for i, idx in enumerate(indices):
        try:
            # 获取图像
            img_array = images[idx]
            
            # 处理不同的图像格式
            # 如果是3D数组 (height, width, channels) 或 (channels, height, width)
            if len(img_array.shape) == 3:
                if img_array.shape[0] == 1 or img_array.shape[0] == 3:
                    # 通道在第一个维度 (C, H, W)
                    img_array = np.transpose(img_array, (1, 2, 0))
                # 现在应该是 (H, W, C) 格式
                if img_array.shape[2] == 1:
                    # 灰度图，去掉最后一个维度
                    img_array = img_array[:, :, 0]
            
            # 归一化到0-255范围（如果图像是float类型且在0-1范围）
            if img_array.dtype == np.float32 or img_array.dtype == np.float64:
                if img_array.max() <= 1.0:
                    img_array = (img_array * 255).astype(np.uint8)
                else:
                    img_array = img_array.astype(np.uint8)
            elif img_array.dtype != np.uint8:
                # 确保是uint8类型
                if img_array.max() > 255:
                    img_array = (img_array / img_array.max() * 255).astype(np.uint8)
                else:
                    img_array = img_array.astype(np.uint8)
            
            # 转换为PIL Image
            if len(img_array.shape) == 2:
                # 灰度图
                img = Image.fromarray(img_array)
            elif len(img_array.shape) == 3 and img_array.shape[2] == 3:
                # RGB图
                img = Image.fromarray(img_array)
            else:
                print(f"  警告: 图像 {idx} 的形状 {img_array.shape} 无法处理，跳过")
                continue
            
            # 保存图片
            label_info = ""
            if labels is not None:
                label = labels[idx]
                # 如果是多维标签，转换为字符串
                if isinstance(label, np.ndarray):
                    label_str = "_".join(map(str, label.flatten()))
                else:
                    label_str = str(label)
                label_info = f"_label_{label_str}"
            
            filename = f"sample_{idx:05d}{label_info}.png"
            filepath = os.path.join(output_dir, filename)
            
            img.save(filepath)
            print(f"  ✓ [{i+1}/{num_samples}] 保存: {filename}")
            extracted_count += 1
            
        except Exception as e:
            print(f"  ✗ 提取第 {idx} 张图片失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("-" * 50)
    print(f"✓ 提取完成!")
    print(f"  成功提取: {extracted_count}/{num_samples} 张图片")
    print(f"  输出目录: {output_dir}")
    print("=" * 50)
    
    return extracted_count


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='从MedMNIST的npz文件中提取示例图片')
    parser.add_argument('--npz', type=str, 
                       default='datasets/medmnist_data/chestmnist.npz',
                       help='npz文件路径 (默认: datasets/medmnist_data/chestmnist.npz)')
    parser.add_argument('--output', type=str,
                       default='test_images',
                       help='输出目录 (默认: test_images)')
    parser.add_argument('--num', type=int, default=10,
                       help='要提取的图片数量 (默认: 10)')
    parser.add_argument('--split', type=str, default='train',
                       choices=['train', 'val', 'test'],
                       help='数据集分割类型 (默认: train)')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.npz):
        print(f"错误: 文件不存在: {args.npz}")
        print(f"请确认文件路径正确")
        return
    
    # 提取图片
    extract_samples_from_npz(
        npz_path=args.npz,
        output_dir=args.output,
        num_samples=args.num,
        split=args.split
    )


if __name__ == "__main__":
    main()

