@echo off

REM 后台启动 NVIDIA 代理（无窗口）
start "" /B python D:\myAPP\Claude_Config\nvidia-api-proxy\nvidia_proxy.pyw

REM 启动 CC-Switch（路径按你的实际情况修改）
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\CC Switch\cc-switch.exe"
