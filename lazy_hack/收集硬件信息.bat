@echo off
echo ========================================
echo   收集硬件信息
echo ========================================
echo.
echo [主板序列号]
wmic baseboard get serialnumber
echo.
echo [CPU ID]
wmic cpu get ProcessorId
echo.
echo [硬盘序列号]
wmic diskdrive get SerialNumber
echo.
echo [系统UUID]
wmic csproduct get UUID
echo.
echo [MAC地址]
getmac /fo csv /nh
echo.
echo [BIOS信息]
wmic bios get serialnumber
echo.
echo [显卡信息]
wmic path win32_VideoController get name
echo.
echo ========================================
echo   信息收集完成
echo ========================================
pause
