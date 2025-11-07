import requests # 1. 导入 requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# --- 配置 ---
# (关键修改：已替换为您 App 的 URL)
app_url = "https://risk-dashboard-ieaxltxpoxwctmisasjtdv.streamlit.app/"
log_file = "click_log.txt"
log_retention_days = 2
sleep_text = "get this app back up" # 睡眠按钮上的关键文字

# --- 清理旧日志函数 (来自您的脚本) ---
def clean_old_logs():
    if not os.path.exists(log_file):
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

    except Exception as e:
        print(f"日志清理失败：{e}")

# --- 执行清理 ---
clean_old_logs()

# --- 2. 阶段一 (轻量级检查) ---
needs_wakeup = False
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"开始轻量级检查: {app_url}")
try:
    # 伪装成浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    # 设置超时为 20 秒
    response = requests.get(app_url, timeout=20, headers=headers)
    response.raise_for_status() # 如果状态码不是 200-299, 抛出异常
    
    page_content = response.text

    # 检查页面内容
    if sleep_text in page_content:
        print("检测到应用处于睡眠状态。即将启动 Selenium 唤醒...")
        needs_wakeup = True
        log_entry = f"[{timestamp}] [轻量检查] 检测到睡眠，准备唤醒\n"
    else:
        print("应用已处于唤醒状态。无需操作。")
        needs_wakeup = False
        log_entry = f"[{timestamp}] [轻量检查] 应用已唤醒，跳过点击\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except requests.exceptions.RequestException as e:
    # 如果 requests 检查失败 (例如超时或503错误), 我们也认为需要唤醒
    print(f"轻量级检查失败: {e}。将尝试启动 Selenium... (可能是应用已损坏或超时)")
    needs_wakeup = True
    log_entry = f"[{timestamp}] [轻量检查] 检查失败 ({e})，尝试强行唤醒\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)


# --- 3. 阶段二 (仅在需要时运行 Selenium) ---
if needs_wakeup:
    print("启动 Selenium 唤醒流程...")
    driver = None # 先声明
    try:
        # 设置无头浏览器参数
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # 创建 Chrome 驱动
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(app_url)
        print("已打开网页 (Selenium)，等待页面加载 30 秒...")
        time.sleep(30) # 初次加载等待

        # 查找按钮
        buttons = driver.find_elements(By.XPATH, f"//button[contains(text(), '{sleep_text}')]")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if buttons:
            buttons[0].click()
            print("检测到按钮，已点击。等待 60 秒完成恢复操作...")
            time.sleep(60) # 点击后等待
            log_entry = f"[{timestamp}] [Selenium] 按钮已点击，已等待60秒完成\n"
        else:
            print("Selenium 未检测到按钮 (可能在轻量检查后刚被唤醒)。")
            log_entry = f"[{timestamp}] [Selenium] 未发现按钮，未执行点击\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f"[{timestamp}] [Selenium] 错误：{str(e)}\n"
        print(f"Selenium 发生错误：{e}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_msg)
    
    finally:
        if driver: # 确保 driver 成功初始化
            driver.quit()
        print("Selenium 流程结束。")

else:
    print("检查完成，无需 Selenium。")
