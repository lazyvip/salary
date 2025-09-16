// 全局变量
let currentNewsData = null;
let historyData = [];

// 语音合成相关变量
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;
let isReading = false;
let availableVoices = [];
let voiceSettings = {
    rate: 0.9,
    pitch: 1.0,
    volume: 1.0,
    voice: "Chinese (Taiwan) [zh-TW]"
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化');
    initializeApp();
});

// 页面卸载时停止朗读
window.addEventListener('beforeunload', function() {
    if (isReading) {
        stopSpeaking();
    }
});

// 页面隐藏时暂停朗读
document.addEventListener('visibilitychange', function() {
    if (document.hidden && isReading) {
        stopSpeaking();
    }
});

// 初始化应用
function initializeApp() {
    // 绑定导航事件
    bindNavigationEvents();
    
    // 初始化语音设置
    initializeVoiceSettings();
    
    // 加载今日新闻
    loadTodayNews();
    
    // 加载历史数据
    loadHistoryData();
    
    // 绑定模态框事件
    bindModalEvents();
}

// 绑定导航事件
function bindNavigationEvents() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const tab = this.getAttribute('data-tab');
            switchTab(tab);
        });
    });
}

// 切换标签页
function switchTab(tab) {
    // 更新导航状态
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    
    // 更新内容显示
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tab).classList.add('active');
    
    // 如果切换到历史页面，刷新历史数据
    if (tab === 'history') {
        loadHistoryData();
    }
}

