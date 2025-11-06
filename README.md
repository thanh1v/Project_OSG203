# Project môn học OSG203 
# Title: Secure Linux File System

Mô tả: 
Sử dụng các công cụ AI để xây dựng hệ thống bảo mật file trong Linux.
- Tận dụng AI để sửa lỗi và giải quyết edge cases.
- Mã hóa và bảo về 1 thư mục đặc biệt trong môi trường Linux.
- Cần đăng nhập để truy cập vào file này.
- Mật khẩu lưu trữ được mã hóa AES-128.


# Các tài nguyên cần thiết
- python
- pip
- cryptodome
- llm
## Ubuntu/Desbian
```
sudo apt install python3
sudo apt install python3-pip -y
pip3 install pycryptodome
pip3 install llm
```
## CentOS/Red Hat
```
sudo dnf install python3
sudo dnf install python3-pip -y
pip3 install pycryptodome
pip3 install llm
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
SECURE_DIR_NAME="secure-dir"
AUTH_SCRIPT_NAME=".init.sh"

# Lưu lệnh cd gốc
alias real_cd="builtin cd"

# Định nghĩa lại hàm cd
cd() {
    local TARGET_DIR_INPUT
    # Nếu không có đối số, mặc định là Home (~)
    if [ -z "$1" ]; then
        TARGET_DIR_INPUT="~"
    else
        TARGET_DIR_INPUT="$1"
    fi

    local TARGET_ABS_PATH

    # Xử lý trường hợp đặc biệt 'cd -' (quay lại $OLDPWD)
    if [ "$TARGET_DIR_INPUT" = "-" ]; then
        # Lấy đường dẫn của thư mục trước đó ($OLDPWD)
        # Sử dụng 'pwd -P' để lấy canonical path
        TARGET_ABS_PATH=$(real_cd - >/dev/null 2>&1 && pwd -P)

        # Nếu OLDPWD không hợp lệ hoặc không tồn tại
        if [ -z "$TARGET_ABS_PATH" ]; then
            # Chạy cd gốc để in ra lỗi chuẩn
            real_cd "$@"
            return $?
        fi

    # Xử lý các đường dẫn bình thường (tuyệt đối, tương đối, ~)
    else
        # Chuyển đổi đường dẫn nhập vào thành đường dẫn tuyệt đối/đã xử lý (canonical path)
        # Chạy real_cd trong subshell để không thay đổi PWD hiện tại
        TARGET_ABS_PATH=$( (real_cd -- "$TARGET_DIR_INPUT" >/dev/null 2>&1 && pwd -P) )

        # Nếu đường dẫn không hợp lệ (ví dụ: thư mục không tồn tại)
        if [ -z "$TARGET_ABS_PATH" ]; then
            real_cd "$@" # Chạy cd gốc để in ra thông báo lỗi
            return $?
        fi
    fi

    # --- Bắt đầu Logic Xử lý Bảo mật ---

    # 1. Kiểm tra xem thư mục đích có phải là SECURE_DIR_NAME không
    if [ "$(basename "$TARGET_ABS_PATH")" = "$SECURE_DIR_NAME" ]; then

        local SCRIPT_PATH="$TARGET_ABS_PATH/$AUTH_SCRIPT_NAME"

        # 2. Kiểm tra sự tồn tại của script (.init.sh)
        if [ ! -f "$SCRIPT_PATH" ]; then
            echo "Lỗi: Không tìm thấy $TARGET_ABS_PATH/$AUTH_SCRIPT_NAME. Cho phép truy cập..."
            real_cd "$@" # Vẫn cho phép vào nếu không tìm thấy script
            return $?
        fi

        # 3. Chạy kịch bản xác thực
        echo "Cần xác thực để vào thư mục $SECURE_DIR_NAME..."
        if bash "$SCRIPT_PATH"; then
            # Đăng nhập thành công, thực hiện lệnh cd
            real_cd "$@"
            return $?
        else
            # Đăng nhập thất bại
            echo "Truy cập thư mục $SECURE_DIR_NAME bị chặn."
            return 1 # Trả về mã lỗi 1
        fi
    else
        # Nếu không phải là secure-dir, chạy lệnh cd gốc
        real_cd "$@"
    fi
}
# --- Kết thúc Hook cho secure-dir ---
```
