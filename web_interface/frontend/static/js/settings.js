/**
 * 设置页面逻辑
 */

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
    
    // 量化模式选择
    quantizationSelect: document.getElementById('quantization-select'),
    quantizationDisplay: document.getElementById('quantization-display'),
    
    // 输入
    temperatureInput: document.getElementById('temperature'),
    temperatureValue: document.getElementById('temperature-value'),
    maxTokensInput: document.getElementById('max-tokens'),
    maxTokensValue: document.getElementById('max-tokens-value'),
    
    // 加载遮罩
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingText: document.getElementById('loading-text')
};

/**
 * 初始化应用
 */
async function initApp() {
    console.log('初始化设置页面...');
    
    // 从localStorage加载设置
    loadSettings();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 检查服务状态
    await checkStatus();
}

/**
 * 从localStorage加载设置
 */
function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('generationSettings') || '{}');
    
    if (settings.temperature !== undefined) {
        elements.temperatureInput.value = settings.temperature;
        elements.temperatureValue.textContent = settings.temperature;
    }
    
    if (settings.maxTokens !== undefined) {
        elements.maxTokensInput.value = settings.maxTokens;
        elements.maxTokensValue.textContent = settings.maxTokens;
    }
    
    // 加载量化模式设置（默认4bit）
    const quantization = settings.quantization || '4bit';
    elements.quantizationSelect.value = quantization;
    elements.quantizationDisplay.textContent = quantization;
}

/**
 * 保存设置到localStorage
 */
function saveSettings() {
    const settings = {
        temperature: parseFloat(elements.temperatureInput.value),
        maxTokens: parseInt(elements.maxTokensInput.value),
        quantization: elements.quantizationSelect.value
    };
    
    localStorage.setItem('generationSettings', JSON.stringify(settings));
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 模型控制按钮
    elements.loadModelBtn.addEventListener('click', handleLoadModel);
    elements.unloadModelBtn.addEventListener('click', handleUnloadModel);
    
    // 量化模式选择
    elements.quantizationSelect.addEventListener('change', (e) => {
        elements.quantizationDisplay.textContent = e.target.value;
        saveSettings();
    });
    
    // 设置滑块
    elements.temperatureInput.addEventListener('input', (e) => {
        elements.temperatureValue.textContent = e.target.value;
        saveSettings();
    });
    elements.maxTokensInput.addEventListener('input', (e) => {
        elements.maxTokensValue.textContent = e.target.value;
        saveSettings();
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
                elements.gpuInfo.classList.remove('hidden');
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
    if (loaded) {
        elements.modelStatus.textContent = '✅ 已加载';
        elements.modelStatus.style.color = '#10b981';
        elements.loadModelBtn.disabled = true;
        elements.unloadModelBtn.disabled = false;
    } else {
        elements.modelStatus.textContent = '⚪ 未加载';
        elements.modelStatus.style.color = '#64748b';
        elements.loadModelBtn.disabled = false;
        elements.unloadModelBtn.disabled = true;
    }
}

/**
 * 加载模型
 */
async function handleLoadModel() {
    // 获取用户选择的量化模式
    const quantization = elements.quantizationSelect.value;
    
    // 显示友好的加载提示
    const modeNames = {
        '4bit': '4-bit量化',
        '8bit': '8-bit量化',
        'standard': '标准',
        'cpu': 'CPU'
    };
    const modeName = modeNames[quantization] || quantization;
    
    showLoading(`正在以${modeName}模式加载模型，请稍候...`);
    
    try {
        const result = await apiClient.loadModel(quantization);
        
        if (result.success) {
            updateModelStatus(true);
            // 更新量化模式显示
            if (result.quantization) {
                elements.quantizationMode.textContent = result.quantization;
            }
            showNotification(`模型加载成功！(${modeName}模式)`, 'success');
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
    } else if (type === 'success') {
        alert('成功: ' + message);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);