// 加载今日新闻
async function loadTodayNews() {
    console.log('开始加载今日新闻');
    
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');
    const contentEl = document.getElementById('news-content');
    
    // 显示加载状态
    loadingEl.style.display = 'block';
    errorEl.style.display = 'none';
    contentEl.style.display = 'none';
    
    try {
        // 尝试从API获取数据
        const response = await fetch('https://v3.alapi.cn/api/zaobao', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: 'wpaakpirgkoetjh1m627psuf2ncd85',
                format: 'json'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API响应数据:', data);
        
        if (data && data.success && data.data) {
            // 标记数据来源为API
            data.data.source = 'api';
            currentNewsData = data.data;
            displayTodayNews(currentNewsData);
            saveToHistory(currentNewsData);
            console.log('API数据加载成功并已保存到历史记录');
        } else {
            throw new Error('API返回数据格式错误');
        }
        
    } catch (error) {
        console.error('获取新闻数据失败:', error);
        // 如果API失败，使用模拟数据
        loadMockData();
    }
}

// 加载模拟数据（当API不可用时）
function loadMockData() {
    console.log('使用模拟数据');
    
    const mockData = {
        date: new Date().toISOString().split('T')[0],
        news: [
            '1、国家统计局：11月份，全国居民消费价格同比上涨0.2%，环比下降0.6%。',
            '2、教育部：2024年全国硕士研究生招生考试将于12月23日至25日举行。',
            '3、工信部：前10个月，我国软件业务收入同比增长13.7%。',
            '4、交通运输部：预计今年春运期间客流量将达到90亿人次。',
            '5、央行：11月末，广义货币(M2)余额同比增长10.0%。',
            '6、商务部：1-10月，我国实际使用外资金额同比增长2.3%。',
            '7、国家能源局：前10个月，全国发电量同比增长4.2%。',
            '8、住建部：加快推进城市更新，提升城市发展质量。',
            '9、农业农村部：全国秋粮收获基本结束，产量再创历史新高。',
            '10、文旅部：国庆假期全国共接待游客8.26亿人次。'
        ],
        image: 'data:image/svg+xml;base64,' + btoa(`
            <svg xmlns="http://www.w3.org/2000/svg" width="800" height="1200" viewBox="0 0 800 1200">
                <defs>
                    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <rect width="800" height="1200" fill="url(#bg)"/>
                <rect x="40" y="40" width="720" height="1120" rx="20" fill="white" fill-opacity="0.95"/>
                <text x="400" y="120" text-anchor="middle" font-family="Arial, sans-serif" font-size="36" font-weight="bold" fill="#333">📰 每日新闻早报</text>
                <text x="400" y="180" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#666">${new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })}</text>
                <text x="400" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#999">60秒读懂世界</text>
                <line x1="80" y1="260" x2="720" y2="260" stroke="#eee" stroke-width="2"/>
                ${mockData.news.map((item, index) => `
                    <text x="100" y="${320 + index * 80}" font-family="Arial, sans-serif" font-size="16" fill="#333">${item}</text>
                `).join('')}
                <rect x="80" y="1080" width="640" height="60" rx="30" fill="#667eea" fill-opacity="0.1"/>
                <text x="400" y="1120" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#667eea">关注公众号：懒人搜索</text>
            </svg>
        `),
        source: 'mock' // 标记为模拟数据
    };
    
    currentNewsData = mockData;
    displayTodayNews(currentNewsData);
    saveToHistory(currentNewsData);
    console.log('模拟数据加载完成并已保存到历史记录');
}

// 生成历史数据（如果需要）
function generateHistoryDataIfNeeded() {
    try {
        const historyKey = 'newsHistory';
        let history = JSON.parse(localStorage.getItem(historyKey) || '[]');
        
        // 如果历史数据少于7天，生成一些历史数据
        if (history.length < 7) {
            console.log('历史数据不足，生成模拟历史数据');
            
            const newsTemplates = [
                [
                    '1、央行：12月LPR保持不变，1年期为3.1%，5年期以上为3.6%。',
                    '2、统计局：11月CPI同比上涨0.2%，PPI同比下降2.8%。',
                    '3、工信部：前11月全国规模以上工业增加值同比增长4.3%。',
                    '4、商务部：1-11月全国实际使用外资金额1.09万亿元。',
                    '5、交通部：预计元旦假期全国发送旅客超1.5亿人次。',
                    '6、教育部：2024年全国高考报名人数1353万，再创历史新高。',
                    '7、住建部：11月70个大中城市房价环比下降0.5%。',
                    '8、农业部：全年粮食产量预计超1.39万亿斤，实现"二十连丰"。',
                    '9、文旅部：预计元旦假期国内旅游出游1.35亿人次。',
                    '10、卫健委：全国医疗机构床位使用率保持在75%左右。'
                ],
                [
                    '1、发改委：11月全社会用电量同比增长8.4%，经济运行稳中向好。',
                    '2、财政部：1-11月全国一般公共预算收入20.1万亿元。',
                    '3、人社部：11月全国城镇调查失业率为5.0%，保持稳定。',
                    '4、生态环境部：11月全国空气质量优良天数比例为85.2%。',
                    '5、市场监管总局：前11月新设经营主体3200万户。',
                    '6、海关总署：11月进出口总值3.7万亿元，同比增长1.2%。',
                    '7、银保监会：11月末银行业金融机构总资产417万亿元。',
                    '8、证监会：持续推进资本市场高质量发展。',
                    '9、外汇局：11月末外汇储备规模31718亿美元。',
                    '10、国资委：央企前11月营业收入同比增长2.9%。'
                ],
                [
                    '1、科技部：我国研发经费投入强度达到2.64%，创历史新高。',
                    '2、工信部：5G基站总数达337.7万个，覆盖所有地级市。',
                    '3、网信办：持续净化网络环境，维护网络安全。',
                    '4、能源局：11月全社会用电量7417亿千瓦时。',
                    '5、水利部：南水北调工程累计调水超600亿立方米。',
                    '6、自然资源部：严格耕地保护，坚守18亿亩红线。',
                    '7、应急部：全年安全生产形势总体稳定。',
                    '8、税务总局：前11月全国税收收入15.5万亿元。',
                    '9、邮政局：11月快递业务量完成139.0亿件。',
                    '10、气象局：预计今冬气温偏高，降水偏少。'
                ],
                [
                    '1、外交部：中方愿与各国加强合作，共建人类命运共同体。',
                    '2、国防部：中国军队将坚决维护国家主权和领土完整。',
                    '3、公安部：持续推进"百日行动"，社会治安持续向好。',
                    '4、司法部：深化司法体制改革，提升司法公信力。',
                    '5、民政部：全国共有社会组织90万个，发挥重要作用。',
                    '6、人社部：企业职工基本养老保险基金累计结余5.1万亿元。',
                    '7、退役军人部：做好退役军人服务保障工作。',
                    '8、应急部：加强应急管理体系和能力现代化建设。',
                    '9、审计署：持续加大对重大政策落实情况审计力度。',
                    '10、统计局：经济运行总体平稳，稳中有进。'
                ],
                [
                    '1、最高法：深化司法改革，让人民群众感受到公平正义。',
                    '2、最高检：依法履职尽责，维护社会公平正义。',
                    '3、全国人大：完善立法工作，推进全面依法治国。',
                    '4、全国政协：发挥人民政协专门协商机构作用。',
                    '5、中科院：加强基础研究，推动科技自立自强。',
                    '6、社科院：加强哲学社会科学研究，服务国家建设。',
                    '7、工程院：发挥国家工程科技思想库作用。',
                    '8、中医药局：传承发展中医药事业，服务人民健康。',
                    '9、文物局：加强文物保护利用，传承中华优秀传统文化。',
                    '10、体育总局：推动体育强国建设，促进全民健身。'
                ]
            ];
            
            // 生成过去几天的数据
            for (let i = 1; i <= 10; i++) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                const dateStr = date.toISOString().split('T')[0];
                
                // 检查是否已存在该日期的记录
                const existingIndex = history.findIndex(item => item.date === dateStr);
                if (existingIndex >= 0) continue;
                
                const newsIndex = (i - 1) % newsTemplates.length;
                const newsData = newsTemplates[newsIndex];
                
                const historyItem = {
                    date: dateStr,
                    news: newsData,
                    image: generateHistoryImage(date, newsData),
                    timestamp: date.getTime()
                };
                
                history.unshift(historyItem);
            }
            
            // 按日期排序并保存
            history = history.sort((a, b) => new Date(b.date) - new Date(a.date));
            history = history.slice(0, 30); // 只保留最近30天
            
            localStorage.setItem(historyKey, JSON.stringify(history));
            console.log('历史数据生成完成，共', history.length, '条记录');
        }
    } catch (error) {
        console.error('生成历史数据失败:', error);
    }
}

