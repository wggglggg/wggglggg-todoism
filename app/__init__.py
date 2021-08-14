import os
import click
import pytz

from app.extensions import db, login_manager, csrf, babel
from flask import Flask, render_template, request, jsonify
from flask_babel import _
from config import config
from app.blueprints.home import home_bp
from app.blueprints.auth import auth_bp
from app.blueprints.app import app_bp
from app.apis.v1 import api_v1


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_template_context(app)
    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    csrf.exempt(api_v1)     # api不需要CSRF保护, 不便于前后商数据交换,exempt()去除保护
    babel.init_app(app)


def register_blueprints(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(app_bp)
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    # 相当于 127.0.0.1：5000／api/v1/xxxxx
    # app.register_blueprint(api_v1, url_prefix='/v1', subdomain='api')
    # 相当于 api.example.com


def register_template_context(app):
    @app.context_processor
    def inject_info():
        timezones = pytz.all_timezones
        return dict(timezones=timezones)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request():
        return render_template('errors.html', code=400, info=_('Bad Request')), 400

    @app.errorhandler(403)
    def forbidden():
        return render_template('errors.html', code=403, info=_('Forbidden')), 403

    @app.errorhandler(404)
    def page_not_found():           # 如果请求头里Content-Type期待返回的是什么内容类型
        if request.accept_mimetypes.accept_json and \
                not request.accept_mimetypes.accept_html \
                or request.path.startswith('api'):
            response = jsonify(code=404, message='The requested URL was not found on the server')
            response.status_code = 404
            return response

        return render_template('errors.html', code=404, info=_('Page Not Found')), 404

    @app.errorhandler(405)
    def method_not_allowed():
        response = jsonify(code=405, message='The method is not allowed for the requested URL.')
        response.status_code = 405
        return response

    @app.errorhandler(500)
    def internal_server_error():
        if request.accept_mimetypes.accept_json and \
                not request.accept_mimetypes.accept_html or \
                request.host.startswith('api'):
            response = jsonify(code=500, message='An internal server error occurred')
            response.status_code = 500
            return response

        return render_template('errors.html', code=500, info=_('Server Error')), 500


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

    @app.cli.group()
    def translate():
        """翻译 或者 本地化, 此函数只是创建一个组, 方便管理"""
        pass

    @translate.command()
    @click.argument('locale')
    def init(locale):
        """初始化一个语言模板 messages.pot 文件, locale为en 或者 zh_Hans_CN"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel init -i messages.pot -d app/translations -l' + locale):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')          #"""因为.pot文件只是临时文件, 可以删除"""

    @translate.command()
    def update():
        """更新翻译messages.po文件, 如果修改过html py里面的原文(英文), 也会更新messages.pot"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('updte command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """"生成 MO文件, flask-babel是从些文件读取各区域的语言"""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')