@echo off
start cmd /c "%USERPROFILE%\AppData\Local\anaconda3\python.exe wzry.py config.1.txt"
%USERPROFILE%\AppData\Local\anaconda3\python.exe wzry.py config.0.txt
:: 不用windows计划任务，是因为windows的计划任务，无法启动模拟器