// 生成历史图片
function generateHistoryImage(date, newsData) {
    const dateStr = date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
    
    return 'data:image/svg+xml;base64,' + btoa(`
        <svg xmlns="http://www.w3.org/2000/svg" width="800" height="1200" viewBox="0 0 800 1200">
            <defs>
                <linearGradient id="bg${date.getTime()}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#${getRandomColor(date)};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#${getRandomColor(date, 1)};stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="800" height="1200" fill="url(#bg${date.getTime()})"/>
            <rect x="40" y="40" width="720" height="1120" rx="20" fill="white" fill-opacity="0.95"/>
            <text x="400" y="120" text-anchor="middle" font-family="Arial, sans-serif" font-size="36" font-weight="bold" fill="#333">📰 每日新闻早报</text>
            <text x="400" y="180" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#666">${dateStr}</text>
            <text x="400" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#999">60秒读懂世界</text>
            <line x1="80" y1="260" x2="720" y2="260" stroke="#eee" stroke-width="2"/>
            ${newsData.map((item, index) => `
                <text x="100" y="${320 + index * 80}" font-family="Arial, sans-serif" font-size="16" fill="#333">${item}</text>
            `).join('')}
            <rect x="80" y="1080" width="640" height="60" rx="30" fill="#667eea" fill-opacity="0.1"/>
            <text x="400" y="1120" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#667eea">关注公众号：懒人搜索</text>
        </svg>
    `);
}

// 根据日期生成随机颜色
function getRandomColor(date, offset = 0) {
    const colors = ['667eea', '764ba2', 'f093fb', 'f5576c', '4facfe', '00f2fe', 'a8edea', 'fed6e3', 'ffecd2', 'fcb69f'];
    const index = (date.getDay() + offset) % colors.length;
    return colors[index];
}

