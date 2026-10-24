"""
app.py - File chạy Flask phục vụ việc render giao diện Jinja2 và chạy thử nghiệm.
"""
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = 'it-career-compass-secret-key'

@app.route('/')
def index():
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/comparison')
def comparison():
    return render_template('comparison.html')

@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/register')
def register():
    return render_template('auth/register.html')

if __name__ == '__main__':
    # Chạy ở cổng 5000 ở chế độ Debug
    app.run(debug=True, port=5000)
