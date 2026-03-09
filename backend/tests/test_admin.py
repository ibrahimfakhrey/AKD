"""Tests for admin endpoints — quest CRUD, user management, analytics, audit log."""


def _signup_admin(client, app, email='admin@test.com'):
    """Sign up and promote to admin."""
    resp = client.post('/api/v1/auth/signup', json={
        'email': email,
        'password': 'secret123',
        'display_name': 'Admin',
    })
    token = resp.get_json()['access_token']
    user_id = resp.get_json()['user']['id']

    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        user = User.query.get(user_id)
        user.is_admin = True
        db.session.commit()

    return token, user_id


def _signup_user(client, email='regular@test.com', display_name='Regular'):
    resp = client.post('/api/v1/auth/signup', json={
        'email': email,
        'password': 'secret123',
        'display_name': display_name,
    })
    data = resp.get_json()
    return data['access_token'], data['user']['id']


def test_non_admin_rejected(client, app):
    token, _ = _signup_user(client)
    resp = client.get('/api/v1/admin/quests',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 403


def test_create_quest(client, app):
    token, _ = _signup_admin(client, app)
    resp = client.post('/api/v1/admin/quests', json={
        'title': 'Admin Quest',
        'description': 'Created by admin',
        'reward_points': 20,
    }, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    assert resp.get_json()['title'] == 'Admin Quest'


def test_update_quest(client, app):
    token, _ = _signup_admin(client, app)
    create_resp = client.post('/api/v1/admin/quests', json={
        'title': 'Old Title',
        'description': 'Desc',
    }, headers={'Authorization': f'Bearer {token}'})
    quest_id = create_resp.get_json()['id']

    resp = client.put(f'/api/v1/admin/quests/{quest_id}',
                      json={'title': 'New Title', 'reward_points': 30},
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.get_json()['title'] == 'New Title'
    assert resp.get_json()['reward_points'] == 30


def test_delete_quest_soft(client, app):
    token, _ = _signup_admin(client, app)
    create_resp = client.post('/api/v1/admin/quests', json={
        'title': 'To Delete',
        'description': 'Will be deactivated',
    }, headers={'Authorization': f'Bearer {token}'})
    quest_id = create_resp.get_json()['id']

    resp = client.delete(f'/api/v1/admin/quests/{quest_id}',
                         headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert 'deactivated' in resp.get_json()['message'].lower()


def test_list_users(client, app):
    token, _ = _signup_admin(client, app)
    _signup_user(client, 'listed@test.com', 'Listed')

    resp = client.get('/api/v1/admin/users',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'users' in data
    assert data['total'] >= 2


def test_ban_unban_user(client, app):
    token, _ = _signup_admin(client, app)
    _, user_id = _signup_user(client, 'victim@test.com', 'Victim')

    # Ban
    resp = client.post(f'/api/v1/admin/users/{user_id}/ban',
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert 'banned' in resp.get_json()['message'].lower()

    # Unban
    resp = client.post(f'/api/v1/admin/users/{user_id}/unban',
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert 'unbanned' in resp.get_json()['message'].lower()


def test_analytics(client, app):
    token, _ = _signup_admin(client, app)

    resp = client.get('/api/v1/admin/analytics',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_users' in data
    assert 'pending_proofs' in data
    assert 'total_points_earned' in data


def test_audit_log(client, app):
    token, _ = _signup_admin(client, app)

    # Create a quest to generate an audit log entry
    client.post('/api/v1/admin/quests', json={
        'title': 'Audited Quest',
        'description': 'This should appear in audit log',
    }, headers={'Authorization': f'Bearer {token}'})

    resp = client.get('/api/v1/admin/audit-log',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1
    assert data[0]['action_type'] == 'create_quest'


def test_search_users(client, app):
    token, _ = _signup_admin(client, app)
    _signup_user(client, 'searchme@test.com', 'Findable')

    resp = client.get('/api/v1/admin/users?search=Findable',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['users']) >= 1
    assert any(u['display_name'] == 'Findable' for u in data['users'])
