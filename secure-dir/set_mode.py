#!/bin/env python3

import subprocess

def change_mode(role):
    if role == "admin":
        command = "chmod 700 ./secure-dir/*"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Permissions changed to 700 for admin.")
        else:
            print(f"Error changing permissions: {result.stderr}")

    elif role == "user":
        command = "chmod 000 ./secure-dir/*"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Permissions changed to 000 for user.")
        else:
            print(f"Error changing permissions: {result.stderr}")

        command = "chmod 644 ./secure-dir/open-dir/*"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Permissions changed to 644 for files in open-dir.")
        else:
            print(f"Error changing permissions: {result.stderr}")
    
    else:
        print("Invalid role specified. Use 'admin' or 'user'.")
