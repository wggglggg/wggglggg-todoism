from flask.views import MethodView
from app.apis.v1 import api_v1
from app.models import Item, User
from flask import jsonify, g, request, current_app, url_for
from app.apis.v1.errors import api_abort, ValidationError
from app.apis.v1.schemas import item_schema, user_schema, items_schema
from app.extensions import db

from app.apis.v1.auth import generate_token, auth_required


# 获取 item 的 主体body
def get_item_body():
    data = request.get_json()
    body = data.get('body')
    if body is None or str(body).strip() == '':
        """如果body是none或者去除空格后, 拿到的是空的"""
        return ValidationError('The item body was empty or invalid.')
    return body


# item资源类
class ItemAPI(MethodView):
    decorators = [auth_required]

    def get(self, item_id):
        """获取 item"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        return jsonify(item_schema(item))

    def put(self, item_id):
        """编辑 item"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.body = get_item_body()
        db.session.commit()
        return '', 204

    def patch(self, item_id):
        """切换 item 状态"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.done = not item.done
        db.session.commit()
        return '', 204

    def delete(self, item_id):
        """删除 Item"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        db.session.delete(item)
        db.session.commit()
        return '', 204


# index资源类
class IndexAPI(MethodView):

    def get(self):
        return jsonify({
            'api_version': '1.0',
            'api_base_url': 'http://example.com/api/v1',
            'current_user_url': 'http://example.com/api/v1/user',
            'authentication_url': 'http://example.com/api/v1/token',
            'item_url': 'http://example.com/api/v1/items/{item_id}',
            'current_user_items_url': 'http://example.com/api/v1/user/items{?page,per_page}',
            'current_user_active_items_url': 'http://example.com/api/v1/user/items/active{?page,per_page}',
            'current_user_completed_items_url': 'http://example.com/api/v1/user/items/completed{?page,per_page}',
        })


# 用户资源类
class UserAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        return jsonify(user_schema(g.current_user))


# 当前用户待办items资源类
class ItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """获取当前用户所有的Items"""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).paginate(page, per_page=per_page)

        items = pagination.items

        current = url_for('.items', page=page, _external=True)      # 获取当前页码
        prev = None                                                  # 前一页设为none
        if pagination.has_prev:                                     # 如果 前面还有一页
            prev = url_for('.items', page=page - 1, _external=True)

        next = None                                             # 后一页设置为none
        if pagination.has_next:
            next = url_for('.items', page=page + 1, _external=True)  # 如果 后面还有一页, 页码 + 1

        return jsonify(items_schema(items, current, prev, next, pagination))

    def post(self):
        """创建新item"""
        item = Item(body=get_item_body(), author=g.current_user)
        db.session.add(item)
        db.session.commit()

        response = jsonify(item_schema(item))
        response.status_code = 201
        response.headers['Location'] = url_for('.item', item_id=item.id, _external=True)
        return response


# 未完成待办事项Items资源类
class ActiveItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """获取当前用户 所有未完成事项"""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=False).paginate(page, per_page=per_page)
        items = pagination.items

        current = url_for('.items', page=page, _external=True)

        prev = None
        if pagination.has_prev:                         # 如果这个对象的has_prev属性有值,
            prev = url_for('.items', page=page - 1, _external=True)

        next = None
        if pagination.has_next:
            next = url_for('.items', page=page + 1, _external=True)

        return jsonify(items_schema(items, current, prev, next, pagination))


# 已完成待办事项items资源类
class CompletedItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """获取已完成的所有事项"""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=True).paginate(page, per_page=per_page)
        items = pagination.items

        current = url_for('.items', page=page, _external=True)

        prev = None
        if pagination.has_prev:
            prev = url_for('.items', page = page - 1, _external=True)

        next = None
        if pagination.has_next:
            next = url_for('items', page=page + 1, _external=True)

        return jsonify(items_schema(items, current, prev, next, pagination))

    def delete(self):
        """清除已完成的"""
        Item.query.with_parent(g.current_user).filter_by(done=True).delete()
        db.session.commit()
        return '', 204


class AuthTokenAPI(MethodView):

    def post(self):
        grant_type = request.form.get('grant_type')     # 获取访问者form属性 是否为 password type  密码类型
        username = request.form.get('username')         # 获取 用户名值
        password = request.form.get('password')         # 获取 密码值

        if grant_type is None or grant_type.lower() != 'password':  # form中grant_type是空或者不是 Password类型
            return api_abort(code=400, message='认证类型必须为 password类型')       # 返回400 响应值 , 和消息

        user = User.query.filter_by(username=username).first()      # 如果用户名密码合法后, 再去数据库查些用户名
        if user is None or not user.validate_password(password):
            return api_abort(code=400, message='用户名或者密码错误')

        token, expiration = generate_token(user)                    # 拿到序列化后的token令牌 和 expiration 有效期

        response = jsonify({
            'access_token': token,                                  # 将token, token类型, 有效期 制作成json
            'token_type': 'Bearer',
            'expires_in': expiration,
        })
        response.headers['Cache-Control'] = 'no-store'              # 给响应头Cache-Control 设置为 no-store不存储
        response.headers['Pragma'] = 'no-cache'                     # 给响应头Pragma 设置为 no-cache无缓存
        return response                                             # 给客户商返回 响应数据 包含token expiration等


# 为上面的资源 注册路由
api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/user/items/<int:item_id>', view_func=ItemAPI.as_view('item'), methods=['GET', 'PUT', 'PATCH''DELETE'])
# api_v1.add_url_rule('/user', view_func=UserAPI.as_view('user'), methods=['GET'])
api_v1.add_url_rule('/user', view_func=UserAPI.as_view('user'), methods=['GET'])
api_v1.add_url_rule('/user/items', view_func=ItemsAPI.as_view('items'), methods=['GET', 'POST'])
api_v1.add_url_rule('/user/items/active', view_func=ActiveItemsAPI.as_view('active_items'), methods=['GET'])
api_v1.add_url_rule('/user/items/completed', view_func=CompletedItemsAPI.as_view('completed_items'), methods=['GET','DELETE'])
api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])
