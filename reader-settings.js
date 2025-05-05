/**
 * Web Reads - 阅读设置脚本
 * 提供全局阅读设置功能，包括主题、字体、字体大小、行距和页边距调整
 */

// 创建设置面板
function createSettingsPanel() {
    // 检查是否已存在设置面板
    if (document.getElementById('settings-panel')) {
        return;
    }

    // 创建设置面板元素
    const settingsPanel = document.createElement('div');
    settingsPanel.className = 'settings-panel';
    settingsPanel.id = 'settings-panel';

    // 设置面板HTML内容
    settingsPanel.innerHTML = `
        <button class="settings-close" id="settings-close">×</button>
        <h3 style="margin-top: 0;">阅读设置</h3>

        <div class="settings-section">
            <div class="settings-title">主题</div>
            <div class="theme-options">
                <div class="theme-option theme-light" data-theme="light" title="浅色"></div>
                <div class="theme-option theme-dark" data-theme="dark" title="深色"></div>
                <div class="theme-option theme-sepia" data-theme="sepia" title="纸张色"></div>
            </div>
        </div>

        <div class="settings-section">
            <div class="settings-title">字体</div>
            <div class="font-options">
                <div class="font-option font-sans" data-font="sans">无衬线字体</div>
                <div class="font-option font-serif" data-font="serif">衬线字体</div>
            </div>
        </div>

        <div class="settings-section">
            <div class="settings-title">字体大小</div>
            <div class="settings-option">
                <div class="settings-label">A-</div>
                <div class="slider-container">
                    <input type="range" min="14" max="24" value="16" class="slider" id="font-size-slider">
                </div>
                <div class="settings-label">A+</div>
            </div>
            <div style="text-align: center; margin-top: 5px;" id="font-size-value">16px</div>
        </div>

        <div class="settings-section">
            <div class="settings-title">行距</div>
            <div class="settings-option">
                <div class="settings-label">紧凑</div>
                <div class="slider-container">
                    <input type="range" min="1.2" max="2.2" value="1.7" step="0.1" class="slider" id="line-height-slider">
                </div>
                <div class="settings-label">宽松</div>
            </div>
            <div style="text-align: center; margin-top: 5px;" id="line-height-value">1.7</div>
        </div>

        <div class="settings-section">
            <div class="settings-title">段落间距</div>
            <div class="settings-option">
                <div class="settings-label">紧凑</div>
                <div class="slider-container">
                    <input type="range" min="0.8" max="2.5" value="1.4" step="0.1" class="slider" id="paragraph-spacing-slider">
                </div>
                <div class="settings-label">宽松</div>
            </div>
            <div style="text-align: center; margin-top: 5px;" id="paragraph-spacing-value">1.4rem</div>
        </div>

        <div class="settings-section">
            <div class="settings-title">页边距</div>
            <div class="settings-option">
                <div class="settings-label">窄</div>
                <div class="slider-container">
                    <input type="range" min="5" max="15" value="5" step="1" class="slider" id="margin-slider">
                </div>
                <div class="settings-label">宽</div>
            </div>
            <div style="text-align: center; margin-top: 5px;" id="margin-value">5%</div>
        </div>
    `;

    // 添加设置面板到body
    document.body.appendChild(settingsPanel);

    // 添加设置按钮到导航栏
    const headerRight = document.querySelector('.header-content > div:last-child');
    if (headerRight) {
        // 检查是否已存在设置按钮
        if (!document.getElementById('settings-button')) {
            const settingsButton = document.createElement('button');
            settingsButton.className = 'settings-button';
            settingsButton.id = 'settings-button';
            settingsButton.title = '阅读设置';
            settingsButton.textContent = '⚙️';

            // 插入到主题切换按钮之前
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                headerRight.insertBefore(settingsButton, themeToggle);
            } else {
                headerRight.appendChild(settingsButton);
            }
        }
    }

    // 添加CSS样式
    if (!document.getElementById('reader-settings-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'reader-settings-styles';
        styleElement.textContent = `
            /* 阅读设置面板样式 */
            .settings-button {
                background: none;
                border: none;
                color: var(--text-color);
                cursor: pointer;
                font-size: 1.3rem;
                padding: 5px;
                margin-right: 10px;
            }

            .settings-panel {
                position: fixed;
                top: 0;
                right: -300px;
                width: 300px;
                height: 100%;
                background-color: var(--bg-color);
                box-shadow: -2px 0 10px rgba(0,0,0,0.1);
                z-index: 2000;
                padding: 20px;
                overflow-y: auto;
                transition: right 0.3s ease;
            }

            .settings-panel.open {
                right: 0;
            }

            .settings-close {
                position: absolute;
                top: 10px;
                right: 10px;
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--text-color);
            }

            .settings-section {
                margin-bottom: 20px;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 15px;
            }

            .settings-section:last-child {
                border-bottom: none;
            }

            .settings-title {
                font-weight: 700;
                margin-bottom: 10px;
                font-size: 1.1rem;
            }

            .settings-option {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }

            .settings-label {
                flex: 1;
            }

            .settings-control {
                flex: 1;
            }

            .theme-options {
                display: flex;
                gap: 10px;
            }

            .theme-option {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                cursor: pointer;
                border: 2px solid transparent;
                transition: transform 0.2s ease;
            }

            .theme-option:hover {
                transform: scale(1.1);
            }

            .theme-option.active {
                border-color: var(--highlight-color);
            }

            .theme-light {
                background-color: #fff;
                box-shadow: 0 0 3px rgba(0,0,0,0.2);
            }

            .theme-dark {
                background-color: #121212;
                box-shadow: 0 0 3px rgba(0,0,0,0.2);
            }

            .theme-sepia {
                background-color: #F9F5E9;
                box-shadow: 0 0 3px rgba(0,0,0,0.2);
            }

            .font-options {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .font-option {
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                border: 1px solid var(--border-color);
                transition: all 0.2s ease;
            }

            .font-option:hover {
                background-color: rgba(0,0,0,0.02);
            }

            .font-option.active {
                border-color: var(--highlight-color);
                background-color: rgba(0,0,0,0.03);
            }

            [data-theme="dark"] .font-option:hover {
                background-color: rgba(255,255,255,0.03);
            }

            [data-theme="dark"] .font-option.active {
                background-color: rgba(255,255,255,0.05);
            }

            [data-theme="sepia"] .font-option:hover {
                background-color: rgba(0,0,0,0.02);
            }

            [data-theme="sepia"] .font-option.active {
                background-color: rgba(0,0,0,0.03);
            }

            .font-sans {
                font-family: 'Noto Sans SC', sans-serif;
            }

            .font-serif {
                font-family: 'Noto Serif SC', serif;
            }

            .slider-container {
                width: 100%;
                padding: 5px 0;
            }

            .slider {
                width: 100%;
                -webkit-appearance: none;
                height: 6px;
                border-radius: 3px;
                background: var(--border-color);
                outline: none;
            }

            .slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                appearance: none;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: var(--highlight-color);
                cursor: pointer;
                transition: transform 0.2s ease;
            }

            .slider::-moz-range-thumb {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: var(--highlight-color);
                cursor: pointer;
                transition: transform 0.2s ease;
                border: none;
            }

            .slider::-webkit-slider-thumb:hover {
                transform: scale(1.2);
            }

            .slider::-moz-range-thumb:hover {
                transform: scale(1.2);
            }

            @media (max-width: 600px) {
                .settings-panel {
                    width: 85%;
                    right: -85%;
                }
            }
        `;
        document.head.appendChild(styleElement);
    }
}

