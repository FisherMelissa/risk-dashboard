# V3.15 - 最终修复：使用您截图中 100% 正确的标题
import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # 导入 TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

# --- 配置 ---
APP_URL = "https://risk-dashboard-ieaxltxpoxwctmisasjtdv.streamlit.app/"
LOG_FILE = "click_log.txt"
LOG_RETENTION_DAYS = 2
SLEEP_BUTTON_TEXT = "get this app back up" # 按钮上的文字

# --- V3.15 关键修复：使用您截图 (image_68a81f.png) 中的“真相”标题 ---
APP_TITLE_TEXT = "青少年风险动态评估与分级干预系统 (V3.3)"
# -----------------------------------------------------------------

def log_message(message):
    """将消息写入日志文件并打印"""
    print(message) 
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"写入日志文件失败: {e}")

# --- 清理旧日志函数 (不变) ---
def clean_old_logs():
    if not os.path.exists(LOG_FILE):
        log_message("日志文件不存在，跳过清理。")
        return
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f: lines = f.readlines()
        cleaned_lines = []
        cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
        for line in lines:
            if line.startswith("["):
                try:
                    timestamp = datetime.strptime(line.split("]")[0][1:], "%Y-%m-%d %H:%M:%S")
                    if timestamp >= cutoff: cleaned_lines.append(line)
                except: cleaned_lines.append(line)
            else: cleaned_lines.append(line)
        with open(LOG_FILE, "w", encoding="utf-8") as f: f.writelines(cleaned_lines)
        log_message("旧日志清理完成。")
    except Exception as e: log_message(f"日志清理失败：{e}")


# --- V3.15 核心：修复了 V3.13 的 try/except 逻辑 ---
def run_selenium_wakeup():
    log_message("启动 Selenium 唤醒流程...")
    driver = None
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(180) # 3 分钟

        log_message(f"正在打开 {APP_URL}...")
        driver.get(APP_URL)

        # 核心逻辑：我们“等待” 2 分钟 (120秒)，看“睡眠按钮”是否会出现
        wait = WebDriverWait(driver, 120) 
        
        # 不区分大小写的 XPath 查询
        xpath_query = f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{SLEEP_BUTTON_TEXT}')]"
        
        try:
            # 1. 尝试寻找“睡眠按钮”
            log_message("正在检测“睡眠按钮” (最长等待 120 秒)...")
            button = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_query))
            )
            
            # 2. 如果找到了 (即 App 睡着了)
            log_message("检测到睡眠按钮，正在点击...")
            button.click()
            
            # 3. 点击后，等待 App 标题加载 (使用 V3.15 的正确标题)
            log_message("已点击，等待 App 标题加载...")
            wait.until(EC.title_contains(APP_TITLE_TEXT))
            log_message(f"App 标题 '{APP_TITLE_TEXT}' 加载成功。App 已唤醒！")
        
        except TimeoutException:
            # 4. 如果 120 秒内“没找到”睡眠按钮
            #    这意味着 App *本来就是醒着的*
            log_message("未在 120 秒内检测到睡眠按钮。")
            
            # 5. 我们最后验证一次标题是否正确 (使用 V3.15 的正确标题)
            if APP_TITLE_TEXT in driver.title:
                log_message(f"App 标题 '{APP_TITLE_TEXT}' 已存在。App 确认处于唤醒状态。")
            else:
                log_message(f"警告：App 已唤醒，但标题不正确！(期望: '{APP_TITLE_TEXT}', 实际: '{driver.title}')")

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f"[{timestamp}] [Selenium] 错误：{str(e)}\n"
        log_message(f"Selenium 发生严重错误：{e}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_msg)
    
    finally:
        if driver: 
            driver.quit()
        log_message("Selenium 流程结束。")

# --- 主执行 ---
if __name__ == "__main__":
    clean_old_logs()
    run_selenium_wakeup()
    log_message("检查完成。")
