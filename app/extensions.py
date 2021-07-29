from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from faker import Faker


db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
fake = Faker()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))   # 如果能查到返回true, 反之false