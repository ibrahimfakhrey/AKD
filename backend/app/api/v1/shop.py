"""Shop API — browse items, buy with gems, view inventory."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.shop import ShopItem, Purchase
from app.models.user import User
from app.services.ledger_service import deduct_gems
from app.utils.errors import APIError, NotFoundError

shop_bp = Blueprint('shop', __name__, url_prefix='/api/v1/shop')


@shop_bp.route('/items', methods=['GET'])
@jwt_required()
def list_items():
    items = ShopItem.query.filter_by(active=True).all()
    return jsonify([item.to_dict() for item in items])


@shop_bp.route('/buy/<item_id>', methods=['POST'])
@jwt_required()
def buy_item(item_id):
    user_id = get_jwt_identity()
    item = ShopItem.query.get(item_id)
    if not item or not item.active:
        raise NotFoundError('Shop item not found')

    # Check if already purchased (cosmetics are unique per user)
    existing = Purchase.query.filter_by(user_id=user_id, shop_item_id=item_id).first()
    if existing:
        raise APIError('You already own this item')

    # Deduct gems (raises InsufficientFundsError if not enough)
    deduct_gems(user_id, item.price_gems, 'shop_purchase', related_id=item.id)

    purchase = Purchase(user_id=user_id, shop_item_id=item.id)
    db.session.add(purchase)
    db.session.commit()

    return jsonify({
        'message': f'Purchased {item.name}!',
        'purchase': purchase.to_dict(),
    })


@shop_bp.route('/inventory', methods=['GET'])
@jwt_required()
def inventory():
    user_id = get_jwt_identity()
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    return jsonify([p.to_dict() for p in purchases])


@shop_bp.route('/equip/<item_id>', methods=['POST'])
@jwt_required()
def equip_item(item_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        from app.utils.errors import APIError
        raise APIError('User not found', status_code=404)

    # Verify ownership
    purchase = Purchase.query.filter_by(user_id=user_id, shop_item_id=item_id).first()
    if not purchase:
        from app.utils.errors import APIError
        raise APIError('You do not own this item', status_code=403)

    item = purchase.shop_item
    item_type = item.item_type
    metadata = item.metadata_json or {}

    # Initialize equipped_cosmetics if None
    equipped = user.equipped_cosmetics or {}

    if item_type == 'profile_picture':
        # Apply the image URL to the user's avatar
        user.avatar_url = item.image_url
    elif item_type == 'name_color':
        # Apply the color to the user's cosmetics dict
        equipped['name_color'] = metadata.get('color', '#FFFFFF')
        user.equipped_cosmetics = equipped
    else:
        # Generic cosmetic equip
        equipped[item_type] = item.id
        user.equipped_cosmetics = equipped

    # Tell SQLAlchemy the JSON field was mutated if we modified `equipped` inplace
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(user, 'equipped_cosmetics')

    db.session.commit()

    return jsonify({
        'message': f'Equipped {item.name}',
        'user': user.to_dict(include_private=True)
    })

