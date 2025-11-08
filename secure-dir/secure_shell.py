#!/usr/bin/env python3
# Restricted shell + command log
import os, sys, shlex, shutil, subprocess, datetime

# ---------- Cấu hình ----------
LS = shutil.which("ls") or "/bin/ls"
CAT = shutil.which("cat") or "/bin/cat"
ALLOWED = {"ls": LS, "cat": CAT, "cd": None}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SECURE_DIR = os.path.abspath(os.environ.get("SECURE_DIR", SCRIPT_DIR))
os.makedirs(SECURE_DIR, exist_ok=True)

# ---------- Helper ----------
def is_flag(tok: str) -> bool:
    return tok.startswith("-")

def _in_secure(real_path: str) -> bool:
    base = os.path.realpath(SECURE_DIR)
    rp = os.path.realpath(real_path)
    return rp == base or rp.startswith(base + os.sep)

def _resolve_in_secure(p: str) -> str:
    if p.startswith("~"):
        p = os.path.join(SECURE_DIR, p.lstrip("~/"))
    if not os.path.isabs(p):
        p = os.path.join(os.getcwd(), p)
    rp = os.path.realpath(p)
    if not _in_secure(rp):
        raise PermissionError(f"path escapes secure-dir: {rp}")
    return rp

def enter_secure_dir() -> None:
    os.environ["HOME"] = SECURE_DIR
    os.chdir(SECURE_DIR)

def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except UnicodeDecodeError:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        data = sys.stdin.buffer.readline()
        if not data:
            raise EOFError
        return data.decode("utf-8", errors="ignore").rstrip("\r\n")

def log_cmd(username: str | None, cmd: str) -> None:
    user = username or "unknown"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("command_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{now} {user} -- {cmd}\n")
    except Exception:
        pass

# ---------- Handlers ----------
def handle_ls(args):
    if any(is_flag(t) for t in args):
        print("Flags for ls are not allowed.")
        return
    try:
        resolved = [_resolve_in_secure(a) for a in args] if args else []
        cmd = [ALLOWED["ls"], *resolved]
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
                while chunk := f.read(8192):
                    sys.stdout.buffer.write(chunk)
        except FileNotFoundError:
            print(f"cat: {p}: No such file")
        except PermissionError as e:
            print(f"cat denied {p}: {e}")
        except Exception as e:
            print(f"cat error {p}: {e}")

def handle_cd(args):
    target = args[0] if args else SECURE_DIR
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

        if inp in ("exit", "quit", "logout"):
            print("Goodbye. Back to:", os.getcwd())
            break

        try:
            parts = shlex.split(inp)
        except ValueError:
            print("Parse error")
            continue

        cmd, args = parts[0], parts[1:]
        if cmd not in ALLOWED:
            print(f"Command not allowed: {cmd}")
            continue

        if cmd == "ls":
            handle_ls(args)
        elif cmd == "cat":
            handle_cat(args)
        elif cmd == "cd":
            handle_cd(args)

# ---------- API ----------
def access(role, username: str | None = None):
    enter_secure_dir()
    if role == "user":
        print(f">> Restricted mode enabled in {SECURE_DIR} <<")
        restricted_repl(username)
    
