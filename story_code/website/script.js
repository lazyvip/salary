// 全局变量
let allStories = [];
let filteredStories = [];
let currentPage = 1;
let storiesPerPage = 12;
let currentCategory = 'all';
let currentView = 'grid';
let currentFilters = {
    lengthRange: 'all',
    readingTime: 'all',
    sortBy: 'default'
};

// 虚拟滚动相关变量
let virtualScrollEnabled = false;
let virtualScrollContainer = null;
let virtualScrollViewport = null;
let virtualScrollContent = null;
let itemHeight = 280; // 故事卡片高度
let visibleItemsCount = 0;
let scrollTop = 0;
let totalHeight = 0;

// 懒加载相关变量
let lazyLoadEnabled = true;
let intersectionObserver = null;

// 性能监控相关变量
let performanceIndicator = null;
let renderStartTime = 0;
let renderCount = 0;

// DOM元素
const storiesGrid = document.getElementById('storiesGrid');
const loadingIndicator = document.getElementById('loadingIndicator');
const pagination = document.getElementById('pagination');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const storyModal = document.getElementById('storyModal');
const modalTitle = document.getElementById('modalTitle');
const modalCategory = document.getElementById('modalCategory');
const modalLength = document.getElementById('modalLength');
const modalContent = document.getElementById('modalContent');
const closeModal = document.getElementById('closeModal');

// 高级筛选元素
const lengthRangeSelect = document.getElementById('lengthRange');
const readingTimeSelect = document.getElementById('readingTime');
const sortBySelect = document.getElementById('sortBy');
const clearFiltersBtn = document.getElementById('clearFilters');

// 统计元素
const totalStories = document.getElementById('totalStories');
const totalCategories = document.getElementById('totalCategories');
const avgLength = document.getElementById('avgLength');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    bindEvents();
    initGreeting();
    initCategorySettings();
});

// 初始化问候语
function initGreeting() {
    const greetingText = document.getElementById('greetingText');
    const hideGreetingBtn = document.getElementById('hideGreetingBtn');
    const greetingSection = document.querySelector('.greeting-section');
    
    // 根据时间设置问候语
    const hour = new Date().getHours();
    let greeting = '';
    
    if (hour < 6) {
        greeting = '夜深了，要早点休息哦';
    } else if (hour < 12) {
        greeting = '早上好，新的一天开始了';
    } else if (hour < 18) {
        greeting = '下午好，今天过得怎么样？';
    } else {
        greeting = '晚上好，今天过得怎么样？';
    }
    
    greetingText.textContent = greeting;
    
    // 检查是否已隐藏问候语
    if (localStorage.getItem('hideGreeting') === 'true') {
        greetingSection.style.display = 'none';
    }
    
    // 隐藏问候语按钮事件
    hideGreetingBtn.addEventListener('click', function() {
        greetingSection.style.display = 'none';
        localStorage.setItem('hideGreeting', 'true');
    });
}

// 初始化分类设置
function initCategorySettings() {
    const categorySettingsBtn = document.getElementById('categorySettingsBtn');
    const categorySettingsPanel = document.getElementById('categorySettingsPanel');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const categoryTabs = document.getElementById('categoryTabs');
    
    // 打开分类设置面板
    categorySettingsBtn.addEventListener('click', function() {
        categorySettingsPanel.classList.toggle('active');
    });
    
    // 关闭分类设置面板
    closeSettingsBtn.addEventListener('click', function() {
        categorySettingsPanel.classList.remove('active');
    });
    
    // 点击面板外部关闭
    document.addEventListener('click', function(e) {
        if (!categorySettingsPanel.contains(e.target) && !categorySettingsBtn.contains(e.target)) {
            categorySettingsPanel.classList.remove('active');
        }
    });
    
    // 分类复选框变化事件
    const categoryCheckboxes = categorySettingsPanel.querySelectorAll('input[type="checkbox"]');
    categoryCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateCategoryTabs();
        });
    });
    
    // 更新分类标签
    function updateCategoryTabs() {
        const checkedCategories = Array.from(categoryCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        // 清空现有标签（保留"全部"）
        const allTab = categoryTabs.querySelector('[data-category="all"]');
        categoryTabs.innerHTML = '';
        categoryTabs.appendChild(allTab);
        
        // 添加选中的分类标签
        checkedCategories.forEach(category => {
            const tab = document.createElement('button');
            tab.className = 'category-tab';
            tab.setAttribute('data-category', category);
            tab.textContent = category;
            tab.addEventListener('click', function() {
                filterByCategory(category);
                setActiveCategoryTab(this);
            });
            categoryTabs.appendChild(tab);
        });
    }
    
    // 设置活跃的分类标签
    function setActiveCategoryTab(activeTab) {
        categoryTabs.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        activeTab.classList.add('active');
    }
    
    // 初始化分类标签点击事件
    categoryTabs.addEventListener('click', function(e) {
        if (e.target.classList.contains('category-tab')) {
            const category = e.target.getAttribute('data-category');
            filterByCategory(category);
            setActiveCategoryTab(e.target);
        }
    });
}

