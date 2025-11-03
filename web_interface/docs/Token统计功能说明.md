# Token统计功能说明

## 功能概述

系统已添加对话Token消耗统计功能，会在控制台实时打印每次对话的Token使用情况。

## 统计信息

每次对话完成后，控制台会显示以下信息：

```
📊 Token消耗统计:
   • 输入Token: xxx
   • 输出Token: xxx
   • 总Token数: xxx
```

### 统计项说明

- **输入Token**: 包含用户问题、历史对话上下文、图片等编码后的token数量
- **输出Token**: 模型生成的回复内容的token数量
- **总Token数**: 输入Token + 输出Token 的总和

## 适用场景

此功能同时支持：

1. **普通对话模式** (`/api/chat`)
   - 完整的token统计信息会在生成完成后打印

2. **流式对话模式** (`/api/chat_stream`)
   - 在流式输出完成后统计并打印token信息

## 示例输出

### 普通对话示例

```
2025-11-03 10:30:45 - model_manager - INFO - 🤔 生成回复: 请分析这张胸片的异常... (图片数: 1, 历史消息数: 0)
2025-11-03 10:30:48 - model_manager - INFO - ✅ 生成完成，响应长度: 245 字符
2025-11-03 10:30:48 - model_manager - INFO - 📊 Token消耗统计:
2025-11-03 10:30:48 - model_manager - INFO -    • 输入Token: 1024
2025-11-03 10:30:48 - model_manager - INFO -    • 输出Token: 156
2025-11-03 10:30:48 - model_manager - INFO -    • 总Token数: 1180
2025-11-03 10:30:48 - model_manager - INFO - ============================================================
```

### 流式对话示例

```
2025-11-03 10:35:22 - model_manager - INFO - 🤔 流式生成回复: 继续分析... (图片数: 0, 历史消息数: 2)
2025-11-03 10:35:25 - model_manager - INFO - ✅ 流式生成完成
2025-11-03 10:35:25 - model_manager - INFO - 📊 Token消耗统计:
2025-11-03 10:35:25 - model_manager - INFO -    • 输入Token: 512
2025-11-03 10:35:25 - model_manager - INFO -    • 输出Token: 98
2025-11-03 10:35:25 - model_manager - INFO -    • 总Token数: 610
2025-11-03 10:35:25 - model_manager - INFO - ============================================================
```

## 技术实现

### 输入Token计算
```python
input_tokens = inputs.input_ids.shape[1]
```

### 输出Token计算

**普通模式**:
```python
output_tokens = len(generated_ids_trimmed[0])
```

**流式模式**:
```python
output_tokens = generated_ids.shape[1] - input_tokens
```

## 注意事项

1. **图片Token**: 当对话包含图片时，输入Token会显著增加，因为图片会被编码为大量tokens
2. **历史上下文**: 多轮对话会累积历史消息，导致输入Token逐渐增加
3. **Token限制**: 总Token数受模型配置的`max_new_tokens`参数限制（默认512）

## 性能优化建议

根据Token统计信息，可以进行以下优化：

- **输入Token过多**: 考虑清除历史对话或减少上传的图片数量
- **输出Token较少**: 可能需要调整提示词以获得更详细的回复
- **总Token接近上限**: 建议清除对话历史或增加`max_new_tokens`配置

## 相关配置

生成配置文件位置: `web_interface/backend/config.py`

相关参数:
```python
GENERATION_CONFIG = {
    "max_new_tokens": 512,  # 最大输出token数
    "temperature": 0.7,
    "top_p": 0.9,
    ...
}
```

