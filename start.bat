@echo off
chcp 65001 >nul
title IT Career Compass - Flask Server
echo ======================================================================
echo   HE THONG DINH HUONG KY NANG NGHE NGHIEP CNTT (FLASK + SQLITE)
echo   De tai: NLCNPM23CS-38
echo   May chu dang chay tai: http://127.0.0.1:5000
echo ======================================================================
echo   DANH SACH TAI KHOAN DUNG THU (Mat khau chung: 123456):
echo   - [Quan tri vien] Admin 1          : admin@hust.edu.vn
echo   - [Quan tri vien] Admin 2          : long.admin@hust.edu.vn
echo   - [SV Backend]    Nguyen Van An    : an.nguyen20@sis.hust.edu.vn
echo   - [SV Frontend]   Tran Thi Bich Ngoc: ngoc.tran21@student.edu.vn
echo   - [SV Data]       Le Hoang Nam     : nam.le21@student.edu.vn
echo   - [SV AI / ML]    Pham Minh Tuan   : tuan.pham22@student.edu.vn
echo ======================================================================
set FLASK_DEBUG=1
set FLASK_HOST=127.0.0.1
.\venv\Scripts\python.exe app.py
pause