// 初始化应用
async function initializeApp() {
    showLoading(true);
    try {
        await loadStories();
        updateStats();
        generateCategoryButtons();
        filterStories();
        
        // 初始化性能优化功能
        initPerformanceMonitor();
        initLazyLoading();
        initVirtualScroll();
        
        renderStories();
        renderPagination();
        
        // 移动端下拉刷新功能
        if (window.innerWidth <= 768) {
            initMobilePullToRefresh();
        }
        
        console.log('应用初始化完成');
        console.log('总故事数:', allStories.length);
        console.log('当前显示故事数:', filteredStories.length);
        console.log('虚拟滚动状态:', virtualScrollEnabled ? '已启用' : '未启用');
    } catch (error) {
        console.error('初始化失败:', error);
        showError('加载故事失败，请刷新页面重试');
    } finally {
        showLoading(false);
    }
}

// 初始化虚拟滚动
function initVirtualScroll() {
    // 当故事数量超过100时启用虚拟滚动
    if (filteredStories.length > 100) {
        virtualScrollEnabled = true;
        setupVirtualScrollContainer();
        calculateVirtualScrollParams();
        renderVirtualScrollItems();
    } else {
        virtualScrollEnabled = false;
        renderStories(); // 使用传统渲染
    }
}

// 设置虚拟滚动容器
function setupVirtualScrollContainer() {
    if (!virtualScrollContainer) {
        // 创建虚拟滚动容器
        virtualScrollContainer = document.createElement('div');
        virtualScrollContainer.className = 'virtual-scroll-container';
        virtualScrollContainer.style.cssText = `
            height: 600px;
            overflow-y: auto;
            position: relative;
        `;
        
        virtualScrollViewport = document.createElement('div');
        virtualScrollViewport.className = 'virtual-scroll-viewport';
        virtualScrollViewport.style.cssText = `
            position: relative;
            overflow: hidden;
        `;
        
        virtualScrollContent = document.createElement('div');
        virtualScrollContent.className = 'virtual-scroll-content';
        virtualScrollContent.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
        `;
        
        virtualScrollViewport.appendChild(virtualScrollContent);
        virtualScrollContainer.appendChild(virtualScrollViewport);
        
        // 替换原有的故事网格
        storiesGrid.style.display = 'none';
        storiesGrid.parentNode.insertBefore(virtualScrollContainer, storiesGrid);
        
        // 添加滚动事件监听
        virtualScrollContainer.addEventListener('scroll', handleVirtualScroll);
    }
}

// 计算虚拟滚动参数
function calculateVirtualScrollParams() {
    const containerHeight = virtualScrollContainer.clientHeight;
    visibleItemsCount = Math.ceil(containerHeight / itemHeight) + 2; // 额外渲染2个项目作为缓冲
    totalHeight = filteredStories.length * itemHeight;
    virtualScrollViewport.style.height = totalHeight + 'px';
}

// 处理虚拟滚动
function handleVirtualScroll() {
    scrollTop = virtualScrollContainer.scrollTop;
    renderVirtualScrollItems();
}

// 渲染虚拟滚动项目
function renderVirtualScrollItems() {
    startPerformanceMonitor('虚拟滚动渲染');
    
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(startIndex + visibleItemsCount, filteredStories.length);
    
    const visibleItems = filteredStories.slice(startIndex, endIndex);
    
    let html = '';
    visibleItems.forEach((story, index) => {
        const actualIndex = startIndex + index;
        const top = actualIndex * itemHeight;
        html += `
            <div class="virtual-story-item" style="position: absolute; top: ${top}px; width: 100%; height: ${itemHeight}px;">
                ${createStoryCard(story)}
            </div>
        `;
    });
    
    virtualScrollContent.innerHTML = html;
    
    // 重新绑定事件
    bindVirtualScrollEvents();
    
    endPerformanceMonitor('虚拟滚动渲染');
}

// 绑定虚拟滚动事件
function bindVirtualScrollEvents() {
    virtualScrollContent.querySelectorAll('.story-card').forEach(card => {
        card.addEventListener('click', function() {
            const storyId = parseInt(this.dataset.storyId);
            showStoryDetail(storyId);
        });
    });
}

// 禁用虚拟滚动
function disableVirtualScroll() {
    virtualScrollEnabled = false;
    
    if (virtualScrollContainer) {
        virtualScrollContainer.style.display = 'none';
        storiesGrid.style.display = '';
    }
}

// 初始化懒加载
function initLazyLoading() {
    if (!lazyLoadEnabled || !('IntersectionObserver' in window)) {
        return;
    }
    
    intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    intersectionObserver.unobserve(img);
                }
            }
        });
    }, {
        rootMargin: '50px'
    });
}

// 初始化性能监控
function initPerformanceMonitor() {
    if (!performanceIndicator) {
        performanceIndicator = document.createElement('div');
        performanceIndicator.className = 'performance-indicator';
        document.body.appendChild(performanceIndicator);
    }
}

// 开始性能监控
function startPerformanceMonitor(operation) {
    renderStartTime = performance.now();
    renderCount++;
    
    if (performanceIndicator) {
        performanceIndicator.textContent = `${operation} 中...`;
        performanceIndicator.classList.add('show');
    }
}

// 结束性能监控
function endPerformanceMonitor(operation) {
    const renderTime = performance.now() - renderStartTime;
    
    if (performanceIndicator) {
        performanceIndicator.textContent = `${operation}: ${renderTime.toFixed(1)}ms | 渲染次数: ${renderCount}`;
        
        // 3秒后隐藏指示器
        setTimeout(() => {
            performanceIndicator.classList.remove('show');
        }, 3000);
    }
    
    console.log(`性能监控 - ${operation}: ${renderTime.toFixed(1)}ms`);
}

// 移动端下拉刷新功能
function initMobilePullToRefresh() {
    let startY = 0;
    let currentY = 0;
    let pullDistance = 0;
    let isPulling = false;
    let refreshThreshold = 80;
    
    const header = document.querySelector('.header');
    
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
            isPulling = true;
        }
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
        if (!isPulling || window.scrollY > 0) return;
        
        currentY = e.touches[0].clientY;
        pullDistance = currentY - startY;
        
        if (pullDistance > 0) {
            e.preventDefault();
            
            // 添加视觉反馈
            const opacity = Math.min(pullDistance / refreshThreshold, 1);
            header.style.transform = `translateY(${Math.min(pullDistance * 0.5, 40)}px)`;
            header.style.opacity = 1 - opacity * 0.3;
            
            if (pullDistance > refreshThreshold) {
                // 可以添加震动反馈（如果支持）
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            }
        }
    }, { passive: false });
    
    document.addEventListener('touchend', function(e) {
        if (!isPulling) return;
        
        isPulling = false;
        
        // 重置样式
        header.style.transform = '';
        header.style.opacity = '';
        
        if (pullDistance > refreshThreshold) {
            // 执行刷新
            showMessage('正在刷新数据...');
            setTimeout(() => {
                location.reload();
            }, 500);
        }
        
        pullDistance = 0;
    }, { passive: true });
}

// 动态生成分类按钮
function generateCategoryButtons() {
    if (!allStories || allStories.length === 0) return;
    
    // 获取所有唯一的分类
    const categories = [...new Set(allStories.map(story => story.category_name))].sort();
    
    // 更新导航栏分类
    const navList = document.querySelector('.nav-list');
    if (navList) {
        // 保留"全部故事"按钮
        navList.innerHTML = '<li><a href="#" class="nav-link active" data-category="all">全部故事</a></li>';
        
        // 添加动态分类
        categories.slice(0, 4).forEach(category => {
            const li = document.createElement('li');
            li.innerHTML = `<a href="#" class="nav-link" data-category="${category}">${category}</a>`;
            navList.appendChild(li);
        });
    }
    
    // 更新分类筛选按钮
    const filterButtons = document.querySelector('.filter-buttons');
    if (filterButtons) {
        // 保留"全部"按钮
        filterButtons.innerHTML = '<button class="filter-btn active" data-category="all">全部</button>';
        
        // 添加动态分类按钮
        categories.forEach(category => {
            const button = document.createElement('button');
            button.className = 'filter-btn';
            button.setAttribute('data-category', category);
            button.textContent = category;
            filterButtons.appendChild(button);
        });
    }
    
    console.log('✅ 动态生成分类按钮:', categories.length, '个分类');
}

// 加载故事数据
async function loadStories() {
    try {
        // 加载Supabase完整数据
        const [storiesResponse, categoriesResponse, contentsResponse] = await Promise.all([
            fetch('supabase_stories.json'),
            fetch('supabase_categories.json'),
            fetch('supabase_story_contents.json')
        ]);

        if (storiesResponse.ok && categoriesResponse.ok && contentsResponse.ok) {
            const stories = await storiesResponse.json();
            const categories = await categoriesResponse.json();
            const contents = await contentsResponse.json();
            
            // 创建内容映射
            const contentMap = {};
            contents.forEach(content => {
                contentMap[content.story_id] = content.content;
            });
            
            // 创建分类映射
            const categoryMap = {};
            categories.forEach(category => {
                categoryMap[category.id] = category.name;
            });
            
            // 合并数据并转换格式
            allStories = stories.map(story => ({
                id: story.id,
                title: story.title,
                category_name: categoryMap[story.category_id] || '未分类',
                category_id: story.category_id,
                excerpt: story.excerpt || '',
                length: story.length || 0,
                content: contentMap[story.id] || '内容暂未加载',
                created_at: story.created_at,
                reading_time: story.reading_time || Math.ceil((story.length || 0) / 200)
            }));
            
            console.log('✅ 成功加载Supabase完整数据:', allStories.length, '个故事');
            console.log('📂 分类数量:', categories.length);
            console.log('📝 内容数量:', contents.length);
            return;
        }
    } catch (error) {
        console.log('❌ Supabase数据加载失败，尝试加载备用数据:', error);
    }

    try {
        // 备用：加载增强版数据
        const response = await fetch('../enhanced_stories.json');
        if (response.ok) {
            allStories = await response.json();
            console.log('加载增强版故事数据:', allStories.length);
            return;
        }
    } catch (error) {
        console.log('增强版数据不可用，尝试加载快速版数据');
    }

    try {
        // 备用：加载快速版数据
        const response = await fetch('../quick_stories.json');
        if (response.ok) {
            allStories = await response.json();
            console.log('加载快速版故事数据:', allStories.length);
            return;
        }
    } catch (error) {
        console.log('快速版数据不可用，使用示例数据');
    }

    // 如果都加载失败，使用示例数据
    allStories = generateSampleStories();
    console.log('使用示例数据:', allStories.length);
}

// 生成示例故事数据
function generateSampleStories() {
    const sampleStories = [
        {
            id: 1,
            title: "小红帽",
            category_name: "童话故事",
            excerpt: "从前有个可爱的小姑娘，她总是戴着一顶红色的帽子...",
            length: 1200,
            content: "从前有个可爱的小姑娘，她总是戴着一顶红色的帽子，所以大家都叫她小红帽。有一天，妈妈让小红帽去看望生病的奶奶..."
        },
        {
            id: 2,
            title: "三只小猪",
            category_name: "童话故事",
            excerpt: "三只小猪要盖房子，老大用稻草，老二用木头，老三用砖头...",
            length: 1500,
            content: "从前有三只小猪，他们要离开妈妈独自生活。老大很懒，用稻草盖了一座房子..."
        },
        {
            id: 3,
            title: "龟兔赛跑",
            category_name: "寓言故事",
            excerpt: "骄傲的兔子和坚持不懈的乌龟进行了一场赛跑...",
            length: 800,
            content: "从前，有一只跑得很快的兔子和一只爬得很慢的乌龟。兔子总是嘲笑乌龟爬得慢..."
        }
    ];
    return sampleStories;
}

// 绑定事件
function bindEvents() {
    // 搜索功能
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // 分类筛选 - 使用事件委托支持动态生成的按钮
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('filter-btn')) {
            const category = e.target.dataset.category;
            setActiveFilter(e.target);
            filterByCategory(category);
        }
    });

    // 导航链接 - 使用事件委托支持动态生成的链接
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('nav-link')) {
            e.preventDefault();
            const category = e.target.dataset.category;
            setActiveNav(e.target);
            filterByCategory(category);
        }
    });

    // 视图切换
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            setActiveView(this);
            switchView(view);
        });
    });

    // 模态框
    closeModal.addEventListener('click', hideModal);
    storyModal.addEventListener('click', function(e) {
        if (e.target === this) {
            hideModal();
        }
    });

    // ESC键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideModal();
        }
    });

    // 高级筛选事件
    lengthRangeSelect.addEventListener('change', handleAdvancedFilter);
    readingTimeSelect.addEventListener('change', handleAdvancedFilter);
    sortBySelect.addEventListener('change', handleAdvancedFilter);
    clearFiltersBtn.addEventListener('click', clearAllFilters);
    
    // 朗读功能
    document.getElementById('readAloudBtn').addEventListener('click', readStoryAloud);
    
    // 收藏功能
    document.getElementById('favoriteBtn').addEventListener('click', toggleFavorite);
}

// 处理搜索
function handleSearch() {
    const query = searchInput.value.trim();
    
    // 移动端搜索时收起虚拟键盘
    if (window.innerWidth <= 768) {
        searchInput.blur();
    }
    
    if (query) {
        searchStories(query);
        
        // 显示搜索结果统计
        const resultCount = filteredStories.length;
        showMessage(`找到 ${resultCount} 个包含"${query}"的故事`);
        
        // 移动端自动滚动到结果区域
        if (window.innerWidth <= 768) {
            setTimeout(() => {
                document.querySelector('.stories-section').scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 100);
        }
    } else {
        filterStories();
        renderStories();
        renderPagination();
    }
}

// 搜索故事
function searchStories(query) {
    if (!query.trim()) {
        filterStories();
        return;
    }

    const searchTerm = query.toLowerCase();
    let searchResults = allStories.filter(story => {
        // 搜索标题
        if (story.title.toLowerCase().includes(searchTerm)) return true;
        
        // 搜索分类
        if (story.category_name.toLowerCase().includes(searchTerm)) return true;
        
        // 搜索摘要
        if (story.excerpt && story.excerpt.toLowerCase().includes(searchTerm)) return true;
        
        // 搜索完整内容
        if (story.content && story.content.toLowerCase().includes(searchTerm)) return true;
        
        return false;
    });

    // 应用分类筛选
    if (currentCategory !== 'all') {
        searchResults = searchResults.filter(story => 
            story.category_name === currentCategory
        );
    }
    
    // 应用高级筛选
    searchResults = applyAdvancedFilters(searchResults);
    
    filteredStories = searchResults;
    
    console.log(`🔍 搜索"${query}"找到 ${filteredStories.length} 个结果`);
    
    currentPage = 1;
    
    // 重新初始化虚拟滚动（如果需要）
    if (filteredStories.length > 100 && !virtualScrollEnabled) {
        initVirtualScroll();
    } else if (filteredStories.length <= 100 && virtualScrollEnabled) {
        disableVirtualScroll();
        renderStories();
    } else {
        renderStories();
    }
    
    renderPagination();
    
    // 更新搜索结果提示
    if (filteredStories.length === 0) {
        showMessage(`没有找到包含"${query}"的故事`);
    } else {
        showMessage(`找到 ${filteredStories.length} 个相关故事`);
    }
}

// 按分类筛选
function filterByCategory(category) {
    currentCategory = category;
    currentPage = 1;
    filterStories();
    
    // 重新初始化虚拟滚动（如果需要）
    if (filteredStories.length > 100 && !virtualScrollEnabled) {
        initVirtualScroll();
    } else if (filteredStories.length <= 100 && virtualScrollEnabled) {
        disableVirtualScroll();
        renderStories();
    } else {
        renderStories();
    }
    
    renderPagination();
}

// 筛选故事
function filterStories() {
    let stories = allStories;
    
    // 分类筛选
    if (currentCategory !== 'all') {
        stories = stories.filter(story => 
            story.category_name === currentCategory
        );
    }
    
    // 高级筛选
    stories = applyAdvancedFilters(stories);
    
    filteredStories = stories;
}

// 应用高级筛选
function applyAdvancedFilters(stories) {
    let filtered = [...stories];
    
    // 字数范围筛选
    if (currentFilters.lengthRange !== 'all') {
        filtered = filtered.filter(story => {
            const length = story.length || 0;
            switch (currentFilters.lengthRange) {
                case 'short':
                    return length <= 500;
                case 'medium':
                    return length > 500 && length <= 2000;
                case 'long':
                    return length > 2000;
                default:
                    return true;
            }
        });
    }
    
    // 阅读时间筛选
    if (currentFilters.readingTime !== 'all') {
        filtered = filtered.filter(story => {
            const length = story.length || 0;
            const readingTime = Math.ceil(length / 200); // 假设每分钟200字
            switch (currentFilters.readingTime) {
                case 'quick':
                    return readingTime <= 3;
                case 'medium':
                    return readingTime > 3 && readingTime <= 10;
                case 'long':
                    return readingTime > 10;
                default:
                    return true;
            }
        });
    }
    
    // 排序
    if (currentFilters.sortBy !== 'default') {
        filtered.sort((a, b) => {
            switch (currentFilters.sortBy) {
                case 'title':
                    return a.title.localeCompare(b.title);
                case 'length':
                    return (b.length || 0) - (a.length || 0);
                case 'category':
                    return a.category_name.localeCompare(b.category_name);
                default:
                    return 0;
            }
        });
    }
    
    return filtered;
}

// 处理高级筛选
function handleAdvancedFilter() {
    currentFilters.lengthRange = lengthRangeSelect.value;
    currentFilters.readingTime = readingTimeSelect.value;
    currentFilters.sortBy = sortBySelect.value;
    
    filterStories();
    renderStories();
    renderPagination();
    
    console.log('应用高级筛选:', currentFilters);
    console.log('筛选后故事数量:', filteredStories.length);
}

// 清除所有筛选
function clearAllFilters() {
    // 重置分类筛选
    currentCategory = 'all';
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('.filter-btn[data-category="all"]').classList.add('active');
    
    // 重置高级筛选
    currentFilters = {
        lengthRange: 'all',
        readingTime: 'all',
        sortBy: 'default'
    };
    
    lengthRangeSelect.value = 'all';
    readingTimeSelect.value = 'all';
    sortBySelect.value = 'default';
    
    // 清除搜索
    searchInput.value = '';
    
    filterStories();
    renderStories();
    renderPagination();
    
    console.log('已清除所有筛选条件');
}

// 渲染故事列表
function renderStories() {
    // 如果启用了虚拟滚动，使用虚拟滚动渲染
    if (virtualScrollEnabled) {
        renderVirtualScrollItems();
        return;
    }
    
    startPerformanceMonitor('传统渲染');
    
    // 传统分页渲染
    const startIndex = (currentPage - 1) * storiesPerPage;
    const endIndex = startIndex + storiesPerPage;
    const currentStories = filteredStories.slice(startIndex, endIndex);

    if (currentStories.length === 0) {
        storiesGrid.innerHTML = '<div class="no-stories"><p>暂无故事数据</p></div>';
        endPerformanceMonitor('传统渲染');
        return;
    }

    const storiesHTML = currentStories.map(story => createStoryCard(story)).join('');
    storiesGrid.innerHTML = storiesHTML;

    // 绑定故事卡片点击事件
    document.querySelectorAll('.story-card').forEach(card => {
        card.addEventListener('click', function() {
            const storyId = parseInt(this.dataset.storyId);
            showStoryDetail(storyId);
        });
    });
    
    // 初始化懒加载图片
    if (lazyLoadEnabled && intersectionObserver) {
        document.querySelectorAll('img[data-src]').forEach(img => {
            intersectionObserver.observe(img);
        });
    }
    
    endPerformanceMonitor('传统渲染');
}

// 创建故事卡片
function createStoryCard(story) {
    const excerpt = story.excerpt || '暂无简介';
    const length = story.length || 0;
    const readingTime = Math.ceil(length / 300);
    
    return `
        <div class="story-card" data-story-id="${story.id}">
            <h3 class="story-title">${story.title}</h3>
            <div class="story-meta">
                <span class="story-category">${story.category_name}</span>
                <span class="story-length">${length} 字</span>
            </div>
            <p class="story-preview">${excerpt}</p>
            <div class="story-footer">
                <span class="story-read-time">${readingTime} 分钟阅读</span>
                <button class="read-btn">阅读</button>
            </div>
        </div>
    `;
}

// 显示故事详情
function showStoryDetail(storyId) {
    const story = allStories.find(s => s.id === storyId);
    if (!story) {
        showError('故事不存在');
        return;
    }

    modalTitle.textContent = story.title;
    modalCategory.textContent = story.category_name;
    modalLength.textContent = `${story.length || 0} 字`;
    
    // 显示故事内容
    if (story.content) {
        modalContent.innerHTML = formatStoryContent(story.content);
    } else {
        modalContent.innerHTML = `
            <p>${story.excerpt || '暂无内容'}</p>
            <p class="content-note">完整内容正在加载中...</p>
        `;
        // 尝试异步加载完整内容
        loadFullStoryContent(storyId);
    }

    showModal();
}

// 格式化故事内容
function formatStoryContent(content) {
    if (!content) return '<p>暂无内容</p>';
    
    // 将内容按段落分割并格式化
    const paragraphs = content.split('\n').filter(p => p.trim());
    return paragraphs.map(p => `<p>${p.trim()}</p>`).join('');
}

// 异步加载完整故事内容
async function loadFullStoryContent(storyId) {
    try {
        // 这里可以实现从服务器加载完整内容的逻辑
        // 目前使用现有数据
        const story = allStories.find(s => s.id === storyId);
        if (story && story.content) {
            modalContent.innerHTML = formatStoryContent(story.content);
        }
    } catch (error) {
        console.error('加载故事内容失败:', error);
    }
}

// 渲染分页
function renderPagination() {
    const totalPages = Math.ceil(filteredStories.length / storiesPerPage);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let paginationHTML = '';
    
    // 上一页
    if (currentPage > 1) {
        paginationHTML += `<button class="page-btn" onclick="goToPage(${currentPage - 1})">
            <i class="fas fa-chevron-left"></i> 上一页
        </button>`;
    }

    // 页码
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        paginationHTML += `<button class="page-btn" onclick="goToPage(1)">1</button>`;
        if (startPage > 2) {
            paginationHTML += `<span class="page-ellipsis">...</span>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === currentPage ? 'active' : '';
        paginationHTML += `<button class="page-btn ${activeClass}" onclick="goToPage(${i})">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<span class="page-ellipsis">...</span>`;
        }
        paginationHTML += `<button class="page-btn" onclick="goToPage(${totalPages})">${totalPages}</button>`;
    }

    // 下一页
    if (currentPage < totalPages) {
        paginationHTML += `<button class="page-btn" onclick="goToPage(${currentPage + 1})">
            下一页 <i class="fas fa-chevron-right"></i>
        </button>`;
    }

    pagination.innerHTML = paginationHTML;
}

