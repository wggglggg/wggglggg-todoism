from flask import url_for
from app.models import Item


# 待办事项与作者的详细数据
def item_schema(item):
    return {
        'id': item.id,
        'self': url_for('.item', item_id=item.id, _external=True),
        'kind': 'Item',
        'body': item.body,
        'done': item.done,
        'author': {
          'id': 1,
          'url': url_for('.user', _external=True),
          'username': item.author.username,
          'kind': 'User',
        },
    }


# # user与user的待办事项 详细情况
# def user_schema(user):
#     return {
#         'id': user.id,
#         'self': url_for('.user', _external=True),
#         'kind': 'User',
#         'username': user.username,
#         'all_items_url': url_for('.items', _external=True),
#         'active_items_url': url_for('.active_items', _external=True),
#         'completed_items_url': url_for('.completed_items', _external=True),
#         'all_item_count': len(user.items),
#         'active_item_count': Item.query.with_parent(user).filter_by(done=False).count(),
#         'completed_item_count': Item.query.with_parent(user).filter_by(done=True).count(),
#     }

def user_schema(user):
    return {
        'id': user.id,
        'self': url_for('.user', _external=True),
        'kind': 'User',
        'username': user.username,
        'all_items_url': url_for('.items', _external=True),
        'active_items_url': url_for('.active_items', _external=True),
        'completed_items_url': url_for('.completed_items', _external=True),
        'all_item_count': len(user.items),
        'active_item_count': Item.query.with_parent(user).filter_by(done=False).count(),
        'completed_item_count': Item.query.with_parent(user).filter_by(done=True).count(),
    }


# 当前用户的所有Items 详细情况
def items_schema(items, current, prev, next, pagination):
    return {
        'self': current,
        'kind': 'ItemCollection',
        'items': [item_schema(item) for item in items],         # for循环后, 获取单个Item待办, 用item_schema显示数据
        'prev': prev,
        'last': url_for('.items', page=pagination.pages, _external=True), # pagination.pages能拿到最大的一页
        'first': url_for('.items', page=1, _external=True),
        'next': next,
        'count': pagination.total,                                           # pagination.total拿到所有items数量
    }



















