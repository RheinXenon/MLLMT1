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
     */
    async loadModel() {
        return await this.post('/api/load_model', {});
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
     * @param {File|null} image - 图片文件（可选）
     * @param {Object} config - 生成配置（可选）
     */
    async chat(prompt, image = null, config = null) {
        const formData = new FormData();
        formData.append('prompt', prompt);
        
        if (image) {
            formData.append('image', image);
        }
        
        if (config) {
            formData.append('config', JSON.stringify(config));
        }
        
        return await this.postFormData('/api/chat', formData);
    }
}

// 创建全局API客户端实例
const apiClient = new APIClient();

