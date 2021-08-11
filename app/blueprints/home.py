from flask import Blueprint, render_template, current_app, jsonify, make_response, abort, redirect, url_for, request
from flask_babel import _
from flask_login import current_user
from app.extensions import db, babel

import pytz

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    return render_template('index.html')


@home_bp.route('/intro')
def intro():
    return render_template('_intro.html')


@home_bp.route('/set_locale/<locale>')
def set_locale(locale):
    if locale not in current_app.config['TODOISM_LOCALES']:
        return jsonify(message=_('Invalid locale')), 404

    response = make_response(jsonify(message=_('Setting updated')))
    if current_user.is_authenticated:
        current_user.locale = locale
        db.session.commit()

    else:
        response.set_cookie('locale', locale, max_age=60 * 60 * 24 * 30)  # 服务器把cookie放到客户端请求中有效一个月
    return response


@home_bp.route('/set_timezone/<path:timezone>')
def set_timezone(timezone):
    if timezone not in pytz.all_timezones:
        abort(404)

    if current_user.is_authenticated:
        current_user.timezone = timezone
        db.session.commit()
        return render_template('_app.html')
    else:                       # 如果未登录 就把当前 的timezone直接加到cookie中
        # response = make_response(redirect(url_for('home.intro')))
        response = make_response(jsonify(message=_('Setting updated')))
        response.set_cookie('timezone', timezone, max_age=60 * 60 * 24 * 30)
        return response




# @home_bp.route('/get_timezone')