// 显示今日新闻
function displayTodayNews(newsData) {
    console.log('显示今日新闻:', newsData);
    
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');
    const contentEl = document.getElementById('news-content');
    
    // 隐藏加载和错误状态
    loadingEl.style.display = 'none';
    errorEl.style.display = 'none';
    
    // 更新日期和时间
    const dateEl = document.getElementById('news-date');
    const timeEl = document.getElementById('news-time');
    const date = new Date(newsData.date || new Date());
    
    dateEl.textContent = date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    });
    
    timeEl.textContent = `更新时间：${date.toLocaleTimeString('zh-CN')}`;
    
    // 更新图片
    const imageEl = document.getElementById('news-image');
    if (newsData.image) {
        imageEl.src = newsData.image;
        imageEl.onerror = function() {
            console.log('图片加载失败，使用默认图片');
            this.src = 'data:image/svg+xml;base64,' + btoa(`
                <svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
                    <rect width="800" height="600" fill="#f0f0f0"/>
                    <text x="400" y="300" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#999">📰 新闻图片加载中...</text>
                </svg>
            `);
        };
    }
    
    // 更新新闻文本
    const textEl = document.getElementById('news-text');
    if (newsData.news && Array.isArray(newsData.news)) {
        textEl.textContent = newsData.news.join('\n\n');
    } else {
        textEl.textContent = '每日新闻早报 - 60秒读懂世界';
    }
    
    // 显示内容并添加动画
    contentEl.style.display = 'block';
    contentEl.classList.add('fade-in');
}

// 保存到历史记录
function saveToHistory(newsData) {
    try {
        const historyKey = 'newsHistory';
        let history = JSON.parse(localStorage.getItem(historyKey) || '[]');
        
        // 检查是否已存在相同日期的记录
        const dateStr = newsData.date || new Date().toISOString().split('T')[0];
        const existingIndex = history.findIndex(item => item.date === dateStr);
        
        const historyItem = {
            date: dateStr,
            news: newsData.news || [],
            image: newsData.image || '',
            timestamp: Date.now(),
            source: newsData.source || 'api' // 标记数据来源
        };
        
        if (existingIndex >= 0) {
            // 更新现有记录，但保留原有的source信息
            const existingItem = history[existingIndex];
            historyItem.source = existingItem.source || historyItem.source;
            history[existingIndex] = historyItem;
            console.log('更新历史记录:', historyItem);
        } else {
            // 添加新记录
            history.unshift(historyItem);
            console.log('添加新历史记录:', historyItem);
        }
        
        // 只保留最近30天的记录
        history = history.slice(0, 30);
        
        localStorage.setItem(historyKey, JSON.stringify(history));
        
        // 重新加载历史数据显示
        if (document.querySelector('.tab-button.active')?.textContent === '历史早报') {
            loadHistoryData();
        }
        
    } catch (error) {
        console.error('保存历史记录失败:', error);
    }
}

// 加载历史数据
function loadHistoryData() {
    try {
        const historyKey = 'newsHistory';
        const history = JSON.parse(localStorage.getItem(historyKey) || '[]');
        
        historyData = history.sort((a, b) => new Date(b.date) - new Date(a.date));
        displayHistoryData(historyData);
        
    } catch (error) {
        console.error('加载历史数据失败:', error);
        historyData = [];
        displayHistoryData([]);
    }
}

