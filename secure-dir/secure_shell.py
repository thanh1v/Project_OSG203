#!/usr/bin/env python3
# Restricted shell: có thể bật/tắt hạn chế tùy user
import os, sys, shlex, shutil, subprocess

# --- cấu hình ---
LS = shutil.which("ls") or "/bin/ls"
CAT = shutil.which("cat") or "/bin/cat"
ALLOWED = {"ls": LS, "cat": CAT, "cd": None}

# --- helper ---
def is_flag(tok): return tok.startswith("-")

def handle_ls(args):
    if any(is_flag(t) for t in args):
        print("Flags for ls are not allowed."); return
    cmd = [ALLOWED["ls"]] + args if args else [ALLOWED["ls"]]
    try: subprocess.run(cmd, check=False)
    except Exception as e: print("ls error:", e)

def handle_cat(args):
    if any(is_flag(t) for t in args):
        print("Flags for cat are not allowed."); return
    if not args: print("Usage: cat <file>"); return
    for p in args:
        if os.path.isdir(p): print(f"cat: {p}: Is a directory"); continue
        try:
            with open(p, "rb") as f:
                while chunk := f.read(8192):
                    sys.stdout.buffer.write(chunk)
        except FileNotFoundError: print(f"cat: {p}: No such file")
        except PermissionError: print(f"cat: {p}: Permission denied")
        except Exception as e: print(f"cat error {p}: {e}")

def handle_cd(args):
    target = args[0] if args else os.path.expanduser("~")
    try: os.chdir(target)
    except Exception as e: print(f"cd error: {e}")

# --- restricted shell ---
def restricted_repl():
    while True:
        try:
            cwd = os.getcwd()
            inp = input(f"{cwd}$ ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not inp: continue
        try: parts = shlex.split(inp)
        except ValueError: print("Parse error"); continue
        cmd, args = parts[0], parts[1:]
        if cmd in ("exit","logout","quit"): break
        if cmd not in ALLOWED:
            print(f"Command not allowed: {cmd}"); continue
        if cmd=="ls": handle_ls(args)
        elif cmd=="cat": handle_cat(args)
        elif cmd=="cd": handle_cd(args)

# --- unrestricted shell ---
def full_repl():
    while True:
        try:
            cwd = os.getcwd()
            inp = input(f"{cwd}# ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not inp: continue
        if inp in ("exit","logout","quit"): break
        try:
            subprocess.run(inp, shell=True)
        except Exception as e:
            print("Error:", e)

# --- main ---
def access(role):
    if role == "user":
        print(">> Restricted mode enabled for this user <<")
        restricted_repl()
    else:
        print(">> Full access granted <<")
        full_repl()

    print("Goodbye.")
