"""Tests for leaderboard endpoints — points and gems rankings."""


def _signup(client, email, display_name='User', points=0, gems=0):
    resp = client.post('/api/v1/auth/signup', json={
        'email': email,
        'password': 'secret123',
        'display_name': display_name,
    })
    token = resp.get_json()['access_token']
    user_id = resp.get_json()['user']['id']

    if points or gems:
        from app.models.user import User
        from app.extensions import db
        user = User.query.get(user_id)
        user.points = points
        user.gems = gems
        db.session.commit()

    return token, user_id


def test_points_leaderboard(client, app):
    with app.app_context():
        tok1, _ = _signup(client, 'lb1@test.com', 'Alpha', points=100)
        _signup(client, 'lb2@test.com', 'Bravo', points=200)
        _signup(client, 'lb3@test.com', 'Charlie', points=50)

    resp = client.get('/api/v1/leaderboard/points',
                      headers={'Authorization': f'Bearer {tok1}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 3
    # Highest first
    assert data[0]['display_name'] == 'Bravo'
    assert data[0]['points'] == 200
    assert data[1]['display_name'] == 'Alpha'
    assert data[2]['display_name'] == 'Charlie'


def test_gems_leaderboard(client, app):
    with app.app_context():
        tok1, _ = _signup(client, 'glb1@test.com', 'Gem1', gems=30)
        _signup(client, 'glb2@test.com', 'Gem2', gems=60)
        _signup(client, 'glb3@test.com', 'Gem3', gems=10)

    resp = client.get('/api/v1/leaderboard/gems',
                      headers={'Authorization': f'Bearer {tok1}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 3
    assert data[0]['display_name'] == 'Gem2'


def test_leaderboard_pagination(client, app):
    with app.app_context():
        tok, _ = _signup(client, 'pag1@test.com', 'Pag1', points=300)
        _signup(client, 'pag2@test.com', 'Pag2', points=200)
        _signup(client, 'pag3@test.com', 'Pag3', points=100)

    resp = client.get('/api/v1/leaderboard/points?limit=2&offset=0',
                      headers={'Authorization': f'Bearer {tok}'})
    data = resp.get_json()
    assert len(data) == 2
    assert data[0]['rank'] == 1

    resp = client.get('/api/v1/leaderboard/points?limit=2&offset=2',
                      headers={'Authorization': f'Bearer {tok}'})
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['rank'] == 3


def test_banned_user_excluded(client, app):
    with app.app_context():
        tok, _ = _signup(client, 'ban_lb1@test.com', 'Visible', points=50)
        _, banned_id = _signup(client, 'ban_lb2@test.com', 'Banned', points=999)

        from app.models.user import User
        from app.extensions import db
        banned = User.query.get(banned_id)
        banned.is_banned = True
        db.session.commit()

    resp = client.get('/api/v1/leaderboard/points',
                      headers={'Authorization': f'Bearer {tok}'})
    names = [e['display_name'] for e in resp.get_json()]
    assert 'Banned' not in names
