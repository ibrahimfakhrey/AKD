"""Challenge model — timed kindness challenges."""
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)
    # status: active | completed | failed | expired | pending_review
    cost_points = db.Column(db.Integer, default=10, nullable=False)
    proof_id = db.Column(db.String(36), db.ForeignKey('proofs.id'), nullable=True)
    reward_given = db.Column(db.Boolean, default=False, nullable=False)

    # Social challenge fields (populated when sent to a friend)
    challenge_type = db.Column(db.String(20), default='self', nullable=False)
    # challenge_type: 'self' | 'received'
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    recipient_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    proof = db.relationship('Proof', backref='challenge', uselist=False, foreign_keys=[proof_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'started_at': self.started_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'status': self.status,
            'cost_points': self.cost_points,
            'proof_id': self.proof_id,
            'reward_given': self.reward_given,
            'challenge_type': self.challenge_type,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
        }