// 显示历史数据
function displayHistoryData(history) {
    const listEl = document.getElementById('history-list');
    const emptyEl = document.getElementById('history-empty');
    
    if (history.length === 0) {
        listEl.innerHTML = '';
        emptyEl.style.display = 'block';
        return;
    }
    
    emptyEl.style.display = 'none';
    
    const colorClasses = ['orange', 'red', 'pink', 'blue', 'green', 'purple'];
    const mottos = [
        '"无行动，不决策"，任何决策都必须指向行动',
        '年少时没有恐惧，那不过是因为没有经历过真正的失去',
        '人在低纬度遇到的问题，往往只有升到高纬度，才能解决',
        '推动人生不断前进的不是忧愁，而是胆魄',
        '世界上最难沟通的人，不是没文化的人，而是被灌输了标准答案的人',
        '我们的要务不是辨明朦胧的远方，而是专注清晰的眼前',
        '无恋亦无厌，始是逍遥人',
        '常常期待，有时收获',
        '每个人都带着一生的历史和半个月的哀愁，走在人生路上',
        '得意时打拼事业，失意时享受生活'
    ];
    
    const html = history.map((item, index) => {
        const date = new Date(item.date);
        const today = new Date();
        const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
        
        let dateStr = '';
        if (isSameDay(date, today)) {
            dateStr = '今天';
        } else if (isSameDay(date, yesterday)) {
            dateStr = '昨天';
        } else {
            dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
        }
        
        const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
        const weekday = weekdays[date.getDay()];
        
        const summary = item.news && item.news.length > 0 
            ? item.news[0].substring(0, 80) + '...'
            : '每日新闻早报 - 60秒读懂世界';
        
        const colorClass = colorClasses[date.getDay() % colorClasses.length];
        const motto = mottos[index % mottos.length];
        
        return `
            <div class="history-card ${colorClass}" onclick="viewHistoryDetail(${index})">
                <div class="history-date">${dateStr}</div>
                <div class="history-weekday">${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${weekday}</div>
                <div class="history-summary">${summary}</div>
                <div class="history-motto">"${motto}"</div>
            </div>
        `;
    }).join('');
    
    listEl.innerHTML = html;
    listEl.classList.add('fade-in');
}

// 判断是否为同一天
function isSameDay(date1, date2) {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
}

// 查看历史详情
function viewHistoryDetail(index) {
    if (index >= 0 && index < historyData.length) {
        const item = historyData[index];
        showModal(item);
    }
}

// 显示模态框
function showModal(newsData) {
    const modal = document.getElementById('news-modal');
    const titleEl = document.getElementById('modal-title');
    const imageEl = document.getElementById('modal-image');
    const textEl = document.getElementById('modal-text');
    
    const date = new Date(newsData.date);
    titleEl.textContent = `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 新闻早报`;
    
    if (newsData.image) {
        imageEl.src = newsData.image;
        imageEl.style.display = 'block';
    } else {
        imageEl.style.display = 'none';
    }
    
    if (newsData.news && Array.isArray(newsData.news)) {
        textEl.textContent = newsData.news.join('\n\n');
    } else {
        textEl.textContent = '暂无新闻内容';
    }
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // 保存当前模态框数据
    modal.currentData = newsData;
}

