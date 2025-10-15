#!/usr/bin/env python3

import getpass
import sys
import json
import os


MAX_ATTEMPTS = 3

# Hàm đọc file passwd.json
def read_passwd():
    """Đọc dữ liệu tài khoản từ file JSON nằm cùng thư mục script."""
    # Lấy đường dẫn tuyệt đối tới file hiện tại
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    json_path = os.path.join(script_dir, ".passwd.json")

    if not os.path.exists(json_path):
        print(f"Không tìm thấy file JSON tại: {json_path}")
        return False

    try:
        with open(json_path, 'r') as f:
            accounts = json.load(f)
            return accounts
    except json.JSONDecodeError:
        print(f"Lỗi: {json_path} không phải định dạng JSON hợp lệ")
        return False


# Đăng nhập
def authenticate():
    """Yêu cầu người dùng nhập mật khẩu."""
    attempts = 0
    accounts = read_passwd()
    while attempts < MAX_ATTEMPTS:
        # getpass ẩn đầu vào mật khẩu
        username_input = input("Nhập username: ")
        password_input = getpass.getpass("Nhập password: ")

        if username_input in accounts:
            account_data = accounts[username_input]

            if password_input == account_data.get("password"):
                role = account_data.get("role")                     # chưa sử dụng!!
                print("=== Đăng nhập thành công ===")
                print(f"Chào mừng {username_input}")
                return True
        else:
            attempts += 1
            remaining = MAX_ATTEMPTS - attempts
            if remaining > 0:
                print(f"Sai username hoặc mật khẩu. Còn {remaining} lần thử.")
            else:
                print("Bạn đã nhập sai 3 lần. Truy cập bị từ chối.")

    return False

if __name__ == "__main__":
    if authenticate():
        # Trả về 0 (thành công) cho Shell
        sys.exit(0)
    else:
        # Trả về 1 (thất bại) cho Shell
        sys.exit(1)
