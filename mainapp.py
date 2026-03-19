from flask import Flask, request, jsonify, send_from_directory, render_template
import os,string
from sql import *
from flask import session, redirect
from datetime import timedelta

app = Flask(__name__,
            template_folder='templates',  # 明确指定模板文件夹
            static_folder='static',        # 明确指定静态文件夹
            static_url_path='/static')
app.config['SECRET_KEY'] = 'hanimi06spar10'
app.config['SESSION_PERMANENT'] = False

# # 1. 设置安全的SECRET_KEY（必须，建议从环境变量读取）
# app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'your_secure_random_key_123456'  # 替换为随机字符串
# # 2. 设置Session过期时间（例如30分钟，无操作则过期）
# app.permanent_session_lifetime = timedelta(minutes=30)
# # 3. 禁用Session持久化（关闭浏览器则失效）
# app.config['SESSION_PERMANENT'] = False
# # 4. 可选：强制Session随浏览器关闭失效
# app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False，生产环境HTTPS下设为True
# app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止JS读取Cookie，提升安全
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
@app.route('/')
def index():
    return render_template('map.html')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if verify_user(username, password):
            # 保留角色查询逻辑
            with get_db_connection() as (conn, cur):
                cur.execute("SELECT role FROM users WHERE account=?", (username,))
                user = cur.fetchone()

            session['username'] = username
            session['role'] = user['role']  # 保留权限存储
            # 关键：改回直接渲染map.html（和旧代码一致）
            return render_template('map.html')
        else:
             # 改回返回登录页+错误提示（和旧代码一致）
             return render_template('login.html', error="账号或密码错误")
    else:
        return render_template('login.html')
@app.route('/register.html')
def register_html():
    return render_template('register.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # 1. 空值校验
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'})
        if not password:
            return jsonify({'success': False, 'message': '密码不能为空'})

        # 2. 密码长度校验
        if len(password) < 8:
            return jsonify({'success': False, 'message': '密码长度不能小于8位'})

        # 3. 密码复杂度校验
        if not any(c.isupper() for c in password):
            return jsonify({'success': False, 'message': '密码必须包含大写字母'})
        if not any(c.islower() for c in password):
            return jsonify({'success': False, 'message': '密码必须包含小写字母'})
        if not any(c.isdigit() for c in password):
            return jsonify({'success': False, 'message': '密码必须包含数字'})
        if not any(c in string.punctuation for c in password):
            return jsonify({'success': False, 'message': '密码必须包含特殊字符'})

        # 4. 两次密码校验
        if password != confirm_password:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'})

        # 5. 调用注册函数
        rs = register_user(username, password)
        if rs:
            return jsonify({'success': True, 'message': '注册成功', 'account': username})
        else:
            return jsonify({'success': False, 'message': '用户名已存在，请使用其他用户名'})
    else:
        # GET请求返回页面（兼容直接访问/register的情况）
        return render_template('register.html')

# @app.route('/admin')
# def admin_page():
#     # 未登录
#     if 'username' not in session:
#         return redirect('/login')
#
#     # 不是管理员
#     if session.get('role') != 'admin':
#         return "权限不足，无法访问后台"
#
#     # 是管理员 → 正常显示
#     return render_template('admin.html')
@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/route')
def route():
    return render_template('route.html')

@app.route('/favorites')
def favorites():
    return render_template('favorites.html')

@app.route('/posts')
def posts():
    return render_template('posts.html')

@app.route('/notices')
def notices():
    return render_template('notices.html')
@app.route('/publish-notices')
def publishnotices():
    return render_template('publish-notices.html')
@app.route('/profile')
def profile():
    username = session.get('username')
    # 如果没登录，自动跳转到登录页
    if 'username' not in session:
        return redirect('/login')  # 自动跳转

    # 已登录就正常显示页面
    return render_template('profile.html', username=session['username'])
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # 清空当前用户的所有登录信息
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


