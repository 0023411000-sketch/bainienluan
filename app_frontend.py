"""
app_frontend.py - File chạy Flask phục vụ render giao diện Jinja2 độc lập cho Frontend
Đề tài: NLCNPM23CS-38 - Ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT
"""

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = 'it-career-compass-frontend-secret-key'

# 1. Trang chủ điều hướng về Dashboard tổng quan
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

# 2. Xác thực tài khoản
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

# 3. Dashboard tổng quan
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 4. Hồ sơ sinh viên (4 phần quản lý)
@app.route('/profile')
def profile():
    return render_template('profile.html')

# 5. Danh mục vị trí nghề nghiệp
@app.route('/positions')
def positions():
    return render_template('positions.html')

# 6. Quản lý tin tuyển dụng & nhập file CSV
@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

# 7. Thống kê kỹ năng theo vị trí tuyển dụng
@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

# 8. Đánh giá và so sánh mức độ phù hợp hồ sơ
@app.route('/compare')
@app.route('/comparison')
def compare():
    return render_template('compare.html')

# 9. Kế hoạch và lộ trình phát triển kỹ năng
@app.route('/plan')
@app.route('/roadmap')
def plan():
    return render_template('plan.html')

# Xử lý lỗi 404 không tìm thấy trang
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    print("=" * 65)
    print("  UNG DUNG DINH HUONG KY NANG NGHE NGHIEP CNTT (FRONTEND FLASK)")
    print("  De tai: NLCNPM23CS-38")
    print("  Dang chay tai: http://127.0.0.1:5000")
    print("  Mac dinh: Su dung Mock Data (doi USE_MOCK trong static/js/config.js)")
    print("=" * 65)
    app.run(debug=True, host='0.0.0.0', port=5000)
