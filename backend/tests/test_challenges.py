"""Tests for challenge system — lifecycle, points deduction, gems reward."""
import io


def _signup(client, email='challenge@test.com', display_name='Challenger'):
    resp = client.post('/api/v1/auth/signup', json={
        'email': email,
        'password': 'secret123',
        'display_name': display_name,
    })
    return resp.get_json()['access_token']


def _give_points(app, email, points):
    """Give points directly to a user for test setup."""
    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        user.points = points
        db.session.commit()


def test_send_challenge(client, app):
    token = _signup(client)
    _signup(client, email='friend@test.com', display_name='Friend')
    _give_points(app, 'challenge@test.com', 100)

    # Need to make them friends first for the send to work
    from app.models.social import Friend
    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        u1 = User.query.filter_by(email='challenge@test.com').first()
        u2 = User.query.filter_by(email='friend@test.com').first()
        f = Friend(user_id=u1.id, friend_user_id=u2.id, status='accepted')
        db.session.add(f)
        db.session.commit()

    resp = client.post('/api/v1/challenges/send',
                       json={'friend_email': 'friend@test.com', 'description': 'Help someone'},
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'active'
    assert data['description'] == 'Help someone'


def test_send_challenge_insufficient_points(client, app):
    token = _signup(client)
    _signup(client, email='friend@test.com', display_name='Friend')
    _give_points(app, 'challenge@test.com', 5)  # less than 50 cost

    from app.models.social import Friend
    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        u1 = User.query.filter_by(email='challenge@test.com').first()
        u2 = User.query.filter_by(email='friend@test.com').first()
        f = Friend(user_id=u1.id, friend_user_id=u2.id, status='accepted')
        db.session.add(f)
        db.session.commit()

    resp = client.post('/api/v1/challenges/send',
                       json={'friend_email': 'friend@test.com'},
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 400
    assert 'Insufficient' in resp.get_json()['error']


def test_get_received_challenges(client, app):
    token = _signup(client)
    token2 = _signup(client, email='friend@test.com', display_name='Friend')
    _give_points(app, 'challenge@test.com', 100)

    from app.models.social import Friend
    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        u1 = User.query.filter_by(email='challenge@test.com').first()
        u2 = User.query.filter_by(email='friend@test.com').first()
        f = Friend(user_id=u1.id, friend_user_id=u2.id, status='accepted')
        db.session.add(f)
        db.session.commit()

    client.post('/api/v1/challenges/send',
                json={'friend_email': 'friend@test.com'},
                headers={'Authorization': f'Bearer {token}'})
                
    resp = client.get('/api/v1/challenges/received',
                      headers={'Authorization': f'Bearer {token2}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]['status'] == 'active'


def test_list_challenges(client, app):
    token = _signup(client)
    token2 = _signup(client, email='friend@test.com', display_name='Friend')
    _give_points(app, 'challenge@test.com', 100)

    from app.models.social import Friend
    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        u1 = User.query.filter_by(email='challenge@test.com').first()
        u2 = User.query.filter_by(email='friend@test.com').first()
        f = Friend(user_id=u1.id, friend_user_id=u2.id, status='accepted')
        db.session.add(f)
        db.session.commit()

    client.post('/api/v1/challenges/send',
                json={'friend_email': 'friend@test.com'},
                headers={'Authorization': f'Bearer {token}'})
                
    resp = client.get('/api/v1/challenges/',
                      headers={'Authorization': f'Bearer {token2}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_send_challenge_deducts_points(client, app):
    token = _signup(client)
    _signup(client, email='friend@test.com', display_name='Friend')
    _give_points(app, 'challenge@test.com', 100)

    from app.models.social import Friend
    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        u1 = User.query.filter_by(email='challenge@test.com').first()
        u2 = User.query.filter_by(email='friend@test.com').first()
        f = Friend(user_id=u1.id, friend_user_id=u2.id, status='accepted')
        db.session.add(f)
        db.session.commit()

    client.post('/api/v1/challenges/send',
                json={'friend_email': 'friend@test.com'},
                headers={'Authorization': f'Bearer {token}'})

    # Check points were deducted from sender
    resp = client.get('/api/v1/auth/profile',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.get_json()['points'] == 50  # 100 - 50 cost
