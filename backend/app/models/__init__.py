"""Models package — import all models so Alembic can discover them."""
from app.models.user import User
from app.models.quest import Quest, DailyQuest
from app.models.proof import Proof
from app.models.challenge import Challenge
from app.models.social import Friend
from app.models.shop import ShopItem, Purchase, Transaction
from app.models.admin import AdminAuditLog

__all__ = [
    'User', 'Quest', 'DailyQuest', 'Proof', 'Challenge',
    'Friend', 'ShopItem', 'Purchase', 'Transaction', 'AdminAuditLog',
]