// 关闭模态框
function closeModal() {
    const modal = document.getElementById('news-modal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// 绑定模态框事件
function bindModalEvents() {
    const modal = document.getElementById('news-modal');
    
    // 点击模态框外部关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // ESC键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });
}

// 保存图片功能
function saveImage() {
    if (currentNewsData && currentNewsData.image) {
        const link = document.createElement('a');
        link.href = currentNewsData.image;
        link.download = `懒人日报_${new Date().toISOString().split('T')[0]}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast('图片保存成功！');
    } else {
        showToast('暂无图片可保存');
    }
}

// 保存模态框图片
function saveModalImage() {
    const modal = document.getElementById('news-modal');
    const newsData = modal.currentData;
    
    if (newsData && newsData.image) {
        const link = document.createElement('a');
        link.href = newsData.image;
        link.download = `懒人日报_${newsData.date}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast('图片保存成功！');
    } else {
        showToast('暂无图片可保存');
    }
}

// 朗读当前新闻
function speakCurrentNews() {
    if (isReading) {
        stopSpeaking();
        return;
    }
    
    if (!currentNewsData || !currentNewsData.news) {
        showMessage('没有可朗读的新闻内容', 'warning');
        return;
    }
    
    const textToSpeak = currentNewsData.news.join('。');
    speakText(textToSpeak);
}

// 朗读模态框新闻
function speakModalNews() {
    if (isReading) {
        stopSpeaking();
        return;
    }
    
    const modal = document.getElementById('news-modal');
    const newsData = modal.currentData;
    
    if (!newsData || !newsData.news) {
        showMessage('没有可朗读的新闻内容', 'warning');
        return;
    }
    
    const textToSpeak = newsData.news.join('。');
    speakText(textToSpeak);
}

// 复制新闻文本
function copyNewsText() {
    if (currentNewsData && currentNewsData.news) {
        const text = Array.isArray(currentNewsData.news) 
            ? currentNewsData.news.join('\n\n')
            : currentNewsData.news;
        
        copyToClipboard(text);
    } else {
        showToast('暂无文本可复制');
    }
}

// 复制模态框文本
function copyModalText() {
    const modal = document.getElementById('news-modal');
    const newsData = modal.currentData;
    
    if (newsData && newsData.news) {
        const text = Array.isArray(newsData.news) 
            ? newsData.news.join('\n\n')
            : newsData.news;
        
        copyToClipboard(text);
    } else {
        showToast('暂无文本可复制');
    }
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('文本已复制到剪贴板！');
        }).catch(err => {
            console.error('复制失败:', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

// 备用复制方法
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showToast('文本已复制到剪贴板！');
        } else {
            showToast('复制失败，请手动复制');
        }
    } catch (err) {
        console.error('复制失败:', err);
        showToast('复制失败，请手动复制');
    }
    
    document.body.removeChild(textArea);
}

// 分享功能
function shareNews() {
    if (navigator.share && currentNewsData) {
        const shareData = {
            title: '懒人日报 - 每日新闻早报',
            text: '60秒读懂世界',
            url: window.location.href
        };
        
        navigator.share(shareData).then(() => {
            console.log('分享成功');
        }).catch(err => {
            console.error('分享失败:', err);
            fallbackShare();
        });
    } else {
        fallbackShare();
    }
}

// 分享模态框新闻
function shareModalNews() {
    const modal = document.getElementById('news-modal');
    const newsData = modal.currentData;
    
    if (navigator.share && newsData) {
        const date = new Date(newsData.date);
        const shareData = {
            title: `懒人日报 - ${date.getMonth() + 1}月${date.getDate()}日新闻早报`,
            text: '60秒读懂世界',
            url: window.location.href
        };
        
        navigator.share(shareData).then(() => {
            console.log('分享成功');
        }).catch(err => {
            console.error('分享失败:', err);
            fallbackShare();
        });
    } else {
        fallbackShare();
    }
}

// 备用分享方法
function fallbackShare() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent('懒人日报 - 每日新闻早报，60秒读懂世界');
    
    // 创建分享选项
    const shareOptions = [
        {
            name: '微信',
            action: () => showToast('请复制链接到微信分享')
        },
        {
            name: '微博',
            action: () => window.open(`https://service.weibo.com/share/share.php?url=${url}&title=${text}`, '_blank')
        },
        {
            name: 'QQ',
            action: () => window.open(`https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${text}`, '_blank')
        },
        {
            name: '复制链接',
            action: () => copyToClipboard(window.location.href)
        }
    ];
    
    // 简单的分享提示
    showToast('请选择分享方式：复制链接或使用浏览器分享功能');
}

// 初始化语音设置
function initializeVoiceSettings() {
    // 等待语音列表加载
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = loadVoices;
    }
    loadVoices();
}

// 加载可用语音
function loadVoices() {
    availableVoices = speechSynthesis.getVoices();
    
    // 优先选择台湾中文语音
    const taiwanVoice = availableVoices.find(voice => 
        voice.name.includes('Chinese (Taiwan)') || voice.lang === 'zh-TW'
    );
    
    // 如果没有台湾语音，选择其他中文语音
    const chineseVoice = availableVoices.find(voice => 
        voice.lang.includes('zh') || voice.name.includes('Chinese')
    );
    
    if (taiwanVoice) {
        voiceSettings.voice = taiwanVoice;
    } else if (chineseVoice) {
        voiceSettings.voice = chineseVoice;
    }
    
    console.log('可用语音:', availableVoices.length);
    
    // 更新语音选择下拉框
    updateVoiceSelect();
}

