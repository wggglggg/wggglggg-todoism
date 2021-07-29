from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Item
from app.extensions import fake, db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('app.app'))

    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and user.validate_password(password):
            login_user(user)
            return jsonify(message='登录成功')
        return jsonify(message='用户名或者密码错误'), 400

    return render_template('_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message='已经退出.')


@auth_bp.route('/register')
def register():
    username = fake.user_name()             # 随机生成一个注册用户名
    while User.query.filter_by(username=username).first() is not None:
        username = fake.user_name()         # 检测注册的用户名 是否在数据中 有同名情况
    password = fake.word()                  # 随机生成密码

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    item = Item(body='下班给人送螺旋杆菌检测纸', author=user)
    item2 = Item(body='取门卫快递', author=user)
    item3 = Item(body='晚上有女排奥运决赛', author=user)
    item4 = Item(body='adfadfasdfasdfasd', author=user, done=True)
    db.session.add_all([item, item2, item3, item4])
    db.session.commit()

    return jsonify(username=username, password=password, message='注册成功')