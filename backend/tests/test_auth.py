"""Tests for auth endpoints."""
import json


def test_signup(client):
    resp = client.post('/api/v1/auth/signup', json={
        'email': 'test@example.com',
        'password': 'secret123',
        'display_name': 'Test User',
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'access_token' in data
    assert data['user']['email'] == 'test@example.com'


def test_signup_duplicate(client):
    client.post('/api/v1/auth/signup', json={
        'email': 'dup@example.com',
        'password': 'secret123',
        'display_name': 'Dup',
    })
    resp = client.post('/api/v1/auth/signup', json={
        'email': 'dup@example.com',
        'password': 'secret123',
        'display_name': 'Dup2',
    })
    assert resp.status_code == 409


def test_login(client):
    client.post('/api/v1/auth/signup', json={
        'email': 'login@example.com',
        'password': 'secret123',
        'display_name': 'Login User',
    })
    resp = client.post('/api/v1/auth/login', json={
        'email': 'login@example.com',
        'password': 'secret123',
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data


def test_login_wrong_password(client):
    client.post('/api/v1/auth/signup', json={
        'email': 'wrong@example.com',
        'password': 'secret123',
        'display_name': 'Wrong',
    })
    resp = client.post('/api/v1/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword',
    })
    assert resp.status_code == 401


def test_profile(client):
    signup = client.post('/api/v1/auth/signup', json={
        'email': 'profile@example.com',
        'password': 'secret123',
        'display_name': 'Profile User',
    })
    token = signup.get_json()['access_token']
    resp = client.get('/api/v1/auth/profile', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    assert resp.get_json()['display_name'] == 'Profile User'


def test_update_profile(client):
    signup = client.post('/api/v1/auth/signup', json={
        'email': 'update@example.com',
        'password': 'secret123',
        'display_name': 'Old Name',
    })
    token = signup.get_json()['access_token']
    resp = client.put('/api/v1/auth/profile',
                      json={'display_name': 'New Name', 'bio': 'Hello!'},
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.get_json()['display_name'] == 'New Name'
    assert resp.get_json()['bio'] == 'Hello!'


def test_health(client):
    resp = client.get('/api/v1/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ok'
