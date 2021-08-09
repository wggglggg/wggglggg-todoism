from flask import Blueprint, render_template, request, jsonify
from app.models import Item
from flask_login import current_user, login_required
from app.extensions import db
from flask_babel import _

app_bp = Blueprint('app', __name__)


@app_bp.route('/app')
@login_required
def app():
    all_count = Item.query.with_parent(current_user).count()
    active_count = Item.query.with_parent(current_user).filter_by(done=False).count()
    completed_count = Item.query.with_parent(current_user).filter_by(done=True).count()
    items = current_user.items
    return render_template('_app.html', items=items, all_count=all_count, active_count=active_count,
                           completed_count=completed_count)


# 新添加待办事项
@app_bp.route('/new_item', methods=['POST'])
@login_required
def new_item():
    data = request.get_json()
    if data is None and data['body'].strip() == '':
        return jsonify(message=_('Invalid item body.')), 400
    item = Item(body=data['body'], author=current_user._get_current_object())
    db.session.add(item)
    db.session.commit()
    return jsonify(html=render_template('_item.html', item=item), message='+1')


# 编辑某条待办事项
@app_bp.route('/edit_item/<int:item_id>', methods=['PUT'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('Permission denied.')), 403

    data = request.get_json()

    if data is None or data['body'].strip() == '':
        return jsonify(message=_('Invalid item body.')), 400

    item.body = data['body']
    db.session.commit()
    return jsonify(message=_('Item updated.'))


# 删除某条待办事项
@app_bp.route('/delete_item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('Permission denied.')), 403

    db.session.delete(item)
    db.session.commit()
    return jsonify(message=_('Item deleted.'))


# 切换待办事项状态(已完成, 未完成)
@app_bp.route('/toggle_item/<int:item_id>', methods=['PATCH'])
@login_required
def toggle_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('Permission denied.')), 403

    item.done = not item.done

    db.session.commit()
    return jsonify(message=_('Item toggled.'))


# 一皱清除已完成事项
@app_bp.route('/clear_items', methods=['DELETE'])
@login_required
def clear_items():
    items = Item.query.with_parent(current_user).filter_by(done=True).all()  # 获取当前用户已完成的事项
    for item in items:
        db.session.delete(item)

    db.session.commit()
    return jsonify(message=_('All clear!'))

