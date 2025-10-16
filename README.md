# Project môn học OSG203 
# Title: Secure Linux File System

Mô tả: 
- Mã hóa và bảo về 1 thư mục đặc biệt trong môi trường Linux.
- Cần đăng nhập để truy cập vào file này.
- Mật khẩu lưu trữ được mã hóa AES-128.

# Các tài nguyên cần thiết
## Python cho Linux
- Ubuntu/Desbian
``` bash
sudo apt install python3
```
- CentOS/Red Hat
``` bash
sudo dnf install python3
```

## Cryptodome
- Ubuntu/Desbian
``` bash
sudo apt install python3-pip -y
pip3 install pycryptodome
```
- CentOS/Red Hat
``` bash
sudo dnf install python3-pip -y
pip3 install pycryptodome
```

# Cách cài đặt file
## Tải file 
```bash
git clone https://github.com/thanh1v/Project_OSG203/
```
## Sửa Shell
```bash
nano ~/.bashrc
# hoặc nano ~/.zshrc nếu bạn dùng Zsh
```
- THÊM lệnh sau vào bashrc/zshrc (KHÔNG PHẢI VIẾT LẠI MÀ LÀ THÊM)
``` bash
# --- Bắt đầu Hook cho secure-dir ---
# Tên thư mục bảo mật
SECURE_DIR_NAME="secure-dir"
# Tên script xác thực (Wrapper Shell)
AUTH_SCRIPT_NAME=".init.sh"

# Lưu lệnh cd gốc
alias real_cd="builtin cd"

# Định nghĩa lại hàm cd
cd() {
    local TARGET_DIR
    TARGET_DIR="$1"

    # Chỉ xử lý nếu mục tiêu là thư mục bảo mật của chúng ta
    if [ "$(basename "$TARGET_DIR")" = "$SECURE_DIR_NAME" ] || [ "$TARGET_DIR" = "$SECURE_DIR_NAME" ]; then

        # Đường dẫn tuyệt đối đến file .init.sh
        # Giả sử thư mục secure-dir nằm ngay trong thư mục hiện tại khi gọi cd
        local SCRIPT_PATH="./$SECURE_DIR_NAME/$AUTH_SCRIPT_NAME"

        # Kiểm tra sự tồn tại của script (.init.sh)
        if [ ! -f "$SCRIPT_PATH" ]; then
            echo "Lỗi: Không tìm thấy $SECURE_DIR_NAME/$AUTH_SCRIPT_NAME."
            real_cd "$@"
            return
        fi

        # Chạy kịch bản xác thực và kiểm tra mã thoát (exit code)
        if bash "$SCRIPT_PATH"; then
            # Đăng nhập thành công, thực hiện lệnh cd gốc
            real_cd "$@"
        else
            # Đăng nhập thất bại
            echo "Truy cập thư mục $SECURE_DIR_NAME bị chặn."
            return 1
        fi
    else
        # Nếu không phải là secure-dir, chạy lệnh cd gốc
        real_cd "$@"
    fi
}
# --- Kết thúc Hook cho secure-dir ---
```
