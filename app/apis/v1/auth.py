from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from flask import current_app, request, g
from app.models import User
from functools import wraps
from app.apis.v1.errors import api_abort, invalid_token, token_missing


# 生成令牌函数
def generate_token(user):
    expiration = 3600                   # token 存活期(有效期)设为 60秒 * 60分 = 1小时
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)  # 以安全码key秘有效期生成一串字母数字组合
    token = s.dumps({'id': user.id}).decode('ascii')            # 加入user_id, 生成token的序列化码以 ascii解码
    return token, expiration


# 获取令牌token
def get_token():
    if 'Authorization' in request.headers:
        try:                                                                # 去除None
            token_type, token = request.headers['Authorization'].split(None, 1)
            print('request.headers["Authorization"].split(None, 1)', request.headers['Authorization'].split(None, 5))
        except ValueError:
            token_type = token = None

    else:
        token_type = token = None

    return token_type, token


# 验证令牌
def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):        # 如果token验证失败, 错误的签名令牌, 或者过期的令牌, 会被捕获
        return False

    user = User.query.get(data['id'])               # token里面会有dumps加入的user.id
    if user is None:
        return False

    g.current_user = user                           # 将用户对象存到 g 上下文中
    return True


# 登录保护装饰器
def auth_required(f):
    @wraps(f)                           # 加入wraps , 被 auth_required装饰过的函数, 还是普通函数, 不使用, 就会变马装饰器函数
    def decorated(*args, **kwargs):
        token_type, token = get_token()

        if token_type is None or token_type.lower() != 'bearer':     # 如果token_type不是bearer
            return api_abort(400, 'The token type must be bearer.')
        if token is None:                                               # 如果token是none, 返回token_missing的值
            return token_missing()
        if not validate_token(token):                                   # 如果token检验后无效, 返回invali_token的值
            return invalid_token()

        return f(*args, **kwargs)

    return decorated
