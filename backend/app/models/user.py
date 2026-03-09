"""User model."""
import uuid
from datetime import datetime, timezone

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=0, nullable=False)
    gems = db.Column(db.Integer, default=0, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_verified_email = db.Column(db.Boolean, default=False, nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    privacy_settings = db.Column(db.JSON, nullable=True)
    equipped_cosmetics = db.Column(db.JSON, nullable=True)  # {"avatar_frame": "item_id", ...}
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    daily_quests = db.relationship('DailyQuest', backref='user', lazy='dynamic')
    proofs = db.relationship('Proof', backref='user', lazy='dynamic')
    challenges = db.relationship('Challenge', backref='user', lazy='dynamic', foreign_keys='Challenge.user_id')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    purchases = db.relationship('Purchase', backref='user', lazy='dynamic')

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'points': self.points,
            'gems': self.gems,
            'equipped_cosmetics': self.equipped_cosmetics,
            'created_at': self.created_at.isoformat(),
        }
        if include_private:
            data.update({
                'email': self.email,
                'is_verified_email': self.is_verified_email,
                'is_admin': self.is_admin,
                'is_banned': self.is_banned,
                'privacy_settings': self.privacy_settings,
                'last_active_at': self.last_active_at.isoformat(),
            })
        return data

    def __repr__(self):
        return f'<User {self.display_name}>'
