"""
app.py - File chạy Flask chính, đồng bộ với app_frontend.py
Đề tài: NLCNPM23CS-38
"""

from app_frontend import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