// 跳转到指定页面
function goToPage(page) {
    currentPage = page;
    renderStories();
    renderPagination();
    
    // 滚动到顶部
    document.querySelector('.stories-section').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// 更新统计信息
function updateStats() {
    if (!allStories || allStories.length === 0) {
        animateNumber(totalStories, 0);
        animateNumber(totalCategories, 0);
        animateNumber(avgLength, 0);
        return;
    }
    
    const categories = [...new Set(allStories.map(story => story.category_name))];
    const totalLength = allStories.reduce((sum, story) => sum + (story.length || 0), 0);
    const avgLengthValue = allStories.length > 0 ? Math.round(totalLength / allStories.length) : 0;

    // 动画更新数字
    animateNumber(totalStories, allStories.length);
    animateNumber(totalCategories, categories.length);
    animateNumber(avgLength, avgLengthValue);
    
    console.log('📊 统计信息更新:', {
        totalStories: allStories.length,
        totalCategories: categories.length,
        avgLength: avgLengthValue,
        categories: categories.slice(0, 5)
    });
}

// 数字动画
function animateNumber(element, targetValue) {
    const startValue = 0;
    const duration = 1000;
    const startTime = Date.now();

    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentValue = Math.round(startValue + (targetValue - startValue) * progress);
        
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// 设置活跃的筛选按钮
function setActiveFilter(activeBtn) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    activeBtn.classList.add('active');
}

// 设置活跃的导航链接
function setActiveNav(activeLink) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    activeLink.classList.add('active');
}

