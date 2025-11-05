#!/usr/bin/env python3
# Restricted shell: bật/tắt hạn chế tùy vai trò (được gọi từ main.py)
import os, sys, shlex, shutil, subprocess

# ---------- Cấu hình ----------
LS = shutil.which("ls") or "/bin/ls"
CAT = shutil.which("cat") or "/bin/cat"
ALLOWED = {"ls": LS, "cat": CAT, "cd": None}

# Thư mục làm việc an toàn (mặc định: chính thư mục chứa script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SECURE_DIR = os.path.abspath(os.environ.get("SECURE_DIR", SCRIPT_DIR))
os.makedirs(SECURE_DIR, exist_ok=True)  # đảm bảo tồn tại

# ---------- Helper chung ----------
def is_flag(tok: str) -> bool:
    return tok.startswith("-")

def _in_secure(real_path: str) -> bool:
    base = os.path.realpath(SECURE_DIR)
    rp = os.path.realpath(real_path)
    return rp == base or rp.startswith(base + os.sep)

def _resolve_in_secure(p: str) -> str:
    # Map ~ về SECURE_DIR
    if p.startswith("~"):
        p = os.path.join(SECURE_DIR, p.lstrip("~/"))
    # Chuẩn hoá về tuyệt đối theo cwd hiện tại
    if not os.path.isabs(p):
        p = os.path.join(os.getcwd(), p)
    rp = os.path.realpath(p)  # resolve symlink/../.
    if not _in_secure(rp):
        raise PermissionError(f"path escapes secure-dir: {rp}")
    return rp

def enter_secure_dir() -> None:
    """Bắt đầu phiên trong SECURE_DIR."""
    os.environ["HOME"] = SECURE_DIR
    try:
        os.chdir(SECURE_DIR)
    except Exception as e:
        print(f"Cannot chdir to secure dir {SECURE_DIR}: {e}")
        sys.exit(1)

def safe_input(prompt: str) -> str:
    """Đọc input an toàn, tránh UnicodeDecodeError."""
    try:
        return input(prompt)
    except UnicodeDecodeError:
        pass
    sys.stdout.write(prompt)
    sys.stdout.flush()
    data = sys.stdin.buffer.readline()
    if not data:
        raise EOFError
    return data.decode("utf-8", errors="ignore").rstrip("\r\n")

def log_cmd(username: str | None, cmd: str) -> None:
    user = (username or os.environ.get("LOGNAME") or "anonymous")
    try:
        with open("command_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{user} -- {cmd}\n")
    except Exception:
        pass

# ---------- Handlers (restricted) ----------
def handle_ls(args):
    if any(is_flag(t) for t in args):
        print("Flags for ls are not allowed.")
        return
    try:
        if args:
            resolved = [_resolve_in_secure(a) for a in args]
            cmd = [ALLOWED["ls"], *resolved]
        else:
            cmd = [ALLOWED["ls"]]
        subprocess.run(cmd, check=False)
    except PermissionError as e:
        print("ls denied:", e)
    except Exception as e:
        print("ls error:", e)

def handle_cat(args):
    if any(is_flag(t) for t in args):
        print("Flags for cat are not allowed.")
        return
    if not args:
        print("Usage: cat <file>")
        return
    for p in args:
        try:
            rp = _resolve_in_secure(p)
            if os.path.isdir(rp):
                print(f"cat: {p}: Is a directory")
                continue
            with open(rp, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    sys.stdout.buffer.write(chunk)
        except FileNotFoundError:
            print(f"cat: {p}: No such file")
        except PermissionError as e:
            print(f"cat denied {p}: {e}")
        except Exception as e:
            print(f"cat error {p}: {e}")

def handle_cd(args):
    target = args[0] if args else SECURE_DIR  # mặc định về secure-dir
    try:
        rp = _resolve_in_secure(target)
        os.chdir(rp)
    except PermissionError as e:
        print(f"cd denied: {e}")
    except Exception as e:
        print(f"cd error: {e}")

# ---------- REPL ----------
def restricted_repl(username=None):
    while True:
        try:
            cwd = os.getcwd()
            inp = safe_input(f"{cwd}$ ").strip()
            log_cmd(username, inp)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not inp:
            continue
        try:
            parts = shlex.split(inp)
        except ValueError:
            print("Parse error")
            continue

        cmd, args = parts[0], parts[1:]
        if cmd in ("exit", "logout", "quit"):
            break
        if cmd not in ALLOWED:
            print(f"Command not allowed: {cmd}")
            continue

        if cmd == "ls":
            handle_ls(args)
        elif cmd == "cat":
            handle_cat(args)
        elif cmd == "cd":
            handle_cd(args)

def full_repl(username=None):
    while True:
        try:
            cwd = os.getcwd()
            inp = safe_input(f"{cwd}# ").strip()
            log_cmd(username, inp)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not inp:
            continue
        if inp in ("exit", "logout", "quit"):
            break

        # Hỗ trợ cd thật sự
        try:
            parts = shlex.split(inp)
        except ValueError:
            print("Parse error")
            continue
        if parts and parts[0] == "cd":
            target = parts[1] if len(parts) > 1 else os.path.expanduser("~")
            try:
                os.chdir(os.path.expanduser(target))
            except Exception as e:
                print(f"cd error: {e}")
            continue

        try:
            subprocess.run(inp, shell=True)
        except Exception as e:
            print("Error:", e)

# ---------- API chính để main.py gọi ----------
def access(role: str, username: str | None = None):
    """
    Khởi chạy shell theo role. Khi exit, tiến trình rời khỏi secure-dir.
    Gọi từ main.py: secure_shell.access(role, username)
    """
    prev_dir = os.getcwd()
    enter_secure_dir()
    try:
        if role == "user":
            print(f">> Restricted mode enabled in {SECURE_DIR} <<")
            restricted_repl(username)
        else:
            print(f">> Full access granted <<")
            full_repl(username)
    finally:
        # rời khỏi secure-dir trước khi kết thúc tiến trình
        try:
            prev_rp   = os.path.realpath(prev_dir)
            secure_rp = os.path.realpath(SECURE_DIR)
            if prev_rp == secure_rp or prev_rp.startswith(secure_rp + os.sep):
                target = os.path.dirname(secure_rp)  # nhảy ra thư mục cha của secure-dir
            else:
                target = prev_dir
            os.chdir(target)
        except Exception:
            pass
        print("Goodbye. Back to:", os.getcwd())
