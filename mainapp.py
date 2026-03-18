from flask import Flask, request, jsonify, send_from_directory, render_template
import os,string
from sql import *
from flask import session, redirect

app = Flask(__name__,
            template_folder='templates',  # 明确指定模板文件夹
            static_folder='static',        # 明确指定静态文件夹
            static_url_path='/static')
app.config['SECRET_KEY'] = 'hanimi06spar10'
@app.route('/')
def index():
    return render_template('map.html')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        rs=db4(username,password)
        if rs:
            session['username'] = username
            session['password'] = password
            return render_template('map.html')
        else:
            return render_template('login.html',error="wrong")
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
        rs = db6(username, password)
        if rs:
            return jsonify({'success': True, 'message': '注册成功', 'account': username})
        else:
            return jsonify({'success': False, 'message': '用户名已存在，请使用其他用户名'})
    else:
        # GET请求返回页面（兼容直接访问/register的情况）
        return render_template('register.html')
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


