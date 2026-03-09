"""Tests for friends system — request, accept, delete, list, pending."""


def _signup(client, email, display_name='User'):
    resp = client.post('/api/v1/auth/signup', json={
        'email': email,
        'password': 'secret123',
        'display_name': display_name,
    })
    data = resp.get_json()
    return data['access_token'], data['user']['id']


def test_send_friend_request(client, app):
    token_a, id_a = _signup(client, 'alice@test.com', 'Alice')
    token_b, id_b = _signup(client, 'bob@test.com', 'Bob')

    resp = client.post('/api/v1/friends/request',
                       json={'friend_email': 'bob@test.com'},
                       headers={'Authorization': f'Bearer {token_a}'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'requested'
    assert data['user_id'] == id_a
    assert data['friend_user_id'] == id_b


def test_cannot_friend_yourself(client, app):
    token, uid = _signup(client, 'solo@test.com', 'Solo')

    resp = client.post('/api/v1/friends/request',
                       json={'friend_email': 'solo@test.com'},
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 400


def test_duplicate_friend_request(client, app):
    token_a, id_a = _signup(client, 'dup_a@test.com', 'DupA')
    token_b, id_b = _signup(client, 'dup_b@test.com', 'DupB')

    client.post('/api/v1/friends/request',
                json={'friend_email': 'dup_b@test.com'},
                headers={'Authorization': f'Bearer {token_a}'})
    resp = client.post('/api/v1/friends/request',
                       json={'friend_email': 'dup_b@test.com'},
                       headers={'Authorization': f'Bearer {token_a}'})
    assert resp.status_code == 409


def test_accept_friend_request(client, app):
    token_a, id_a = _signup(client, 'acc_a@test.com', 'AccA')
    token_b, id_b = _signup(client, 'acc_b@test.com', 'AccB')

    # A sends request to B
    resp = client.post('/api/v1/friends/request',
                       json={'friend_email': 'acc_b@test.com'},
                       headers={'Authorization': f'Bearer {token_a}'})
    friendship_id = resp.get_json()['id']

    # B accepts
    resp = client.post(f'/api/v1/friends/{friendship_id}/accept',
                       headers={'Authorization': f'Bearer {token_b}'})
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'accepted'


def test_cannot_accept_others_request(client, app):
    token_a, id_a = _signup(client, 'own_a@test.com', 'OwnA')
    token_b, id_b = _signup(client, 'own_b@test.com', 'OwnB')
    token_c, id_c = _signup(client, 'own_c@test.com', 'OwnC')

    resp = client.post('/api/v1/friends/request',
                       json={'friend_email': 'own_b@test.com'},
                       headers={'Authorization': f'Bearer {token_a}'})
    friendship_id = resp.get_json()['id']

    # C tries to accept A→B request
    resp = client.post(f'/api/v1/friends/{friendship_id}/accept',
                       headers={'Authorization': f'Bearer {token_c}'})
    assert resp.status_code == 403


def test_delete_friend(client, app):
    token_a, id_a = _signup(client, 'del_a@test.com', 'DelA')
    token_b, id_b = _signup(client, 'del_b@test.com', 'DelB')

    resp = client.post('/api/v1/friends/request',
                       json={'friend_email': 'del_b@test.com'},
                       headers={'Authorization': f'Bearer {token_a}'})
    friendship_id = resp.get_json()['id']

    resp = client.delete(f'/api/v1/friends/{friendship_id}',
                         headers={'Authorization': f'Bearer {token_a}'})
    assert resp.status_code == 200


def test_list_friends(client, app):
    token_a, id_a = _signup(client, 'list_a@test.com', 'ListA')
    token_b, id_b = _signup(client, 'list_b@test.com', 'ListB')

    # Create and accept friend request
    resp = client.post('/api/v1/friends/request',
                       json={'friend_email': 'list_b@test.com'},
                       headers={'Authorization': f'Bearer {token_a}'})
    friendship_id = resp.get_json()['id']
    client.post(f'/api/v1/friends/{friendship_id}/accept',
                headers={'Authorization': f'Bearer {token_b}'})

    # A's friends list
    resp = client.get('/api/v1/friends/list',
                      headers={'Authorization': f'Bearer {token_a}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['friend']['display_name'] == 'ListB'


def test_pending_requests(client, app):
    token_a, id_a = _signup(client, 'pend_a@test.com', 'PendA')
    token_b, id_b = _signup(client, 'pend_b@test.com', 'PendB')

    client.post('/api/v1/friends/request',
                json={'friend_email': 'pend_b@test.com'},
                headers={'Authorization': f'Bearer {token_a}'})

    # B checks pending
    resp = client.get('/api/v1/friends/pending',
                      headers={'Authorization': f'Bearer {token_b}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['requester']['display_name'] == 'PendA'
