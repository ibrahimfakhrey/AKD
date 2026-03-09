"""Proof model — photo evidence for quests and challenges."""
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Proof(db.Model):
    __tablename__ = 'proofs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    file_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    upload_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    ai_verification_result = db.Column(db.JSON, nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    verifier = db.Column(db.String(20), nullable=True)  # 'ai' | 'manual'
    verifier_confidence = db.Column(db.Float, nullable=True)
    moderation_flags = db.Column(db.JSON, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_url': self.file_url,
            'thumbnail_url': self.thumbnail_url,
            'upload_time': self.upload_time.isoformat(),
            'ai_verification_result': self.ai_verification_result,
            'verified': self.verified,
            'verifier': self.verifier,
            'verifier_confidence': self.verifier_confidence,
            'moderation_flags': self.moderation_flags,
        }
