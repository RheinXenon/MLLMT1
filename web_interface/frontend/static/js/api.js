/**
 * API调用封装模块
 */

const API_BASE_URL = '';  // 使用相对路径

/**
 * API客户端类
 */
class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * 发起GET请求
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('GET请求失败:', error);
            throw error;
        }
    }

    /**
     * 发起POST请求（JSON）
     */
    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('POST请求失败:', error);
            throw error;
        }
    }

    /**
     * 发起POST请求（FormData，用于文件上传）
     */
    async postFormData(endpoint, formData) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('POST请求失败:', error);
            throw error;
        }
    }

    /**
     * 获取服务状态
     */
    async getStatus() {
        return await this.get('/api/status');
    }

    /**
     * 加载模型
     * @param {string} quantization - 量化模式 (4bit, 8bit, standard, cpu)
     */
    async loadModel(quantization = '4bit') {
        return await this.post('/api/load_model', { quantization });
    }

    /**
     * 卸载模型
     */
    async unloadModel() {
        return await this.post('/api/unload_model', {});
    }

    /**
     * 发送聊天消息
     * @param {string} prompt - 用户输入的文本
     * @param {File[]|File|null} images - 图片文件或图片文件数组（可选）
     * @param {Object} config - 生成配置（可选）
     * @param {string|null} sessionId - 会话ID（可选，用于上下文对话）
     */
    async chat(prompt, images = null, config = null, sessionId = null) {
        const formData = new FormData();
        formData.append('prompt', prompt);
        
        // 支持单张图片或多张图片
        if (images) {
            if (Array.isArray(images)) {
                // 多张图片
                images.forEach((image, index) => {
                    formData.append('images', image);
                });
            } else {
                // 单张图片（向后兼容）
                formData.append('images', images);
            }
        }
        
        if (config) {
            formData.append('config', JSON.stringify(config));
        }
        
        if (sessionId) {
            formData.append('session_id', sessionId);
        }
        
        return await this.postFormData('/api/chat', formData);
    }

    /**
     * 清除对话历史
     * @param {string|null} sessionId - 会话ID（可选，不提供则清除所有）
     */
    async clearHistory(sessionId = null) {
        const data = sessionId ? { session_id: sessionId } : {};
        return await this.post('/api/clear_history', data);
    }

    /**
     * 发送流式聊天消息
     * @param {string} prompt - 用户输入的文本
     * @param {File[]|File|null} images - 图片文件或图片文件数组（可选）
     * @param {Object} config - 生成配置（可选）
     * @param {string|null} sessionId - 会话ID（可选，用于上下文对话）
     * @param {Function} onChunk - 接收文本块的回调函数
     * @param {Function} onComplete - 完成时的回调函数
     * @param {Function} onError - 错误时的回调函数
     */
    async chatStream(prompt, images = null, config = null, sessionId = null, onChunk, onComplete, onError) {
        const formData = new FormData();
        formData.append('prompt', prompt);
        
        // 支持单张图片或多张图片
        if (images) {
            if (Array.isArray(images)) {
                // 多张图片
                images.forEach((image, index) => {
                    formData.append('images', image);
                });
            } else {
                // 单张图片（向后兼容）
                formData.append('images', images);
            }
        }
        
        if (config) {
            formData.append('config', JSON.stringify(config));
        }
        
        if (sessionId) {
            formData.append('session_id', sessionId);
        }
        
        try {
            const response = await fetch(`${this.baseURL}/api/chat_stream`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let returnSessionId = null;
            
            while (true) {
                const { value, done } = await reader.read();
                
                if (done) {
                    break;
                }
                
                // 解码数据
                buffer += decoder.decode(value, { stream: true });
                
                // 处理SSE消息
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';  // 保留最后一行（可能不完整）
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.substring(6);
                        try {
                            const data = JSON.parse(dataStr);
                            
                            if (data.session_id) {
                                returnSessionId = data.session_id;
                            } else if (data.chunk) {
                                onChunk(data.chunk);
                            } else if (data.done) {
                                onComplete(returnSessionId);
                                return;
                            } else if (data.error) {
                                onError(data.error);
                                return;
                            }
                        } catch (e) {
                            console.error('解析SSE数据失败:', e, dataStr);
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('流式请求失败:', error);
            onError(error.message);
        }
    }
}

// 创建全局API客户端实例
const apiClient = new APIClient();