// 更新语音选择下拉框
function updateVoiceSelect() {
    const voiceSelect = document.getElementById('voice-select');
    if (!voiceSelect) return;
    
    // 清空现有选项
    voiceSelect.innerHTML = '<option value="">默认语音</option>';
    
    // 添加可用语音
    availableVoices.forEach((voice, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${voice.name} (${voice.lang})`;
        if (voiceSettings.voice && voiceSettings.voice.name === voice.name) {
            option.selected = true;
        }
        voiceSelect.appendChild(option);
    });
    
    // 绑定事件
    voiceSelect.addEventListener('change', function() {
        const selectedIndex = this.value;
        if (selectedIndex === '') {
            voiceSettings.voice = null;
        } else {
            voiceSettings.voice = availableVoices[selectedIndex];
        }
        saveVoiceSettings();
    });
    
    // 绑定滑块事件
    bindSliderEvents();
}

// 绑定滑块事件
function bindSliderEvents() {
    const rateSlider = document.getElementById('voice-rate');
    const pitchSlider = document.getElementById('voice-pitch');
    const volumeSlider = document.getElementById('voice-volume');
    
    const rateValue = document.getElementById('rate-value');
    const pitchValue = document.getElementById('pitch-value');
    const volumeValue = document.getElementById('volume-value');
    
    if (rateSlider) {
        rateSlider.value = voiceSettings.rate;
        rateValue.textContent = voiceSettings.rate;
        rateSlider.addEventListener('input', function() {
            voiceSettings.rate = parseFloat(this.value);
            rateValue.textContent = this.value;
            saveVoiceSettings();
        });
    }
    
    if (pitchSlider) {
        pitchSlider.value = voiceSettings.pitch;
        pitchValue.textContent = voiceSettings.pitch.toFixed(1);
        pitchSlider.addEventListener('input', function() {
            voiceSettings.pitch = parseFloat(this.value);
            pitchValue.textContent = parseFloat(this.value).toFixed(1);
            saveVoiceSettings();
        });
    }
    
    if (volumeSlider) {
        volumeSlider.value = voiceSettings.volume;
        volumeValue.textContent = voiceSettings.volume.toFixed(1);
        volumeSlider.addEventListener('input', function() {
            voiceSettings.volume = parseFloat(this.value);
            volumeValue.textContent = parseFloat(this.value).toFixed(1);
            saveVoiceSettings();
        });
    }
}

// 保存语音设置
function saveVoiceSettings() {
    try {
        const settings = {
            rate: voiceSettings.rate,
            pitch: voiceSettings.pitch,
            volume: voiceSettings.volume,
            voiceName: voiceSettings.voice ? voiceSettings.voice.name : null
        };
        localStorage.setItem('voiceSettings', JSON.stringify(settings));
    } catch (error) {
        console.error('保存语音设置失败:', error);
    }
}

// 加载语音设置
function loadVoiceSettings() {
    try {
        const saved = localStorage.getItem('voiceSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            voiceSettings.rate = settings.rate || 0.9;
            voiceSettings.pitch = settings.pitch || 1.0;
            voiceSettings.volume = settings.volume || 1.0;
            
            // 恢复语音选择
            if (settings.voiceName && availableVoices.length > 0) {
                const voice = availableVoices.find(v => v.name === settings.voiceName);
                if (voice) {
                    voiceSettings.voice = voice;
                }
            }
        }
    } catch (error) {
        console.error('加载语音设置失败:', error);
    }
}

// 切换设置面板
function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    if (panel.classList.contains('show')) {
        panel.classList.remove('show');
    } else {
        panel.classList.add('show');
        // 加载保存的设置
        loadVoiceSettings();
        updateVoiceSelect();
    }
}

// 测试语音
function testVoice() {
    const testText = '这是语音测试，懒人日报为您播报新闻。';
    speakText(testText);
}

// 重置语音设置
function resetVoiceSettings() {
    voiceSettings = {
        rate: 0.9,
        pitch: 1.0,
        volume: 1.0,
        voice: null
    };
    
    // 优先选择台湾中文语音
    const taiwanVoice = availableVoices.find(voice => 
        voice.name.includes('Chinese (Taiwan)') || voice.lang === 'zh-TW'
    );
    
    // 如果没有台湾语音，选择其他中文语音
    const chineseVoice = availableVoices.find(voice => 
        voice.lang.includes('zh') || voice.name.includes('Chinese')
    );
    
    if (taiwanVoice) {
        voiceSettings.voice = taiwanVoice;
    } else if (chineseVoice) {
        voiceSettings.voice = chineseVoice;
    }
    
    saveVoiceSettings();
    updateVoiceSelect();
    showMessage('语音设置已重置', 'success');
}

// 语音合成功能
function speakText(text) {
    if (!speechSynthesis) {
        showMessage('您的浏览器不支持语音合成功能', 'error');
        return;
    }
    
    // 如果正在朗读，先停止
    if (isReading) {
        stopSpeaking();
        return;
    }
    
    // 创建语音合成实例
    currentUtterance = new SpeechSynthesisUtterance(text);
    
    // 设置语音参数
    currentUtterance.lang = 'zh-CN'; // 中文
    currentUtterance.rate = voiceSettings.rate; // 语速
    currentUtterance.pitch = voiceSettings.pitch; // 音调
    currentUtterance.volume = voiceSettings.volume; // 音量
    
    // 设置语音
    if (voiceSettings.voice) {
        currentUtterance.voice = voiceSettings.voice;
    }
    
    // 事件监听
    currentUtterance.onstart = function() {
        isReading = true;
        updateSpeakButtons(true);
        showMessage('开始朗读...', 'info');
    };
    
    currentUtterance.onend = function() {
        isReading = false;
        updateSpeakButtons(false);
        currentUtterance = null;
    };
    
    currentUtterance.onerror = function(event) {
        isReading = false;
        updateSpeakButtons(false);
        showMessage('朗读出现错误: ' + event.error, 'error');
        currentUtterance = null;
    };
    
    // 开始朗读
    speechSynthesis.speak(currentUtterance);
}

// 停止朗读
function stopSpeaking() {
    if (speechSynthesis && isReading) {
        speechSynthesis.cancel();
        isReading = false;
        updateSpeakButtons(false);
        currentUtterance = null;
        showMessage('已停止朗读', 'info');
    }
}

// 更新朗读按钮状态
function updateSpeakButtons(reading) {
    const speakButtons = document.querySelectorAll('.speak-btn');
    speakButtons.forEach(btn => {
        if (reading) {
            btn.innerHTML = '<i class="fas fa-stop"></i> 停止朗读';
            btn.classList.add('reading');
            btn.title = '停止朗读';
        } else {
            btn.innerHTML = '<i class="fas fa-volume-up"></i> 朗读新闻';
            btn.classList.remove('reading');
            btn.title = '朗读新闻';
        }
    });
}

// 显示提示消息
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // 添加样式
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // 根据类型设置背景色
    switch(type) {
        case 'success':
            messageDiv.style.backgroundColor = '#10b981';
            break;
        case 'error':
            messageDiv.style.backgroundColor = '#ef4444';
            break;
        case 'warning':
            messageDiv.style.backgroundColor = '#f59e0b';
            break;
        default:
            messageDiv.style.backgroundColor = '#3b82f6';
    }
    
    document.body.appendChild(messageDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                messageDiv.remove();
            }, 300);
        }
    }, 3000);
}

// 显示提示消息（兼容旧版本）
function showToast(message) {
    showMessage(message, 'info');
}

// 工具函数：格式化日期
function formatDate(date) {
    const d = new Date(date);
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

// 工具函数：格式化时间
function formatTime(date) {
    const d = new Date(date);
    return d.toLocaleTimeString('zh-CN', { hour12: false });
}

// 错误处理
window.addEventListener('error', function(e) {
    console.error('页面错误:', e.error);
});

// 网络状态监听
window.addEventListener('online', function() {
    showToast('网络已连接');
});

window.addEventListener('offline', function() {
    showToast('网络已断开，部分功能可能不可用');
});