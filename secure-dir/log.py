import logging
import os
from datetime import datetime, timedelta

# Đặt log file cùng thư mục với script
#LOG_FILE = "login.log"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "login.log")

# Cấu hình logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    force=True
)

def log_event(user, role, event_type, status=None):
    
    if status:
        logging.info(f"{event_type.upper()} {user} - role:{role} - {status}")
    else:
        logging.info(f"{event_type.upper()} {user} - role:{role}")

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
            if f"LOGIN {user}" in line:
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
    log_event(user, role, "login", "success")
    check_alerts(user)

def handle_login_fail(user, role="unknown"):
    log_event(user, role, "login", "fail")

def handle_logout(user, role):
    log_event(user, role, "logout")


    
