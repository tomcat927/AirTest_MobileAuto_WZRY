#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import keyboard
import sys

try:
    subprocess.Popen("adb", "kill-server")
except:
    pass
# 获取命令行参数
para = ["python", "-u", "object.py"] + sys.argv[1:]

# 启动一个子进程
process = subprocess.Popen(para)

# 监听 Ctrl+C 组合键
def on_terminate():
    if process.poll() is None:  # 检查子进程是否在运行
        process.terminate()  # 终止子进程
        process.kill()  # 如果终止失败，强制杀死子进程

keyboard.add_hotkey("ctrl+c", on_terminate)

# 等待按下 Ctrl+C 组合键
keyboard.wait()

exit()