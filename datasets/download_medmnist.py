"""
下载MedMNIST数据集的脚本
MedMNIST是一个大规模医学影像数据集，包含多个子数据集
"""

import os
import sys

try:
    from medmnist import INFO
    import medmnist.dataset as medmnist_dataset
except ModuleNotFoundError as e:
    print("错误: 无法导入 medmnist 库")
    print(f"  错误详情: {str(e)}")
    print("  提示: 请运行 'pip install medmnist' 安装库")
    sys.exit(1)
except Exception as e:
    print("错误: 导入 medmnist 时发生错误")
    print(f"  错误详情: {str(e)}")
    print("  提示: 可能缺少依赖，请运行 'pip install torch medmnist'")
    sys.exit(1)

def download_medmnist_datasets(download_all=True, selected_datasets=None):
    """
    下载MedMNIST数据集
    
    Args:
        download_all: 如果为True，下载所有可用的数据集；如果为False，只下载selected_datasets中指定的数据集
        selected_datasets: 要下载的数据集列表，例如 ['pathmnist', 'chestmnist', 'dermamnist']
    """
    
    # 创建数据保存目录
    save_dir = os.path.join(os.path.dirname(__file__), 'medmnist_data')
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"数据集将保存到: {save_dir}")
    print("-" * 50)
    
    # 获取所有可用的数据集信息
    available_datasets = list(INFO.keys())
    print(f"可用的数据集: {available_datasets}")
    print("-" * 50)
    
    # 确定要下载的数据集列表
    if download_all:
        datasets_to_download = available_datasets
    else:
        if selected_datasets is None:
            # 如果没有指定，下载最常用的几个数据集
            selected_datasets = ['pathmnist', 'chestmnist', 'dermamnist', 'octmnist', 'pneumoniamnist']
        datasets_to_download = [ds for ds in selected_datasets if ds in available_datasets]
    
    print(f"准备下载 {len(datasets_to_download)} 个数据集:")
    for ds in datasets_to_download:
        print(f"  - {ds}: {INFO[ds]['description']}")
    print("-" * 50)
    
    # 下载每个数据集
    downloaded_count = 0
    failed_count = 0
    
    for dataset_name in datasets_to_download:
        try:
            print(f"\n正在下载: {dataset_name}...")
            
            # 获取数据集类（INFO的键是小写的）
            python_class_name = INFO[dataset_name]['python_class']
            DataClass = getattr(medmnist_dataset, python_class_name)
            
            # 下载数据集
            dataset = DataClass(split='train', download=True, root=save_dir)
            
            # 也下载测试集（如果需要）
            test_dataset = DataClass(split='test', download=True, root=save_dir)
            
            print(f"✓ {dataset_name} 下载完成!")
            print(f"  训练集大小: {len(dataset)}")
            print(f"  测试集大小: {len(test_dataset)}")
            
            downloaded_count += 1
            
        except AttributeError as e:
            print(f"✗ {dataset_name} 下载失败: 无法找到数据集类 '{python_class_name}'")
            print(f"  错误详情: {str(e)}")
            print(f"  提示: 请确认 medmnist 库已正确安装")
            failed_count += 1
            continue
        except ModuleNotFoundError as e:
            print(f"✗ {dataset_name} 下载失败: 缺少必要的依赖")
            print(f"  错误详情: {str(e)}")
            print(f"  提示: 可能需要安装 torch，请运行: pip install torch")
            failed_count += 1
            continue
        except Exception as e:
            print(f"✗ {dataset_name} 下载失败: {str(e)}")
            import traceback
            print(f"  详细错误信息:")
            traceback.print_exc()
            failed_count += 1
            continue
    
    print("\n" + "=" * 50)
    print(f"下载完成!")
    print(f"成功: {downloaded_count} 个数据集")
    print(f"失败: {failed_count} 个数据集")
    print(f"数据保存位置: {save_dir}")
    print("=" * 50)


def download_single_dataset(dataset_name):
    """
    下载单个数据集
    
    Args:
        dataset_name: 数据集名称，例如 'pathmnist'
    """
    save_dir = os.path.join(os.path.dirname(__file__), 'medmnist_data')
    os.makedirs(save_dir, exist_ok=True)
    
    if dataset_name not in INFO:
        print(f"错误: 数据集 '{dataset_name}' 不存在")
        print(f"可用的数据集: {list(INFO.keys())}")
        return
    
    try:
        print(f"正在下载: {dataset_name}...")
        
        # 获取数据集类（INFO的键是小写的）
        python_class_name = INFO[dataset_name]['python_class']
        DataClass = getattr(medmnist_dataset, python_class_name)
        
        dataset = DataClass(split='train', download=True, root=save_dir)
        test_dataset = DataClass(split='test', download=True, root=save_dir)
        
        print(f"✓ {dataset_name} 下载完成!")
        print(f"  训练集大小: {len(dataset)}")
        print(f"  测试集大小: {len(test_dataset)}")
        print(f"  数据保存位置: {save_dir}")
        
    except AttributeError as e:
        print(f"✗ 下载失败: 无法找到数据集类 '{python_class_name}'")
        print(f"  错误详情: {str(e)}")
        print(f"  提示: 请确认 medmnist 库已正确安装")
    except ModuleNotFoundError as e:
        print(f"✗ 下载失败: 缺少必要的依赖")
        print(f"  错误详情: {str(e)}")
        print(f"  提示: 可能需要安装 torch，请运行: pip install torch")
    except Exception as e:
        print(f"✗ 下载失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='下载MedMNIST数据集')
    parser.add_argument('--all', action='store_true', help='下载所有数据集')
    parser.add_argument('--dataset', type=str, help='下载指定的单个数据集')
    parser.add_argument('--datasets', nargs='+', help='下载指定的多个数据集')
    
    args = parser.parse_args()
    
    if args.dataset:
        # 下载单个数据集
        download_single_dataset(args.dataset)
    elif args.datasets:
        # 下载指定的多个数据集
        download_medmnist_datasets(download_all=False, selected_datasets=args.datasets)
    else:
        # 默认：只下载最常用的几个数据集
        print("未指定参数，将下载最常用的几个数据集")
        print("使用 --all 下载所有数据集")
        print("使用 --dataset <name> 下载单个数据集")
        print("使用 --datasets <name1> <name2> ... 下载指定的多个数据集")
        print("-" * 50)
        download_medmnist_datasets(download_all=False)

