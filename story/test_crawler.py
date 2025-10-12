import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_website_structure():
    """测试网站结构"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("访问网站...")
        driver.get("https://storynook.cn")
        
        # 等待页面加载
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)
        
        print("页面标题:", driver.title)
        print("页面URL:", driver.current_url)
        
        # 获取页面源码的前1000个字符
        page_source = driver.page_source
        print("页面源码长度:", len(page_source))
        print("页面源码前500字符:")
        print(page_source[:500])
        
        # 尝试不同的选择器
        selectors_to_test = [
            'div', 'article', '.card', '.item', '.story',
            '[class*="card"]', '[class*="story"]', '[class*="item"]'
        ]
        
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"选择器 '{selector}': 找到 {len(elements)} 个元素")
                    # 显示前3个元素的文本
                    for i, elem in enumerate(elements[:3]):
                        text = elem.text.strip()
                        if text:
                            print(f"  元素 {i+1}: {text[:100]}...")
            except Exception as e:
                print(f"选择器 '{selector}' 出错: {e}")
        
        # 滚动页面
        print("\n开始滚动页面...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print(f"滚动 {i+1} 次")
        
        # 再次检查元素数量
        print("\n滚动后重新检查:")
        for selector in ['.card', '[class*="card"]', 'div']:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"选择器 '{selector}': 找到 {len(elements)} 个元素")
            except:
                pass
                
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_website_structure()