// 设置活跃的视图按钮
function setActiveView(activeBtn) {
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    activeBtn.classList.add('active');
}

// 切换视图
function switchView(view) {
    currentView = view;
    if (view === 'list') {
        storiesGrid.classList.add('list-view');
    } else {
        storiesGrid.classList.remove('list-view');
    }
}

// 显示/隐藏加载指示器
function showLoading(show) {
    loadingIndicator.style.display = show ? 'block' : 'none';
    storiesGrid.style.display = show ? 'none' : 'grid';
}

// 显示模态框
function showModal() {
    storyModal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

// 隐藏模态框
function hideModal() {
    storyModal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

// 显示消息
function showMessage(message) {
    // 创建临时消息元素
    const messageEl = document.createElement('div');
    messageEl.className = 'message-toast';
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #667eea;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        z-index: 3000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

// 显示错误
function showError(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'error-toast';
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #e74c3c;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        z-index: 3000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.remove();
    }, 5000);
}

// 朗读故事
function readStoryAloud() {
    const content = modalContent.textContent;
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(content);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
        
        showMessage('开始朗读故事');
    } else {
        showError('您的浏览器不支持语音朗读功能');
    }
}

// 收藏功能
function toggleFavorite() {
    const storyTitle = modalTitle.textContent;
    const favorites = JSON.parse(localStorage.getItem('favoriteStories') || '[]');
    
    const index = favorites.indexOf(storyTitle);
    if (index > -1) {
        favorites.splice(index, 1);
        showMessage('已取消收藏');
    } else {
        favorites.push(storyTitle);
        showMessage('已添加到收藏');
    }
    
    localStorage.setItem('favoriteStories', JSON.stringify(favorites));
    updateFavoriteButton();
}

// 更新收藏按钮状态
function updateFavoriteButton() {
    const storyTitle = modalTitle.textContent;
    const favorites = JSON.parse(localStorage.getItem('favoriteStories') || '[]');
    const favoriteBtn = document.getElementById('favoriteBtn');
    
    if (favorites.includes(storyTitle)) {
        favoriteBtn.innerHTML = '<i class="fas fa-heart"></i> 已收藏';
        favoriteBtn.style.background = '#e74c3c';
    } else {
        favoriteBtn.innerHTML = '<i class="far fa-heart"></i> 收藏';
        favoriteBtn.style.background = '#6c757d';
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .page-ellipsis {
        padding: 0.6rem 1rem;
        color: #6c757d;
    }
    
    .message-toast,
    .error-toast {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .no-stories {
        text-align: center;
        padding: 3rem;
        color: #6c757d;
        grid-column: 1 / -1;
    }
    
    .content-note {
        font-style: italic;
        color: #6c757d;
        text-align: center;
        margin-top: 2rem;
    }
`;
document.head.appendChild(style);