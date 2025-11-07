import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os
import sys # 导入 sys 模块

# --- 配置 ---
app_url = "https://risk-dashboard-ieaxltxpoxwctmisasjtdv.streamlit.app/"
log_file = "click_log.txt"
log_retention_days = 2
sleep_text = "get this app back up" # 睡眠按钮上的关键文字 (保持小写)

def log_message(message):
    """将消息写入日志文件并打印"""
    print(message) # 确保 GitHub Actions 日志能看到
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"写入日志文件失败: {e}")

# --- 清理旧日志函数 (来自您的脚本) ---
def clean_old_logs():
    if not os.path.exists(log_file):
        log_message("日志文件不存在，跳过清理。")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = []
        cutoff = datetime.now() - timedelta(days=log_retention_days)

        for line in lines:
            if line.startswith("["):
                try:
                    timestamp_str = line.split("]")[0][1:]
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if timestamp >= cutoff:
                        cleaned_lines.append(line)
                except:
                    cleaned_lines.append(line) # 非时间行保留
            else:
                cleaned_lines.append(line)

        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
        log_message("旧日志清理完成。")

    except Exception as e:
        log_message(f"日志清理失败：{e}")

# --- 2. 阶段一 (轻量级检查) ---
def lightweight_check():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message(f"开始轻量级检查: {app_url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(app_url, timeout=20, headers=headers)
        response.raise_for_status() 
        
        page_content = response.text.lower() # V3.10 修复

        if sleep_text in page_content:
            log_message("检测到应用处于睡眠状态。即将启动 Selenium 唤醒...")
            log_entry = f"[{timestamp}] [轻量检查] 检测到睡眠，准备唤醒\n"
            needs_wakeup = True
        else:
            # --- V3.11 语法修复：添加了缺失的 ")" ---
            log_message("应用已处于唤醒状态。无需操作。")
            # -------------------------------------
            log_entry = f"[{timestamp}] [轻量检查] 应用已唤醒，跳过点击\n"
            needs_wakeup = False

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        return needs_wakeup

    except requests.exceptions.RequestException as e:
        log_message(f"轻量级检查失败: {e}。将尝试启动 Selenium... (可能是应用已损坏或超时)")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [轻量检查] 检查失败 ({e})，尝试强行唤醒\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        return True # 失败了，也需要唤醒


# --- 3. 阶段二 (仅在需要时运行 Selenium) ---
def heavy_wakeup():
    log_message("启动 Selenium 唤醒流程...")
    driver = None 
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(app_url)
        log_message("已打开网页 (Selenium)，等待页面加载 30 秒...")
        time.sleep(30) 

        # V3.10 修复：不区分大小写的 XPath
        lower_case_sleep_text = sleep_text
        xpath_query = f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{lower_case_sleep_text}')]"
        
        buttons = driver.find_elements(By.XPATH, xpath_query)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if buttons:
            buttons[0].click()
            log_message("检测到按钮，已点击。等待 60 秒完成恢复操作...")
            time.sleep(60) 
            log_entry = f"[{timestamp}] [Selenium] 按钮已点击，已等待60秒完成\n"
        else:
            log_message("Selenium 未检测到按钮 (可能在轻量检查后刚被唤醒)。")
            log_entry = f"[{timestamp}] [Selenium] 未发现按钮，未执行点击\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f"[{timestamp}] [Selenium] 错误：{str(e)}\n"
        log_message(f"Selenium 发生错误：{e}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_msg)
    
    finally:
        if driver: 
            driver.quit()
        log_message("Selenium 流程结束。")

# --- 主执行 ---
if __name__ == "__main__":
    clean_old_logs()
    
    # 1. 运行轻量级检查
    needs_wakeup = lightweight_check()
    
    # 2. 如果需要，才运行重量级唤醒
    if needs_wakeup:
        heavy_wakeup()
    else:
        log_message("检查完成，无需 Selenium。")
