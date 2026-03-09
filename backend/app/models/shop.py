"""Shop, Purchase, and Transaction (ledger) models."""
import uuid
from datetime import datetime, timezone

from app.extensions import db


class ShopItem(db.Model):
    __tablename__ = 'shop_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    item_type = db.Column(db.String(50), default='cosmetic', nullable=False)
    # item_type: cosmetic | avatar_frame | badge | theme
    price_gems = db.Column(db.Integer, nullable=False)
    metadata_json = db.Column(db.JSON, nullable=True)  # e.g. {"color": "#FF5733", "rarity": "rare"}
    image_url = db.Column(db.String(500), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    purchases = db.relationship('Purchase', backref='shop_item', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type,
            'price_gems': self.price_gems,
            'metadata': self.metadata_json,
            'image_url': self.image_url,
            'active': self.active,
        }


class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    shop_item_id = db.Column(db.String(36), db.ForeignKey('shop_items.id'), nullable=False)
    purchased_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'shop_item_id': self.shop_item_id,
            'item': self.shop_item.to_dict() if self.shop_item else None,
            'purchased_at': self.purchased_at.isoformat(),
        }


class Transaction(db.Model):
    """Immutable ledger of all points/gems changes."""
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    change_type = db.Column(db.String(20), nullable=False)  # earn | spend | refund
    amount_points = db.Column(db.Integer, default=0, nullable=False)
    amount_gems = db.Column(db.Integer, default=0, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    related_id = db.Column(db.String(36), nullable=True)  # quest_id, challenge_id, shop_item_id, etc.
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'change_type': self.change_type,
            'amount_points': self.amount_points,
            'amount_gems': self.amount_gems,
            'reason': self.reason,
            'related_id': self.related_id,
            'timestamp': self.timestamp.isoformat(),
        }
