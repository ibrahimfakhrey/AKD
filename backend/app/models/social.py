"""Friend model — social connections between users."""
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Friend(db.Model):
    __tablename__ = 'friends'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    friend_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='requested', nullable=False)
    # status: requested | accepted | blocked
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships to user
    requester = db.relationship('User', foreign_keys=[user_id], backref='sent_friend_requests')
    addressee = db.relationship('User', foreign_keys=[friend_user_id], backref='received_friend_requests')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_user_id', name='uq_friend_pair'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'friend_user_id': self.friend_user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }
