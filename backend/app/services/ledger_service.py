"""Ledger service — atomic points/gems operations."""
from app.extensions import db
from app.models.user import User
from app.models.shop import Transaction
from app.utils.errors import InsufficientFundsError, NotFoundError


def _get_user_or_404(user_id):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    return user


def add_points(user_id, amount, reason, related_id=None):
    """Add points to a user and log the transaction."""
    user = _get_user_or_404(user_id)
    user.points += amount
    txn = Transaction(
        user_id=user_id,
        change_type='earn',
        amount_points=amount,
        reason=reason,
        related_id=related_id,
    )
    db.session.add(txn)
    db.session.flush()
    return txn


def deduct_points(user_id, amount, reason, related_id=None):
    """Deduct points from a user. Raises InsufficientFundsError if not enough."""
    user = _get_user_or_404(user_id)
    if user.points < amount:
        raise InsufficientFundsError('points')
    user.points -= amount
    txn = Transaction(
        user_id=user_id,
        change_type='spend',
        amount_points=amount,
        reason=reason,
        related_id=related_id,
    )
    db.session.add(txn)
    db.session.flush()
    return txn


def add_gems(user_id, amount, reason, related_id=None):
    """Add gems to a user and log the transaction."""
    user = _get_user_or_404(user_id)
    user.gems += amount
    txn = Transaction(
        user_id=user_id,
        change_type='earn',
        amount_gems=amount,
        reason=reason,
        related_id=related_id,
    )
    db.session.add(txn)
    db.session.flush()
    return txn


def deduct_gems(user_id, amount, reason, related_id=None):
    """Deduct gems from a user. Raises InsufficientFundsError if not enough."""
    user = _get_user_or_404(user_id)
    if user.gems < amount:
        raise InsufficientFundsError('gems')
    user.gems -= amount
    txn = Transaction(
        user_id=user_id,
        change_type='spend',
        amount_gems=amount,
        reason=reason,
        related_id=related_id,
    )
    db.session.add(txn)
    db.session.flush()
    return txn


def get_transaction_history(user_id, limit=50, offset=0):
    """Get a user's transaction history."""
    return (
        Transaction.query
        .filter_by(user_id=user_id)
        .order_by(Transaction.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
