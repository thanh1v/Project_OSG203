#!/bin/bash
# Lấy thư mục chứa script (.init.sh) -> Đây chính là thư mục secure-dir
SECURE_DIR=$(dirname "$0")

# Chạy main.py
python3 "$SECURE_DIR/main.py"

# Mã thoát
exit $?
