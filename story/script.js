// 全局变量
let storiesData = {};
let currentCategory = 'all';
let currentPage = 1;
const storiesPerPage = 12;
let filteredStories = [];
let allStories = [];

// DOM元素
let storiesGrid, storyCountElement, loadMoreBtn, searchInput, modal, modalTitle, modalCategory, modalContent, closeBtn;

// 获取DOM元素
function initializeElements() {
    storiesGrid = document.getElementById('storiesGrid');
    storyCountElement = document.getElementById('storyCount');
    loadMoreBtn = document.getElementById('loadMoreBtn');
    searchInput = document.getElementById('searchInput');
    modal = document.getElementById('storyModal');
    modalTitle = document.getElementById('modalTitle');
    modalCategory = document.getElementById('modalCategory');
    modalContent = document.getElementById('modalContent');
    closeBtn = document.querySelector('.close-btn');
}

// 加载故事数据
async function loadStoriesData() {
    try {
        const response = await fetch('stories_data.json');
        const data = await response.json();
        
        // 转换数据格式以适配现有代码
        storiesData = {};
        allStories = [];
        
        for (const [categoryName, categoryData] of Object.entries(data.categories)) {
            storiesData[categoryName] = categoryData.stories;
            allStories = allStories.concat(categoryData.stories);
        }
        
        filteredStories = [...allStories];
        
        console.log('成功加载故事数据:', Object.keys(storiesData).length, '个分类');
        console.log('总故事数:', data.crawl_info.total_stories);
        
        return true;
    } catch (error) {
        console.error('加载故事数据失败:', error);
        // 如果加载失败，使用默认数据
        storiesData = {
            "睡前故事": [
                {
                    title: "小老鼠打电话",
                    content: "冬天到了，天气也越来越冷了，小老鼠们都挤在一块，可暖和了...",
                    category: "睡前故事"
                }
            ]
        };
        allStories = storiesData["睡前故事"];
        filteredStories = [...allStories];
        return false;
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    // 加载更多按钮
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreStories);
    }
    
    // 模态框关闭
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }
    
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    

}

// 设置分类筛选
function setupCategoryFilters() {
    const categoryFilters = document.getElementById('categoryFilters');
    if (!categoryFilters) return;
    
    // 获取所有分类
    const categories = ['all', ...Object.keys(storiesData)];
    const categoryNames = {
        'all': '全部',
        '睡前故事': '睡前故事',
        '励志故事': '励志故事',
        '智慧故事': '智慧故事',
        '友谊故事': '友谊故事',
        '教育故事': '教育故事',
        '冒险故事': '冒险故事',
        '节日故事': '节日故事',
        '奇幻故事': '奇幻故事'
    };
    
    // 清空现有按钮
    categoryFilters.innerHTML = '';
    
    // 创建分类按钮
    categories.forEach(category => {
        const button = document.createElement('button');
        button.className = 'category-btn';
        button.dataset.category = category;
        button.textContent = categoryNames[category] || category;
        
        // 设置默认选中状态
        if (category === currentCategory) {
            button.classList.add('active');
        }
        
        // 添加点击事件
        button.addEventListener('click', function() {
            // 移除所有按钮的active类
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            // 添加当前按钮的active类
            this.classList.add('active');
            
            // 获取分类
            currentCategory = this.dataset.category;
            currentPage = 1;
            
            // 筛选故事
            filterStories();
            displayStories();
            updateStoryCount();
        });
        
        categoryFilters.appendChild(button);
    });
}

// 筛选故事
function filterStories() {
    if (currentCategory === 'all') {
        filteredStories = [...allStories];
    } else {
        filteredStories = allStories.filter(story => story.category === currentCategory);
    }
}

// 显示故事
function displayStories() {
    if (!storiesGrid) return;
    
    const startIndex = 0;
    const endIndex = currentPage * storiesPerPage;
    const storiesToShow = filteredStories.slice(startIndex, endIndex);
    
    if (currentPage === 1) {
        storiesGrid.innerHTML = '';
    }
    
    storiesToShow.forEach((story, index) => {
        if (index >= (currentPage - 1) * storiesPerPage) {
            const storyCard = createStoryCard(story);
            storiesGrid.appendChild(storyCard);
        }
    });
    
    // 更新加载更多按钮
    if (loadMoreBtn) {
        if (endIndex >= filteredStories.length) {
            loadMoreBtn.style.display = 'none';
        } else {
            loadMoreBtn.style.display = 'block';
        }
    }
}

// 创建故事卡片
function createStoryCard(story) {
    const card = document.createElement('div');
    card.className = 'story-card';
    
    // 截取内容预览
    const preview = story.content.length > 100 ? 
        story.content.substring(0, 100) + '...' : 
        story.content;
    
    card.innerHTML = `
        <div class="story-category">${story.category}</div>
        <h3 class="story-title">${story.title}</h3>
        <p class="story-preview">${preview}</p>
        <div class="story-meta">
            <span class="word-count">${story.content.length} 字</span>
        </div>
    `;
    
    // 添加点击事件
    card.addEventListener('click', () => openStoryModal(story));
    
    return card;
}

// 打开故事模态框
function openStoryModal(story) {
    if (modal && modalTitle && modalCategory && modalContent) {
        modalTitle.textContent = story.title;
        modalCategory.textContent = story.category;
        modalContent.textContent = story.content;
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

// 关闭模态框
function closeModal() {
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// 加载更多故事
function loadMoreStories() {
    currentPage++;
    displayStories();
    updateStoryCount();
}

// 更新故事计数
function updateStoryCount() {
    if (storyCountElement) {
        const currentShowing = Math.min(currentPage * storiesPerPage, filteredStories.length);
        storyCountElement.textContent = `显示 ${currentShowing} / ${filteredStories.length} 个故事`;
    }
}

// 搜索处理
function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        filterStories();
    } else {
        filteredStories = allStories.filter(story => 
            story.title.toLowerCase().includes(searchTerm) ||
            story.content.toLowerCase().includes(searchTerm) ||
            story.category.toLowerCase().includes(searchTerm)
        );
    }
    
    currentPage = 1;
    displayStories();
    updateStoryCount();
}

// 显示空状态
function showEmptyState() {
    if (storiesGrid) {
        storiesGrid.innerHTML = `
            <div class="empty-state">
                <h3>暂无故事</h3>
                <p>请稍后再试或检查网络连接</p>
            </div>
        `;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', async function() {
    initializeElements();
    
    // 先加载数据，再设置事件监听器
    const loadSuccess = await loadStoriesData();
    if (loadSuccess) {
        setupEventListeners();
        setupCategoryFilters();
        displayStories();
        updateStoryCount();
    } else {
        setupEventListeners();
        showEmptyState();
    }
});