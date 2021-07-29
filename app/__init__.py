import os
import click

from app.extensions import db, login_manager, csrf
from flask import Flask, render_template
from config import config
from app.blueprints.home import home_bp
from app.blueprints.auth import auth_bp
from app.blueprints.app import app_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)



def register_blueprints(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(app_bp)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request():
        return render_template('errors.html', code=400, info='Bad Request'), 400

    @app.errorhandler(403)
    def bad_request():
        return render_template('errors.html', code=403, info='Forbidden'), 403

    @app.errorhandler(404)
    def bad_request():
        return render_template('errors.html', code=404, info='Bad Request'), 404

    @app.errorhandler(500)
    def bad_request():
        return render_template('errors.html', code=500, info='Bad Request'), 500


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='先删除旧表, 再创建新表')
    def initdb(drop):
        if drop:
            click.confirm('此操作将删除旧表, 你想继续吗?', abort=True)
            db.drop_all()
            click.echo('数据库表已经被 删除')

        db.create_all()
        click.echo('表初始化完成')
