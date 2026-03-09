"""Quest and DailyQuest models."""
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Quest(db.Model):
    """Master quest catalog — created/managed by admins."""
    __tablename__ = 'quests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # e.g. "community", "self-care", "environment"
    difficulty_hint = db.Column(db.String(20), default='easy')  # easy / medium / hard
    reward_points = db.Column(db.Integer, default=10, nullable=False)
    reward_gems = db.Column(db.Integer, default=5, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_by_admin = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    daily_instances = db.relationship('DailyQuest', backref='quest', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty_hint': self.difficulty_hint,
            'reward_points': self.reward_points,
            'reward_gems': self.reward_gems,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
        }


class DailyQuest(db.Model):
    """Per-user daily quest instance."""
    __tablename__ = 'daily_quests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    quest_id = db.Column(db.String(36), db.ForeignKey('quests.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='assigned', nullable=False)
    # status: assigned | pending_review | completed | rejected
    proof_id = db.Column(db.String(36), db.ForeignKey('proofs.id'), nullable=True)
    reward_awarded = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'quest_id', 'date', name='uq_user_quest_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quest_id': self.quest_id,
            'quest': self.quest.to_dict() if self.quest else None,
            'date': self.date.isoformat(),
            'status': self.status,
            'proof_id': self.proof_id,
            'reward_awarded': self.reward_awarded,
        }
