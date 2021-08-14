from werkzeug.http import HTTP_STATUS_CODES
from flask import jsonify
from app.apis.v1 import api_v1


# 获取错误code, 将code赋值给status_code
def api_abort(code, message=None, **kwargs):
    if message is None:
        message = HTTP_STATUS_CODES.get(code, '')                 # HTTP_STATUS_CODES是code错误的 原文, 使用原文当错误

    response = jsonify(code=code, message=message, **kwargs)
    response.status_code = code
    return response


# 校验错误 继承value error
class ValidationError(ValueError):
    pass


# 当get_item_body()函数 里的body是None或者为 空, 就会抛出ValidationError错误, errorhandelr就会捕捉到, 返回400
@api_v1.errorhandler(ValidationError)
def validation_error(e):
    return api_abort(400, e.args[0])


# token缺失
def token_missing():
    response = api_abort(401)
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


# 无效的token
def invalid_token():
    response = api_abort(401, error='invalid_token', error_description='Either the token was expired or invalid')
    response.headers['WWW-Authenticate'] = 'bearer'
    return response