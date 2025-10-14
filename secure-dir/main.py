#!/usr/bin/env python3

import getpass
import sys

# Mật khẩu
USERNAME = "admin"
PASSWORD = "admin"
MAX_ATTEMPTS = 3

def authenticate():
    """Yêu cầu người dùng nhập mật khẩu."""
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        # getpass ẩn đầu vào mật khẩu
        username_input = input("Nhập username: ")
        password_input = getpass.getpass("Nhập password: ")

        if password_input == PASSWORD and username_input == USERNAME:
            print("Đăng nhập thành công! Tiếp tục vào thư mục...")
            return True
        else:
            attempts += 1
            remaining = MAX_ATTEMPTS - attempts
            if remaining > 0:
                print(f"Mật khẩu sai. Còn {remaining} lần thử.")
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
