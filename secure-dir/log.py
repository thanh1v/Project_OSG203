import logging
import os
from datetime import datetime, timedelta

# Đặt log file cùng thư mục với script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "login.log")

# Cấu hình logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    force=True
)

def log_login(user, role):
    """Ghi nhận sự kiện đăng nhập"""
    logging.info(f"LOGIN {user} - {role}")

def check_alerts(user):
    """Kiểm tra số lần đăng nhập và cảnh báo"""
    if not os.path.exists(LOG_FILE):
        return

    now = datetime.now()
    today = now.date()
    five_min_ago = now - timedelta(minutes=5)

    daily_count = 0
    window_count = 0

    with open(LOG_FILE, "r") as f:
        for line in f:
            if f"user={user}" in line:
                ts_str = line.split(" - ")[0]
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S,%f")

                if ts.date() == today:
                    daily_count += 1
                if ts >= five_min_ago:
                    window_count += 1

    if daily_count > 10:
        print(f"[ALERT] User {user} đăng nhập {daily_count} lần hôm nay (>10)")
    if window_count >= 3:
        print(f"[ALERT] User {user} đăng nhập {window_count} lần trong 5 phút")

def handle_login(user, role):
    log_login(user, role)
    check_alerts(user)
