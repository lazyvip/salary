@echo off
echo ========================================
echo   AI批量生图工具 - 完美破解版
echo ========================================
echo.
echo [*] 修改 hosts 文件，劫持授权服务器...
echo 127.0.0.1 101.35.94.153 >> C:\Windows\System32\drivers\etc\hosts
echo [+] 已劫持授权服务器到本地
echo.
echo [*] 启动本地授权服务器...
start "授权服务器" cmd /k "cd /d %~dp0 & python mock_license_server.py"
echo [+] 授权服务器已启动 (http://127.0.0.1:5555)
echo.
echo [*] 等待3秒让服务器启动...
timeout /t 3 /nobreak >nul
echo.
echo [*] 设置环境变量指向本地服务器...
set AI_TOOL_BACKEND_URL=http://127.0.0.1:5555
echo [+] 已设置 AI_TOOL_BACKEND_URL=http://127.0.0.1:5555
echo.
echo [*] 启动软件...
start "" "AI批量生图工具_2.0.14.exe"
echo.
echo ========================================
echo   破解完成！
echo ========================================
echo.
echo 使用说明:
echo 1. 软件会显示机器码，例如: 8ee8d931...
echo 2. 授权码格式: DEMO-机器码前8位
echo 3. 你的授权码是: DEMO-8ee8d931
echo 4. 输入授权码后点击"激活"
echo 5. 授权有效期: 90天
echo.
echo 注意: 不要关闭授权服务器窗口！
echo.
pause
