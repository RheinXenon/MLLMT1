/**
 * 主应用逻辑
 */

// 应用状态
const appState = {
    modelLoaded: false,
    currentImage: null,
    chatHistory: [],
    isGenerating: false
};

// DOM元素
const elements = {
    // 状态显示
    serviceStatus: document.getElementById('service-status'),
    modelStatus: document.getElementById('model-status'),
    quantizationMode: document.getElementById('quantization-mode'),
    gpuInfo: document.getElementById('gpu-info'),
    gpuName: document.getElementById('gpu-name'),
    
    // 按钮
    loadModelBtn: document.getElementById('load-model-btn'),
    unloadModelBtn: document.getElementById('unload-model-btn'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    sendBtn: document.getElementById('send-btn'),
    uploadBtn: document.getElementById('upload-btn'),
    removeImageBtn: document.getElementById('remove-image-btn'),
    
    // 输入
    chatInput: document.getElementById('chat-input'),
    imageInput: document.getElementById('image-input'),
    temperatureInput: document.getElementById('temperature'),
    temperatureValue: document.getElementById('temperature-value'),
    maxTokensInput: document.getElementById('max-tokens'),
    maxTokensValue: document.getElementById('max-tokens-value'),
    
    // 显示区域
    chatMessages: document.getElementById('chat-messages'),
    imagePreview: document.getElementById('image-preview'),
    previewImg: document.getElementById('preview-img'),
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingText: document.getElementById('loading-text')
};

/**
 * 初始化应用
 */
async function initApp() {
    console.log('初始化应用...');
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 检查服务状态
    await checkStatus();
    
    // 自动调整输入框高度
    autoResizeTextarea();
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 模型控制按钮
    elements.loadModelBtn.addEventListener('click', handleLoadModel);
    elements.unloadModelBtn.addEventListener('click', handleUnloadModel);
    
    // 聊天控制
    elements.sendBtn.addEventListener('click', handleSendMessage);
    elements.clearChatBtn.addEventListener('click', handleClearChat);
    elements.chatInput.addEventListener('keydown', handleInputKeydown);
    elements.chatInput.addEventListener('input', handleInputChange);
    
    // 图片上传
    elements.uploadBtn.addEventListener('click', () => elements.imageInput.click());
    elements.imageInput.addEventListener('change', handleImageSelect);
    elements.removeImageBtn.addEventListener('click', handleRemoveImage);
    
    // 设置滑块
    elements.temperatureInput.addEventListener('input', (e) => {
        elements.temperatureValue.textContent = e.target.value;
    });
    elements.maxTokensInput.addEventListener('input', (e) => {
        elements.maxTokensValue.textContent = e.target.value;
    });
}

/**
 * 检查服务状态
 */
async function checkStatus() {
    try {
        const status = await apiClient.getStatus();
        
        // 更新状态显示
        elements.serviceStatus.textContent = '✅ 运行中';
        elements.serviceStatus.style.color = '#10b981';
        
        if (status.model_loaded) {
            updateModelStatus(true);
            if (status.quantization) {
                elements.quantizationMode.textContent = status.quantization;
            }
            
            // 显示GPU信息
            if (status.gpu_available) {
                elements.gpuInfo.style.display = 'block';
                elements.gpuName.textContent = status.gpu_name;
            }
        } else {
            updateModelStatus(false);
        }
        
    } catch (error) {
        console.error('检查状态失败:', error);
        elements.serviceStatus.textContent = '❌ 连接失败';
        elements.serviceStatus.style.color = '#ef4444';
        showNotification('无法连接到服务器，请检查后端是否启动', 'error');
    }
}

/**
 * 更新模型状态
 */
function updateModelStatus(loaded) {
    appState.modelLoaded = loaded;
    
    if (loaded) {
        elements.modelStatus.textContent = '✅ 已加载';
        elements.modelStatus.style.color = '#10b981';
        elements.loadModelBtn.disabled = true;
        elements.unloadModelBtn.disabled = false;
        elements.chatInput.disabled = false;
        elements.sendBtn.disabled = false;
    } else {
        elements.modelStatus.textContent = '⚪ 未加载';
        elements.modelStatus.style.color = '#64748b';
        elements.loadModelBtn.disabled = false;
        elements.unloadModelBtn.disabled = true;
        elements.chatInput.disabled = true;
        elements.sendBtn.disabled = true;
    }
}

/**
 * 加载模型
 */
async function handleLoadModel() {
    showLoading('正在加载模型，请稍候...');
    
    try {
        const result = await apiClient.loadModel();
        
        if (result.success) {
            updateModelStatus(true);
            showNotification('模型加载成功！', 'success');
        } else {
            showNotification(result.error || '模型加载失败', 'error');
        }
    } catch (error) {
        console.error('加载模型失败:', error);
        showNotification('加载模型时出错: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * 卸载模型
 */
async function handleUnloadModel() {
    showLoading('正在卸载模型...');
    
    try {
        const result = await apiClient.unloadModel();
        
        if (result.success) {
            updateModelStatus(false);
            showNotification('模型已卸载', 'success');
        } else {
            showNotification(result.error || '卸载模型失败', 'error');
        }
    } catch (error) {
        console.error('卸载模型失败:', error);
        showNotification('卸载模型时出错: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * 发送消息
 */
async function handleSendMessage() {
    const prompt = elements.chatInput.value.trim();
    
    if (!prompt) {
        showNotification('请输入问题', 'warning');
        return;
    }
    
    if (!appState.modelLoaded) {
        showNotification('请先加载模型', 'warning');
        return;
    }
    
    if (appState.isGenerating) {
        return;
    }
    
    // 清空欢迎消息
    const welcomeMessage = elements.chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // 添加用户消息
    addMessage('user', prompt, appState.currentImage);
    
    // 清空输入
    elements.chatInput.value = '';
    elements.chatInput.style.height = 'auto';
    
    // 获取生成配置
    const config = {
        temperature: parseFloat(elements.temperatureInput.value),
        max_new_tokens: parseInt(elements.maxTokensInput.value)
    };
    
    // 禁用输入
    appState.isGenerating = true;
    elements.sendBtn.disabled = true;
    elements.chatInput.disabled = true;
    
    // 添加思考中提示
    const thinkingMsg = addThinkingMessage();
    
    try {
        // 发送请求
        const result = await apiClient.chat(prompt, appState.currentImage, config);
        
        // 移除思考中提示
        thinkingMsg.remove();
        
        if (result.success) {
            // 添加助手回复
            addMessage('assistant', result.response);
        } else {
            showNotification(result.error || '生成回复失败', 'error');
        }
        
    } catch (error) {
        console.error('发送消息失败:', error);
        thinkingMsg.remove();
        showNotification('发送消息时出错: ' + error.message, 'error');
    } finally {
        // 清除图片
        if (appState.currentImage) {
            handleRemoveImage();
        }
        
        // 恢复输入
        appState.isGenerating = false;
        elements.sendBtn.disabled = false;
        elements.chatInput.disabled = false;
        elements.chatInput.focus();
    }
}

/**
 * 添加消息到聊天区
 */
function addMessage(role, content, imageFile = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // 如果是用户消息且有图片，显示图片
    if (role === 'user' && imageFile) {
        const img = document.createElement('img');
        img.className = 'message-image';
        img.src = URL.createObjectURL(imageFile);
        messageContent.appendChild(img);
    }
    
    // 添加文本内容
    const textDiv = document.createElement('div');
    textDiv.textContent = content;
    messageContent.appendChild(textDiv);
    
    // 添加时间戳
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    messageContent.appendChild(timeDiv);
    
    messageDiv.appendChild(messageContent);
    elements.chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    scrollToBottom();
    
    // 保存到历史
    appState.chatHistory.push({ role, content, timestamp: Date.now() });
}

/**
 * 添加思考中消息
 */
function addThinkingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'thinking';
    thinkingDiv.innerHTML = '<div class="thinking-dot"></div><div class="thinking-dot"></div><div class="thinking-dot"></div>';
    
    messageContent.appendChild(thinkingDiv);
    messageDiv.appendChild(messageContent);
    elements.chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
    
    return messageDiv;
}

/**
 * 清空聊天
 */
function handleClearChat() {
    if (appState.chatHistory.length === 0) {
        return;
    }
    
    if (confirm('确定要清空所有对话吗？')) {
        elements.chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>👋 欢迎使用 Lingshu-7B 医学助手</h2>
                <p>对话已清空，可以开始新的对话</p>
            </div>
        `;
        appState.chatHistory = [];
        showNotification('对话已清空', 'success');
    }
}

/**
 * 处理图片选择
 */
function handleImageSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        showNotification('请选择图片文件', 'error');
        return;
    }
    
    // 检查文件大小（16MB）
    if (file.size > 16 * 1024 * 1024) {
        showNotification('图片文件过大，请选择小于16MB的图片', 'error');
        return;
    }
    
    // 保存图片
    appState.currentImage = file;
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.previewImg.src = e.target.result;
        elements.imagePreview.style.display = 'block';
    };
    reader.readAsDataURL(file);
    
    showNotification('图片已选择', 'success');
}

/**
 * 移除图片
 */
function handleRemoveImage() {
    appState.currentImage = null;
    elements.imagePreview.style.display = 'none';
    elements.previewImg.src = '';
    elements.imageInput.value = '';
}

/**
 * 处理输入框键盘事件
 */
function handleInputKeydown(e) {
    // Ctrl+Enter 或 Cmd+Enter 发送消息
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleSendMessage();
    }
}

/**
 * 处理输入框内容变化
 */
function handleInputChange() {
    // 自动调整高度
    elements.chatInput.style.height = 'auto';
    elements.chatInput.style.height = elements.chatInput.scrollHeight + 'px';
}

/**
 * 自动调整输入框高度
 */
function autoResizeTextarea() {
    elements.chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
}

/**
 * 滚动到底部
 */
function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

/**
 * 显示加载遮罩
 */
function showLoading(text = '加载中...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.classList.add('active');
}

/**
 * 隐藏加载遮罩
 */
function hideLoading() {
    elements.loadingOverlay.classList.remove('active');
}

/**
 * 显示通知（简单的alert实现，可以替换为更好的通知组件）
 */
function showNotification(message, type = 'info') {
    // 这里使用简单的console和alert
    // 在实际项目中可以使用更好的通知库如 toastr、sweetalert 等
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    if (type === 'error') {
        alert('错误: ' + message);
    } else if (type === 'warning') {
        console.warn(message);
    }
    // success 和 info 类型只在控制台显示
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);

