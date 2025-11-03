/**
 * 主应用逻辑 - 多聊天会话管理版本
 */

// 应用状态
const appState = {
    modelLoaded: false,
    currentImages: [],  // 修改为数组以支持多图片
    isGenerating: false,
    currentChatId: null,  // 当前聊天ID
    chats: {},  // 所有聊天会话 { chatId: { id, title, messages, sessionId, createdAt, updatedAt } }
    abortController: null,  // 用于中止生成的控制器
};

// DOM元素
const elements = {
    // 状态显示
    modelStatusMini: document.getElementById('model-status-mini'),
    
    // 按钮
    newChatBtn: document.getElementById('new-chat-btn'),
    settingsBtn: document.getElementById('settings-btn'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    renameChatBtn: document.getElementById('rename-chat-btn'),
    sendBtn: document.getElementById('send-btn'),
    uploadBtn: document.getElementById('upload-btn'),
    
    // 输入
    chatInput: document.getElementById('chat-input'),
    imageInput: document.getElementById('image-input'),
    chatTitle: document.getElementById('chat-title'),
    
    // 显示区域
    chatMessages: document.getElementById('chat-messages'),
    chatList: document.getElementById('chat-list'),
    imagePreviewContainer: document.getElementById('image-preview-container'),
    imagePreviewList: document.getElementById('image-preview-list'),
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingText: document.getElementById('loading-text')
};

/**
 * 初始化应用
 */
async function initApp() {
    console.log('初始化应用...');
    
    // 从localStorage加载聊天历史
    loadChatsFromStorage();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 检查服务状态
    await checkStatus();
    
    // 如果没有聊天，创建一个新聊天
    if (Object.keys(appState.chats).length === 0) {
        createNewChat();
    } else {
        // 加载最后一个聊天
        const chatIds = Object.keys(appState.chats).sort((a, b) => 
            appState.chats[b].updatedAt - appState.chats[a].updatedAt
        );
        switchToChat(chatIds[0]);
    }
    
    // 自动调整输入框高度
    autoResizeTextarea();
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 聊天控制
    elements.newChatBtn.addEventListener('click', createNewChat);
    elements.settingsBtn.addEventListener('click', () => window.location.href = '/settings.html');
    elements.sendBtn.addEventListener('click', handleSendMessage);
    elements.clearChatBtn.addEventListener('click', handleClearChat);
    elements.renameChatBtn.addEventListener('click', handleRenameChat);
    elements.chatInput.addEventListener('keydown', handleInputKeydown);
    elements.chatInput.addEventListener('input', handleInputChange);
    
    // 图片上传
    elements.uploadBtn.addEventListener('click', () => elements.imageInput.click());
    elements.imageInput.addEventListener('change', handleImageSelect);
}

/**
 * 从localStorage加载聊天历史
 */
function loadChatsFromStorage() {
    try {
        const stored = localStorage.getItem('chats');
        if (stored) {
            appState.chats = JSON.parse(stored);
            console.log('加载了', Object.keys(appState.chats).length, '个聊天记录');
        }
    } catch (error) {
        console.error('加载聊天历史失败:', error);
        appState.chats = {};
    }
}

/**
 * 保存聊天历史到localStorage
 */
function saveChatsToStorage() {
    try {
        localStorage.setItem('chats', JSON.stringify(appState.chats));
    } catch (error) {
        console.error('保存聊天历史失败:', error);
    }
}

/**
 * 创建新聊天
 */
function createNewChat() {
    const chatId = 'chat_' + Date.now();
    const chat = {
        id: chatId,
        title: '新对话',
        messages: [],
        sessionId: null,
        createdAt: Date.now(),
        updatedAt: Date.now()
    };
    
    appState.chats[chatId] = chat;
    saveChatsToStorage();
    
    switchToChat(chatId);
    updateChatList();
}

/**
 * 切换到指定聊天
 */
function switchToChat(chatId) {
    if (!appState.chats[chatId]) {
        console.error('聊天不存在:', chatId);
        return;
    }
    
    appState.currentChatId = chatId;
    const chat = appState.chats[chatId];
    
    // 更新标题
    elements.chatTitle.textContent = '💬 ' + chat.title;
    
    // 清空消息区域并重新渲染
    elements.chatMessages.innerHTML = '';
    
    if (chat.messages.length === 0) {
        // 显示欢迎消息
        elements.chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>👋 欢迎使用 Lingshu-7B 医学助手</h2>
                <p>这是一个基于Qwen2.5-VL的医学多模态对话系统</p>
                <div class="welcome-features">
                    <div class="feature">
                        <span class="feature-icon">💡</span>
                        <h3>智能对话</h3>
                        <p>专业的医学知识问答</p>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">🖼️</span>
                        <h3>图像分析</h3>
                        <p>支持医学图像的诊断分析</p>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">⚡</span>
                        <h3>高效运行</h3>
                        <p>4bit量化，低显存占用</p>
                    </div>
                </div>
                <p class="welcome-hint">请先前往设置页面加载模型，然后开始对话</p>
            </div>
        `;
    } else {
        // 渲染历史消息
        chat.messages.forEach((msg, index) => {
            // 兼容旧版本的单图片格式
            const imageUrls = msg.imageUrls || (msg.imageUrl ? [msg.imageUrl] : null);
            addMessageToDOM(msg.role, msg.content, imageUrls, index);
        });
    }
    
    updateChatList();
}

/**
 * 更新聊天列表显示
 */
function updateChatList() {
    elements.chatList.innerHTML = '';
    
    // 按更新时间排序
    const sortedChats = Object.values(appState.chats).sort((a, b) => 
        b.updatedAt - a.updatedAt
    );
    
    if (sortedChats.length === 0) {
        elements.chatList.innerHTML = '<p style="text-align: center; color: var(--text-muted); font-size: 0.875rem; padding: var(--spacing-md);">暂无历史对话</p>';
        return;
    }
    
    sortedChats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        if (chat.id === appState.currentChatId) {
            chatItem.classList.add('active');
        }
        
        // 获取最后一条消息作为预览
        let preview = '开始新对话...';
        if (chat.messages.length > 0) {
            const lastMsg = chat.messages[chat.messages.length - 1];
            preview = lastMsg.content.substring(0, 30) + (lastMsg.content.length > 30 ? '...' : '');
        }
        
        // 格式化时间
        const timeStr = formatTime(chat.updatedAt);
        
        chatItem.innerHTML = `
            <div class="chat-item-title">${chat.title}</div>
            <div class="chat-item-preview">${preview}</div>
            <div class="chat-item-time">${timeStr}</div>
            <button class="chat-item-delete" title="删除对话">✕</button>
        `;
        
        // 点击聊天项切换对话
        chatItem.addEventListener('click', (e) => {
            // 如果点击的是删除按钮，不切换对话
            if (!e.target.classList.contains('chat-item-delete')) {
                switchToChat(chat.id);
            }
        });
        
        // 删除按钮事件
        const deleteBtn = chatItem.querySelector('.chat-item-delete');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // 阻止事件冒泡
            handleDeleteChatItem(chat.id);
        });
        
        elements.chatList.appendChild(chatItem);
    });
}

/**
 * 格式化时间
 */
function formatTime(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    
    // 小于1分钟
    if (diff < 60 * 1000) {
        return '刚刚';
    }
    // 小于1小时
    if (diff < 60 * 60 * 1000) {
        return Math.floor(diff / (60 * 1000)) + '分钟前';
    }
    // 小于1天
    if (diff < 24 * 60 * 60 * 1000) {
        return Math.floor(diff / (60 * 60 * 1000)) + '小时前';
    }
    // 小于7天
    if (diff < 7 * 24 * 60 * 60 * 1000) {
        return Math.floor(diff / (24 * 60 * 60 * 1000)) + '天前';
    }
    // 显示日期
    const date = new Date(timestamp);
    return `${date.getMonth() + 1}月${date.getDate()}日`;
}

/**
 * 重命名当前聊天
 */
function handleRenameChat() {
    if (!appState.currentChatId) return;
    
    const chat = appState.chats[appState.currentChatId];
    const newTitle = prompt('请输入新的对话标题:', chat.title);
    
    if (newTitle && newTitle.trim()) {
        chat.title = newTitle.trim();
        chat.updatedAt = Date.now();
        saveChatsToStorage();
        
        elements.chatTitle.textContent = '💬 ' + chat.title;
        updateChatList();
    }
}

/**
 * 删除指定的聊天（从列表中）
 */
async function handleDeleteChatItem(chatId) {
    if (!appState.chats[chatId]) return;
    
    const chat = appState.chats[chatId];
    
    if (!confirm(`确定要删除对话"${chat.title}"吗？\n\n此操作不可恢复。`)) {
        return;
    }
    
    // 清除服务器端会话
    if (chat.sessionId) {
        try {
            await apiClient.clearHistory(chat.sessionId);
        } catch (error) {
            console.error('清除服务器会话失败:', error);
        }
    }
    
    // 删除聊天
    delete appState.chats[chatId];
    saveChatsToStorage();
    
    // 如果删除的是当前聊天，切换到其他聊天或创建新聊天
    if (chatId === appState.currentChatId) {
        const chatIds = Object.keys(appState.chats);
        if (chatIds.length > 0) {
            switchToChat(chatIds[0]);
        } else {
            createNewChat();
        }
    } else {
        // 只更新列表
        updateChatList();
    }
    
    showNotification('对话已删除', 'success');
}

/**
 * 检查服务状态
 */
async function checkStatus() {
    try {
        const status = await apiClient.getStatus();
        updateModelStatus(status.model_loaded);
    } catch (error) {
        console.error('检查状态失败:', error);
        updateModelStatus(false);
    }
}

/**
 * 更新模型状态
 */
function updateModelStatus(loaded) {
    appState.modelLoaded = loaded;
    
    if (loaded) {
        elements.modelStatusMini.textContent = '✅ 已加载';
        elements.modelStatusMini.style.color = '#10b981';
        elements.chatInput.disabled = false;
        elements.sendBtn.disabled = false;
    } else {
        elements.modelStatusMini.textContent = '⚪ 未加载';
        elements.modelStatusMini.style.color = '#64748b';
        elements.chatInput.disabled = true;
        elements.sendBtn.disabled = true;
    }
}

/**
 * 发送消息（使用流式输出）
 */
async function handleSendMessage() {
    const prompt = elements.chatInput.value.trim();
    
    if (!prompt) {
        showNotification('请输入问题', 'warning');
        return;
    }
    
    if (!appState.modelLoaded) {
        showNotification('请先前往设置页面加载模型', 'warning');
        return;
    }
    
    if (appState.isGenerating) {
        return;
    }
    
    if (!appState.currentChatId) {
        createNewChat();
    }
    
    const chat = appState.chats[appState.currentChatId];
    
    // 清空欢迎消息
    const welcomeMessage = elements.chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // 保存图片URLs（如果有多张图片）
    let imageUrls = [];
    if (appState.currentImages && appState.currentImages.length > 0) {
        imageUrls = appState.currentImages.map(img => URL.createObjectURL(img));
    }
    
    // 添加用户消息到DOM和历史
    addMessageToDOM('user', prompt, imageUrls);
    chat.messages.push({
        role: 'user',
        content: prompt,
        imageUrls: imageUrls,  // 改为数组
        timestamp: Date.now()
    });
    
    // 如果是第一条消息，自动设置标题
    if (chat.messages.length === 1) {
        chat.title = prompt.substring(0, 20) + (prompt.length > 20 ? '...' : '');
        elements.chatTitle.textContent = '💬 ' + chat.title;
    }
    
    // 更新聊天时间
    chat.updatedAt = Date.now();
    saveChatsToStorage();
    updateChatList();
    
    // 清空输入
    elements.chatInput.value = '';
    elements.chatInput.style.height = 'auto';
    
    // 获取生成配置
    const settings = JSON.parse(localStorage.getItem('generationSettings') || '{}');
    const config = {
        temperature: settings.temperature || 0.7,
        max_new_tokens: settings.maxTokens || 512
    };
    
    // 禁用输入
    appState.isGenerating = true;
    elements.sendBtn.disabled = true;
    elements.chatInput.disabled = true;
    
    // 创建中止控制器
    appState.abortController = new AbortController();
    
    // 添加流式消息容器
    const streamingMsg = addStreamingMessage();
    let fullResponse = '';
    
    // 显示中止按钮
    showStopButton();
    
    try {
        // 发送流式请求（传递多张图片）
        await apiClient.chatStream(
            prompt, 
            appState.currentImages,  // 传递图片数组
            config, 
            chat.sessionId,
            // onChunk: 接收到文本块
            (chunk) => {
                fullResponse += chunk;
                updateStreamingMessage(streamingMsg, fullResponse);
            },
            // onComplete: 完成
            (sessionId) => {
                // 保存会话ID
                if (sessionId) {
                    chat.sessionId = sessionId;
                }
                
                // 完成流式显示
                finalizeStreamingMessage(streamingMsg);
                
                // 添加到历史
                chat.messages.push({
                    role: 'assistant',
                    content: fullResponse,
                    timestamp: Date.now()
                });
                
                // 更新聊天时间
                chat.updatedAt = Date.now();
                saveChatsToStorage();
                updateChatList();
                
                // 清除所有图片
                if (appState.currentImages.length > 0) {
                    handleRemoveAllImages();
                }
                
                // 隐藏中止按钮
                hideStopButton();
                
                // 恢复输入
                appState.isGenerating = false;
                appState.abortController = null;
                elements.sendBtn.disabled = false;
                elements.chatInput.disabled = false;
                elements.chatInput.focus();
            },
            // onError: 错误
            (error) => {
                console.error('流式生成失败:', error);
                
                // 如果是中止错误，保留已生成的内容
                if (error === '已中止生成' && fullResponse) {
                    // 完成流式显示（保留已生成的内容）
                    finalizeStreamingMessage(streamingMsg);
                    
                    // 添加到历史（标记为已中止）
                    chat.messages.push({
                        role: 'assistant',
                        content: fullResponse + '\n\n[生成已中止]',
                        timestamp: Date.now()
                    });
                    
                    // 更新聊天时间
                    chat.updatedAt = Date.now();
                    saveChatsToStorage();
                    updateChatList();
                    
                    showNotification('已中止生成', 'info');
                } else {
                    streamingMsg.remove();
                    showNotification('生成回复时出错: ' + error, 'error');
                }
                
                // 清除所有图片
                if (appState.currentImages.length > 0) {
                    handleRemoveAllImages();
                }
                
                // 隐藏中止按钮
                hideStopButton();
                
                // 恢复输入
                appState.isGenerating = false;
                appState.abortController = null;
                elements.sendBtn.disabled = false;
                elements.chatInput.disabled = false;
                elements.chatInput.focus();
            },
            // signal: 中止信号
            appState.abortController.signal
        );
        
    } catch (error) {
        console.error('发送消息失败:', error);
        streamingMsg.remove();
        showNotification('发送消息时出错: ' + error.message, 'error');
        
        // 清除所有图片
        if (appState.currentImages.length > 0) {
            handleRemoveAllImages();
        }
        
        // 隐藏中止按钮
        hideStopButton();
        
        // 恢复输入
        appState.isGenerating = false;
        appState.abortController = null;
        elements.sendBtn.disabled = false;
        elements.chatInput.disabled = false;
        elements.chatInput.focus();
    }
}

/**
 * 添加消息到DOM
 */
function addMessageToDOM(role, content, imageUrls = null, messageIndex = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // 为用户消息添加数据属性以便后续编辑
    if (role === 'user' && messageIndex !== null) {
        messageDiv.dataset.messageIndex = messageIndex;
    }
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // 如果是用户消息且有图片，显示多张图片
    if (role === 'user' && imageUrls && imageUrls.length > 0) {
        const imagesContainer = document.createElement('div');
        imagesContainer.className = imageUrls.length === 1 ? 'message-images single' : 'message-images';
        
        imageUrls.forEach(url => {
            const img = document.createElement('img');
            img.className = 'message-image';
            img.src = url;
            imagesContainer.appendChild(img);
        });
        
        messageContent.appendChild(imagesContainer);
    }
    
    // 添加文本内容
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = content;
    messageContent.appendChild(textDiv);
    
    // 添加时间戳和操作按钮容器
    const metaDiv = document.createElement('div');
    metaDiv.className = 'message-meta';
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    metaDiv.appendChild(timeDiv);
    
    // 如果是用户消息，添加编辑按钮
    if (role === 'user' && messageIndex !== null) {
        const editBtn = document.createElement('button');
        editBtn.className = 'message-edit-btn';
        editBtn.innerHTML = '✏️ 编辑';
        editBtn.title = '编辑此消息';
        editBtn.onclick = () => handleEditMessage(messageIndex);
        metaDiv.appendChild(editBtn);
    }
    
    messageContent.appendChild(metaDiv);
    
    messageDiv.appendChild(messageContent);
    elements.chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    scrollToBottom();
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
 * 添加流式消息容器
 */
function addStreamingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant streaming';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'streaming-text';
    textDiv.textContent = '';
    
    // 添加光标效果
    const cursor = document.createElement('span');
    cursor.className = 'streaming-cursor';
    cursor.textContent = '▋';
    textDiv.appendChild(cursor);
    
    messageContent.appendChild(textDiv);
    messageDiv.appendChild(messageContent);
    elements.chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
    
    return messageDiv;
}

/**
 * 更新流式消息内容
 */
function updateStreamingMessage(messageDiv, text) {
    const textDiv = messageDiv.querySelector('.streaming-text');
    if (textDiv) {
        // 保留光标
        const cursor = textDiv.querySelector('.streaming-cursor');
        textDiv.textContent = text;
        if (cursor) {
            textDiv.appendChild(cursor);
        }
        scrollToBottom();
    }
}

/**
 * 完成流式消息（移除光标，添加时间戳）
 */
function finalizeStreamingMessage(messageDiv) {
    // 移除streaming类
    messageDiv.classList.remove('streaming');
    
    // 移除光标
    const cursor = messageDiv.querySelector('.streaming-cursor');
    if (cursor) {
        cursor.remove();
    }
    
    // 添加时间戳
    const messageContent = messageDiv.querySelector('.message-content');
    if (messageContent && !messageContent.querySelector('.message-time')) {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        messageContent.appendChild(timeDiv);
    }
}

/**
 * 清空当前聊天
 */
async function handleClearChat() {
    if (!appState.currentChatId) return;
    
    const chat = appState.chats[appState.currentChatId];
    
    if (chat.messages.length === 0) {
        return;
    }
    
    if (!confirm('确定要清空当前对话吗？')) {
        return;
    }
    
    try {
        // 清除服务器端的对话历史
        if (chat.sessionId) {
            await apiClient.clearHistory(chat.sessionId);
            chat.sessionId = null;
        }
        
        // 清除消息
        chat.messages = [];
        chat.updatedAt = Date.now();
        saveChatsToStorage();
        
        // 重新渲染
        switchToChat(appState.currentChatId);
        
        showNotification('对话已清空', 'success');
    } catch (error) {
        console.error('清除对话失败:', error);
        showNotification('清除对话时出错: ' + error.message, 'error');
    }
}

/**
 * 处理多图片选择
 */
function handleImageSelect(e) {
    const files = Array.from(e.target.files);
    if (!files || files.length === 0) return;
    
    // 检查文件数量限制（例如最多5张）
    const MAX_IMAGES = 5;
    const currentCount = appState.currentImages.length;
    const remainingSlots = MAX_IMAGES - currentCount;
    
    if (files.length > remainingSlots) {
        showNotification(`最多只能上传${MAX_IMAGES}张图片，当前已有${currentCount}张`, 'warning');
        return;
    }
    
    // 验证每个文件
    for (const file of files) {
        // 检查文件类型
        if (!file.type.startsWith('image/')) {
            showNotification('只能选择图片文件', 'error');
            return;
        }
        
        // 检查文件大小（16MB）
        if (file.size > 16 * 1024 * 1024) {
            showNotification('图片文件过大，请选择小于16MB的图片', 'error');
            return;
        }
    }
    
    // 添加到当前图片数组
    appState.currentImages.push(...files);
    
    // 更新预览显示
    updateImagePreview();
    
    // 清空input，以便可以重新选择相同的文件
    elements.imageInput.value = '';
    
    showNotification(`已选择${files.length}张图片`, 'success');
}

/**
 * 更新图片预览显示
 */
function updateImagePreview() {
    elements.imagePreviewList.innerHTML = '';
    
    if (appState.currentImages.length === 0) {
        elements.imagePreviewContainer.classList.add('hidden');
        return;
    }
    
    // 显示图片数量徽章
    const badge = document.createElement('div');
    badge.className = 'image-count-badge';
    badge.textContent = `已选择 ${appState.currentImages.length} 张图片`;
    elements.imagePreviewList.appendChild(badge);
    
    // 显示每张图片的预览
    appState.currentImages.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'image-preview-item';
            
            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = `预览图片 ${index + 1}`;
            
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-image-btn';
            removeBtn.textContent = '✕';
            removeBtn.title = '移除此图片';
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                handleRemoveSingleImage(index);
            };
            
            itemDiv.appendChild(img);
            itemDiv.appendChild(removeBtn);
            elements.imagePreviewList.appendChild(itemDiv);
        };
        reader.readAsDataURL(file);
    });
    
    elements.imagePreviewContainer.classList.remove('hidden');
}

/**
 * 移除单张图片
 */
function handleRemoveSingleImage(index) {
    appState.currentImages.splice(index, 1);
    updateImagePreview();
    
    if (appState.currentImages.length === 0) {
        showNotification('已移除所有图片', 'success');
    }
}

/**
 * 移除所有图片
 */
function handleRemoveAllImages() {
    appState.currentImages = [];
    elements.imagePreviewContainer.classList.add('hidden');
    elements.imagePreviewList.innerHTML = '';
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
 * 显示通知
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    if (type === 'error') {
        alert('错误: ' + message);
    } else if (type === 'warning') {
        console.warn(message);
    }
}

/**
 * 显示中止按钮
 */
function showStopButton() {
    // 查找是否已存在中止按钮
    let stopBtn = document.getElementById('stop-generation-btn');
    
    if (!stopBtn) {
        // 创建中止按钮
        stopBtn = document.createElement('button');
        stopBtn.id = 'stop-generation-btn';
        stopBtn.className = 'btn btn-stop';
        stopBtn.innerHTML = '<span class="btn-icon">⏹</span> 中止生成';
        stopBtn.onclick = handleStopGeneration;
        
        // 将按钮插入到发送按钮之前
        elements.sendBtn.parentNode.insertBefore(stopBtn, elements.sendBtn);
    }
    
    // 隐藏发送按钮，显示中止按钮
    elements.sendBtn.style.display = 'none';
    stopBtn.style.display = 'flex';
}

/**
 * 隐藏中止按钮
 */
function hideStopButton() {
    const stopBtn = document.getElementById('stop-generation-btn');
    if (stopBtn) {
        stopBtn.style.display = 'none';
    }
    
    // 显示发送按钮
    elements.sendBtn.style.display = 'flex';
}

/**
 * 处理中止生成
 */
function handleStopGeneration() {
    if (appState.abortController) {
        console.log('用户请求中止生成');
        appState.abortController.abort();
    }
}

/**
 * 处理编辑消息
 */
function handleEditMessage(messageIndex) {
    if (!appState.currentChatId) return;
    
    // 检查是否正在生成
    if (appState.isGenerating) {
        showNotification('请等待当前生成完成', 'warning');
        return;
    }
    
    const chat = appState.chats[appState.currentChatId];
    const message = chat.messages[messageIndex];
    
    if (!message || message.role !== 'user') {
        console.error('无效的消息索引或消息不是用户消息');
        return;
    }
    
    // 找到对应的DOM元素
    const messageDiv = document.querySelector(`.message.user[data-message-index="${messageIndex}"]`);
    if (!messageDiv) {
        console.error('找不到对应的消息DOM元素');
        return;
    }
    
    const messageContent = messageDiv.querySelector('.message-content');
    const textDiv = messageContent.querySelector('.message-text');
    const metaDiv = messageContent.querySelector('.message-meta');
    
    // 保存原始内容
    const originalContent = message.content;
    
    // 创建编辑区域
    const editContainer = document.createElement('div');
    editContainer.className = 'message-edit-container';
    
    const textarea = document.createElement('textarea');
    textarea.className = 'message-edit-textarea';
    textarea.value = originalContent;
    textarea.rows = Math.max(3, originalContent.split('\n').length);
    editContainer.appendChild(textarea);
    
    // 创建按钮容器
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'message-edit-buttons';
    
    const saveBtn = document.createElement('button');
    saveBtn.className = 'btn btn-primary btn-small';
    saveBtn.textContent = '保存并重新生成';
    saveBtn.onclick = () => handleSaveEditedMessage(messageIndex, textarea.value, messageDiv, textDiv, metaDiv, editContainer);
    
    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-secondary btn-small';
    cancelBtn.textContent = '取消';
    cancelBtn.onclick = () => handleCancelEditMessage(messageDiv, textDiv, metaDiv, editContainer);
    
    buttonContainer.appendChild(saveBtn);
    buttonContainer.appendChild(cancelBtn);
    editContainer.appendChild(buttonContainer);
    
    // 隐藏原始文本和元数据，显示编辑区域
    textDiv.style.display = 'none';
    metaDiv.style.display = 'none';
    messageContent.appendChild(editContainer);
    
    // 聚焦到文本框
    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
}

/**
 * 保存编辑的消息并重新生成
 */
async function handleSaveEditedMessage(messageIndex, newContent, messageDiv, textDiv, metaDiv, editContainer) {
    if (!appState.currentChatId) return;
    
    newContent = newContent.trim();
    if (!newContent) {
        showNotification('消息内容不能为空', 'warning');
        return;
    }
    
    const chat = appState.chats[appState.currentChatId];
    const message = chat.messages[messageIndex];
    
    // 如果内容没有变化，直接取消编辑
    if (newContent === message.content) {
        handleCancelEditMessage(messageDiv, textDiv, metaDiv, editContainer);
        return;
    }
    
    // 更新消息内容
    message.content = newContent;
    message.timestamp = Date.now();
    
    // 删除此消息之后的所有消息
    chat.messages = chat.messages.slice(0, messageIndex + 1);
    
    // 更新聊天时间
    chat.updatedAt = Date.now();
    saveChatsToStorage();
    
    // 更新DOM显示
    textDiv.textContent = newContent;
    textDiv.style.display = 'block';
    metaDiv.style.display = 'flex';
    editContainer.remove();
    
    // 删除此消息之后的所有DOM元素
    let nextSibling = messageDiv.nextElementSibling;
    while (nextSibling) {
        const toRemove = nextSibling;
        nextSibling = nextSibling.nextElementSibling;
        toRemove.remove();
    }
    
    // 重新生成回复
    await regenerateResponse(newContent, message.imageUrls);
}

/**
 * 取消编辑消息
 */
function handleCancelEditMessage(messageDiv, textDiv, metaDiv, editContainer) {
    textDiv.style.display = 'block';
    metaDiv.style.display = 'flex';
    editContainer.remove();
}

/**
 * 重新生成回复（编辑后）
 */
async function regenerateResponse(prompt, imageUrls = null) {
    if (!appState.currentChatId) return;
    if (!appState.modelLoaded) {
        showNotification('请先前往设置页面加载模型', 'warning');
        return;
    }
    
    const chat = appState.chats[appState.currentChatId];
    
    // 获取生成配置
    const settings = JSON.parse(localStorage.getItem('generationSettings') || '{}');
    const config = {
        temperature: settings.temperature || 0.7,
        max_new_tokens: settings.maxTokens || 512
    };
    
    // 禁用输入
    appState.isGenerating = true;
    elements.sendBtn.disabled = true;
    elements.chatInput.disabled = true;
    
    // 创建中止控制器
    appState.abortController = new AbortController();
    
    // 添加流式消息容器
    const streamingMsg = addStreamingMessage();
    let fullResponse = '';
    
    // 显示中止按钮
    showStopButton();
    
    try {
        // 注意：这里不需要上传图片，因为图片已经在之前上传过了
        // 如果消息有图片，它们已经存储在服务器端的会话历史中
        await apiClient.chatStream(
            prompt,
            null,  // 不重新上传图片
            config,
            chat.sessionId,
            // onChunk
            (chunk) => {
                fullResponse += chunk;
                updateStreamingMessage(streamingMsg, fullResponse);
            },
            // onComplete
            (sessionId) => {
                if (sessionId) {
                    chat.sessionId = sessionId;
                }
                
                finalizeStreamingMessage(streamingMsg);
                
                chat.messages.push({
                    role: 'assistant',
                    content: fullResponse,
                    timestamp: Date.now()
                });
                
                chat.updatedAt = Date.now();
                saveChatsToStorage();
                updateChatList();
                
                hideStopButton();
                
                appState.isGenerating = false;
                appState.abortController = null;
                elements.sendBtn.disabled = false;
                elements.chatInput.disabled = false;
                elements.chatInput.focus();
            },
            // onError
            (error) => {
                console.error('重新生成失败:', error);
                
                if (error === '已中止生成' && fullResponse) {
                    finalizeStreamingMessage(streamingMsg);
                    
                    chat.messages.push({
                        role: 'assistant',
                        content: fullResponse + '\n\n[生成已中止]',
                        timestamp: Date.now()
                    });
                    
                    chat.updatedAt = Date.now();
                    saveChatsToStorage();
                    updateChatList();
                    
                    showNotification('已中止生成', 'info');
                } else {
                    streamingMsg.remove();
                    showNotification('重新生成时出错: ' + error, 'error');
                }
                
                hideStopButton();
                
                appState.isGenerating = false;
                appState.abortController = null;
                elements.sendBtn.disabled = false;
                elements.chatInput.disabled = false;
                elements.chatInput.focus();
            },
            appState.abortController.signal
        );
    } catch (error) {
        console.error('重新生成失败:', error);
        streamingMsg.remove();
        showNotification('重新生成时出错: ' + error.message, 'error');
        
        hideStopButton();
        
        appState.isGenerating = false;
        appState.abortController = null;
        elements.sendBtn.disabled = false;
        elements.chatInput.disabled = false;
        elements.chatInput.focus();
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);
