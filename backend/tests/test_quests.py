"""Tests for quest system."""
import json
import io


def _signup(client, email='quest@test.com'):
    resp = client.post('/api/v1/auth/signup', json={
        'email': email,
        'password': 'secret123',
        'display_name': 'Quest Tester',
    })
    return resp.get_json()['access_token']


def _create_quest(client, token):
    """Helper — make user admin and create a quest."""
    from app.models.user import User
    from app.extensions import db
    from flask_jwt_extended import decode_token

    # Make admin
    user = User.query.filter_by(email='quest@test.com').first()
    if user:
        user.is_admin = True
        db.session.commit()

    resp = client.post('/api/v1/admin/quests', json={
        'title': 'Test Quest',
        'description': 'Do something kind',
        'reward_points': 15,
    }, headers={'Authorization': f'Bearer {token}'})
    return resp.get_json()


def test_daily_quests(client, app):
    token = _signup(client)
    with app.app_context():
        _create_quest(client, token)
        _create_quest(client, token)
        _create_quest(client, token)

    resp = client.get('/api/v1/quests/daily', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    quests = resp.get_json()
    assert len(quests) == 3


def test_daily_quests_idempotent(client, app):
    """Getting daily quests twice should return the same quests."""
    token = _signup(client)
    with app.app_context():
        _create_quest(client, token)
        _create_quest(client, token)
        _create_quest(client, token)

    resp1 = client.get('/api/v1/quests/daily', headers={
        'Authorization': f'Bearer {token}'
    })
    resp2 = client.get('/api/v1/quests/daily', headers={
        'Authorization': f'Bearer {token}'
    })
    ids1 = [q['id'] for q in resp1.get_json()]
    ids2 = [q['id'] for q in resp2.get_json()]
    assert ids1 == ids2
