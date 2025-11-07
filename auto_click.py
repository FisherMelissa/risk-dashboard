import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# --- 配置 ---
app_url = "https://risk-dashboard-ieaxltxpoxwctmisasjtdv.streamlit.app/"
log_file = "click_log.txt"
log_retention_days = 2
sleep_text = "get this app back up" # 睡眠按钮上的关键文字 (保持小写)

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(app_url, timeout=20, headers=headers)
    response.raise_for_status() 
    
    # --- V3.10 关键修复：将页面内容转换为小写再检查 ---
    page_content = response.text.lower()
    # --------------------------------------------------

    # 检查页面内容 (现在是小写 vs 小写)
    if sleep_text in page_content:
        print("检测到应用处于睡眠状态。即将启动 Selenium 唤醒...")
        needs_wakeup = True
        log_entry = f"[{timestamp}] [轻量检查] 检测到睡眠，准备唤醒\n"
    else:
        print("应用已处于唤醒状态。无需操作。
