"""Tests for ledger service — atomic points/gems operations and overdraft protection."""
import pytest


def _make_user(app):
    """Create a user directly in the DB and return their ID."""
    from app.models.user import User
    from app.extensions import db
    import bcrypt

    with app.app_context():
        pw = bcrypt.hashpw(b'test', bcrypt.gensalt()).decode()
        user = User(
            email='ledger@test.com',
            password_hash=pw,
            display_name='Ledger Tester',
            points=100,
            gems=50,
        )
        db.session.add(user)
        db.session.commit()
        return user.id


def test_add_points(app):
    user_id = _make_user(app)
    with app.app_context():
        from app.services.ledger_service import add_points
        from app.models.user import User
        from app.extensions import db

        txn = add_points(user_id, 25, 'quest_complete')
        db.session.commit()

        user = User.query.get(user_id)
        assert user.points == 125  # 100 + 25
        assert txn.amount_points == 25
        assert txn.change_type == 'earn'


def test_deduct_points(app):
    user_id = _make_user(app)
    with app.app_context():
        from app.services.ledger_service import deduct_points
        from app.models.user import User
        from app.extensions import db

        txn = deduct_points(user_id, 30, 'challenge_start')
        db.session.commit()

        user = User.query.get(user_id)
        assert user.points == 70  # 100 - 30
        assert txn.change_type == 'spend'


def test_deduct_points_overdraft(app):
    user_id = _make_user(app)
    with app.app_context():
        from app.services.ledger_service import deduct_points
        from app.utils.errors import InsufficientFundsError

        with pytest.raises(InsufficientFundsError):
            deduct_points(user_id, 999, 'too_expensive')


def test_add_gems(app):
    user_id = _make_user(app)
    with app.app_context():
        from app.services.ledger_service import add_gems
        from app.models.user import User
        from app.extensions import db

        txn = add_gems(user_id, 10, 'challenge_completed')
        db.session.commit()

        user = User.query.get(user_id)
        assert user.gems == 60  # 50 + 10
        assert txn.amount_gems == 10


def test_deduct_gems(app):
    user_id = _make_user(app)
    with app.app_context():
        from app.services.ledger_service import deduct_gems
        from app.models.user import User
        from app.extensions import db

        deduct_gems(user_id, 20, 'shop_purchase')
        db.session.commit()

        user = User.query.get(user_id)
        assert user.gems == 30  # 50 - 20


def test_deduct_gems_overdraft(app):
    user_id = _make_user(app)
    with app.app_context():
        from app.services.ledger_service import deduct_gems
        from app.utils.errors import InsufficientFundsError

        with pytest.raises(InsufficientFundsError):
            deduct_gems(user_id, 999, 'too_expensive')


def test_transaction_history(app):
    user_id = _make_user(app)
    with app.app_context():
        from app.services.ledger_service import add_points, deduct_points, get_transaction_history
        from app.extensions import db

        add_points(user_id, 10, 'quest_1')
        add_points(user_id, 20, 'quest_2')
        deduct_points(user_id, 5, 'challenge')
        db.session.commit()

        history = get_transaction_history(user_id)
        assert len(history) == 3
        # Most recent first
        assert history[0].reason == 'challenge'
        assert history[1].reason == 'quest_2'
