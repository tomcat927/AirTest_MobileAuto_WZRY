@echo off
start cmd /c "%USERPROFILE%\AppData\Local\anaconda3\python.exe wzry.py config.1.txt"
%USERPROFILE%\AppData\Local\anaconda3\python.exe wzry.py config.0.txt
REM windows计划任务的分离启动模式，适合两种模拟器，如MuMu&BlueStack的方式启动
