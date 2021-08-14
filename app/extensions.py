from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from faker import Faker
from flask_babel import Babel
from flask_login import current_user
from flask import request, current_app


db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
fake = Faker()
babel = Babel()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))  # 如果能查到返回true, 反之false


# 获取用户的Locale区域语言
@babel.localeselector
def get_locale():
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale          # 如果用户已登录并且用户的区域不是None, 就返回用户的区域值

    locale = request.cookies.get('locale')
    if locale is not None:                  # 否则就从网址携带的cookie中获取locale区域值
        return locale
    '''
    cookie里面也没有locale值, 就直接从用户请求头部包含的 (Accept-Language: zh-CN,zh;q=0.9)与config里面的TODOISM_LOCALES匹配最    接近的一个语言偏好
    '''
    return request.accept_languages.best_match(current_app.config['TODOISM_LOCALES'])



@babel.timezoneselector
def get_timezone():
    if current_user.is_authenticated and current_user.timezone is not None:
        return current_user.timezone

    timezone = request.cookies.get('timezone')
    if timezone is not None:
        return timezone

    return None
