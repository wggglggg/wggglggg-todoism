from flask import Flask, render_template
from app.extensions import db
from app.blueprints.home import home_bp
from app.blueprints.auth import auth_bp
from app.blueprints.app import app_bp
from config import config

import os, click


# app工厂
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)

    return app


# 注册 extensions里面的实例化对象
def register_extensions(app):
    db.init_app(app)


# 注册蓝本
def register_blueprints(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(app_bp)


# 注册错误页面
def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return  render_template('errors.html', code=400, info='Bad Request'), 400

    @app.errorhandler(403)
    def bad_request(e):
        return render_template('errors.html', code=403, info='Forbidden'), 403

    @app.errorhandler(404)
    def bad_request(e):
        return render_template('errors.html', code=404, info='Page Not Found'), 404

    @app.errorhandler(500  )
    def bad_request(e):
        return render_template('errors.html', code=500, info='Server Error'), 500


# 注册命令行工具
def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """如果 drop 为 true"""
        if drop:
            db.drop_all()
            click.echo('数据表删除完毕,马上重建')

        db.create_all()
        click.echo('数据库初始化完成.')