"""Admin audit log model."""
import uuid
from datetime import datetime, timezone

from app.extensions import db


class AdminAuditLog(db.Model):
    __tablename__ = 'admin_audit_log'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    action_type = db.Column(db.String(50), nullable=False)  # e.g. "ban_user", "approve_proof", "create_quest"
    target_id = db.Column(db.String(36), nullable=True)
    details = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    actor = db.relationship('User', backref='audit_actions')

    def to_dict(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'action_type': self.action_type,
            'target_id': self.target_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
        }
