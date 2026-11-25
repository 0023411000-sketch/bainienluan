@echo off
chcp 65001 >nul
title IT Career Compass - Cloudflare Quick Tunnel
cd /d "%~dp0"

set "CLOUDFLARED_EXE=C:\Program Files (x86)\cloudflared\cloudflared.exe"
if not exist "%CLOUDFLARED_EXE%" (
    where cloudflared >nul 2>&1
    if %errorlevel% equ 0 (
        set "CLOUDFLARED_EXE=cloudflared"
    ) else (
        echo [LOI] Khong tim thay cloudflared! Hay cai bang: winget install Cloudflare.cloudflared
        pause
        exit /b 1
    )
)

echo ======================================================================
echo   IT CAREER COMPASS - CLOUDFLARE QUICK TUNNEL (KHONG CAN TEN MIEN)
echo ======================================================================

netstat -ano | findstr "127.0.0.1:5000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/2] Dang khoi dong may chu Flask tai http://127.0.0.1:5000 ...
    start "IT Career Compass - Flask Backend" /Min /D "%~dp0" .\venv\Scripts\python.exe app.py
    timeout /t 3 /nobreak >nul
) else (
    echo [1/2] May chu Flask da san sang tai http://127.0.0.1:5000.
)

echo [2/2] Dang khoi tao duong ham HTTPS Cloudflare (doi khoang 5-8 giay)...
start "Cloudflared Connector" /Min "%CLOUDFLARED_EXE%" tunnel --url http://127.0.0.1:5000 --metrics 127.0.0.1:20245 --no-autoupdate

powershell -NoProfile -Command ^
  "$url = $null; for ($i=0; $i -lt 25; $i++) { Start-Sleep -Seconds 1; try { $r = Invoke-RestMethod -Uri 'http://127.0.0.1:20245/quicktunnel' -TimeoutSec 2; if ($r.hostname) { $url = 'https://' + $r.hostname; break } } catch {} }; if ($url) { Set-Clipboard -Value $url; Write-Host ''; Write-Host '======================================================================' -ForegroundColor Green; Write-Host ('  LINK TRUY CAP CONG KHAI: ' + $url) -ForegroundColor Cyan; Write-Host '  (Da tu dong copy vao Clipboard va mo trinh duyet!)' -ForegroundColor Yellow; Write-Host '======================================================================' -ForegroundColor Green; Start-Process $url } else { Write-Host '[LOI] Chua lay duoc link trycloudflare, hay kiem tra cua so Cloudflared Connector.' -ForegroundColor Red }"

echo.
echo Duong ham dang hoat dong ngam. Nhan phim bat ky khi ban muon DUNG duong ham...
pause >nul
taskkill /FI "WINDOWTITLE eq Cloudflared Connector*" /F >nul 2>&1
echo Da dung Cloudflare Tunnel.
cloudflared tunnel --url http://127.0.0.1:5000 --no-autoupdate