// 初始化设置功能
function initSettings() {
    // 创建设置面板
    createSettingsPanel();

    // 获取DOM元素
    const themeToggle = document.getElementById('theme-toggle');
    const settingsButton = document.getElementById('settings-button');
    const settingsPanel = document.getElementById('settings-panel');
    const settingsClose = document.getElementById('settings-close');
    const fontSizeSlider = document.getElementById('font-size-slider');
    const fontSizeValue = document.getElementById('font-size-value');
    const lineHeightSlider = document.getElementById('line-height-slider');
    const lineHeightValue = document.getElementById('line-height-value');
    const paragraphSpacingSlider = document.getElementById('paragraph-spacing-slider');
    const paragraphSpacingValue = document.getElementById('paragraph-spacing-value');
    const marginSlider = document.getElementById('margin-slider');
    const marginValue = document.getElementById('margin-value');
    const themeOptions = document.querySelectorAll('.theme-option');
    const fontOptions = document.querySelectorAll('.font-option');

    // 从本地存储加载设置
    function loadSettings() {
        // 主题设置
        const theme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', theme);
        if (themeToggle) {
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }

        // 更新主题选项的激活状态
        themeOptions.forEach(option => {
            if (option.dataset.theme === theme) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });

        // 字体设置
        const fontFamily = localStorage.getItem('fontFamily') || 'sans';
        document.documentElement.style.setProperty('--font-family',
            fontFamily === 'serif' ?
            "'Noto Serif SC', serif" :
            "'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif");

        // 更新字体选项的激活状态
        fontOptions.forEach(option => {
            if (option.dataset.font === fontFamily) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });

        // 检测是否为移动设备
        const isMobile = window.innerWidth <= 600;

        // 字体大小设置 - 移动端默认更大，但仍然尊重用户的设置
        const defaultFontSize = isMobile ? '18' : '16';
        // 如果用户已经设置了字体大小，则使用用户的设置，否则使用默认值
        const fontSize = localStorage.getItem('fontSize') || defaultFontSize;
        document.documentElement.style.setProperty('--font-size', `${fontSize}px`);
        if (fontSizeSlider) fontSizeSlider.value = fontSize;
        if (fontSizeValue) fontSizeValue.textContent = `${fontSize}px`;

        // 行距设置
        const lineHeight = localStorage.getItem('lineHeight') || '1.7';
        document.documentElement.style.setProperty('--line-height', lineHeight);
        if (lineHeightSlider) lineHeightSlider.value = lineHeight;
        if (lineHeightValue) lineHeightValue.textContent = lineHeight;

        // 段落间距设置
        const paragraphSpacing = localStorage.getItem('paragraphSpacing') || '1.4';
        document.documentElement.style.setProperty('--paragraph-spacing', `${paragraphSpacing}rem`);
        if (paragraphSpacingSlider) paragraphSpacingSlider.value = paragraphSpacing;
        if (paragraphSpacingValue) paragraphSpacingValue.textContent = `${paragraphSpacing}rem`;

        // 页边距设置 - 移动端默认更宽，但仍然尊重用户的设置
        const defaultMargin = isMobile ? '8' : '5';
        // 如果用户已经设置了页边距，则使用用户的设置，否则使用默认值
        const margin = localStorage.getItem('margin') || defaultMargin;
        const containerWidth = 100 - (margin * 2);
        // 确保页边距应用于左右两侧，而不是上下
        document.documentElement.style.setProperty('--container-padding', `0 ${margin}%`);
        document.documentElement.style.setProperty('--container-width', `${containerWidth}%`);

        // 添加特殊的移动端样式覆盖
        if (window.innerWidth <= 600) {
            // 在移动端强制应用我们的设置
            document.documentElement.classList.add('reader-settings-applied');
        }
        if (marginSlider) marginSlider.value = margin;
        if (marginValue) marginValue.textContent = `${margin}%`;
    }

    // 初始加载设置
    loadSettings();

    // 在页面加载时检查是否为移动端，如果是则应用我们的设置
    if (window.innerWidth <= 600) {
        document.documentElement.classList.add('reader-settings-applied');
    }

    // 打开设置面板
    if (settingsButton) {
        settingsButton.addEventListener('click', () => {
            settingsPanel.classList.add('open');
        });
    }

    // 关闭设置面板
    if (settingsClose) {
        settingsClose.addEventListener('click', () => {
            settingsPanel.classList.remove('open');
        });
    }

    // 主题选项点击事件
    themeOptions.forEach(option => {
        option.addEventListener('click', () => {
            const theme = option.dataset.theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);

            // 更新主题切换按钮
            if (themeToggle) {
                themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
            }

            // 更新主题选项的激活状态
            themeOptions.forEach(opt => {
                opt.classList.toggle('active', opt === option);
            });
        });
    });

    // 字体选项点击事件
    fontOptions.forEach(option => {
        option.addEventListener('click', () => {
            const font = option.dataset.font;
            const fontFamily = font === 'serif' ?
                "'Noto Serif SC', serif" :
                "'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

            document.documentElement.style.setProperty('--font-family', fontFamily);
            localStorage.setItem('fontFamily', font);

            // 更新字体选项的激活状态
            fontOptions.forEach(opt => {
                opt.classList.toggle('active', opt === option);
            });
        });
    });

    // 字体大小滑块事件
    if (fontSizeSlider) {
        fontSizeSlider.addEventListener('input', () => {
            const fontSize = fontSizeSlider.value;
            document.documentElement.style.setProperty('--font-size', `${fontSize}px`);
            // 添加特殊的移动端样式覆盖
            if (window.innerWidth <= 600) {
                // 在移动端强制应用我们的设置
                document.documentElement.classList.add('reader-settings-applied');
            }
            fontSizeValue.textContent = `${fontSize}px`;
            localStorage.setItem('fontSize', fontSize);
        });
    }

    // 行距滑块事件
    if (lineHeightSlider) {
        lineHeightSlider.addEventListener('input', () => {
            const lineHeight = lineHeightSlider.value;
            document.documentElement.style.setProperty('--line-height', lineHeight);
            // 添加特殊的移动端样式覆盖
            if (window.innerWidth <= 600) {
                // 在移动端强制应用我们的设置
                document.documentElement.classList.add('reader-settings-applied');
            }
            lineHeightValue.textContent = lineHeight;
            localStorage.setItem('lineHeight', lineHeight);
        });
    }

    // 段落间距滑块事件
    if (paragraphSpacingSlider) {
        paragraphSpacingSlider.addEventListener('input', () => {
            const paragraphSpacing = paragraphSpacingSlider.value;
            document.documentElement.style.setProperty('--paragraph-spacing', `${paragraphSpacing}rem`);
            // 添加特殊的移动端样式覆盖
            if (window.innerWidth <= 600) {
                // 在移动端强制应用我们的设置
                document.documentElement.classList.add('reader-settings-applied');
            }
            paragraphSpacingValue.textContent = `${paragraphSpacing}rem`;
            localStorage.setItem('paragraphSpacing', paragraphSpacing);
        });
    }

    // 页边距滑块事件
    if (marginSlider) {
        marginSlider.addEventListener('input', () => {
            const margin = marginSlider.value;
            const containerWidth = 100 - (margin * 2);
            // 确保页边距应用于左右两侧，而不是上下
            document.documentElement.style.setProperty('--container-padding', `0 ${margin}%`);
            document.documentElement.style.setProperty('--container-width', `${containerWidth}%`);
            // 添加特殊的移动端样式覆盖
            if (window.innerWidth <= 600) {
                // 在移动端强制应用我们的设置
                document.documentElement.classList.add('reader-settings-applied');
            }
            marginValue.textContent = `${margin}%`;
            localStorage.setItem('margin', margin);
        });
    }

    // 点击页面其他区域关闭设置面板
    document.addEventListener('click', (event) => {
        if (settingsPanel &&
            !settingsPanel.contains(event.target) &&
            event.target !== settingsButton &&
            settingsPanel.classList.contains('open')) {
            settingsPanel.classList.remove('open');
        }
    });

    // 监听窗口大小变化，确保在移动端正确应用我们的设置
    window.addEventListener('resize', () => {
        if (window.innerWidth <= 600) {
            // 在移动端强制应用我们的设置
            document.documentElement.classList.add('reader-settings-applied');
        } else {
            // 在桌面端移除特殊的样式覆盖
            document.documentElement.classList.remove('reader-settings-applied');
        }
    });
}

// 当DOM加载完成后初始化设置
document.addEventListener('DOMContentLoaded', initSettings);

// 如果DOM已经加载完成，立即初始化
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    initSettings();
}
