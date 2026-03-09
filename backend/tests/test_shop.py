"""Tests for shop system — list items, buy with gems, inventory, overdraft."""


def _signup(client, email='shop@test.com'):
    resp = client.post('/api/v1/auth/signup', json={
        'email': email,
        'password': 'secret123',
        'display_name': 'Shopper',
    })
    return resp.get_json()['access_token']


def _create_shop_item(app, name='Test Item', price_gems=10):
    from app.models.shop import ShopItem
    from app.extensions import db
    with app.app_context():
        item = ShopItem(
            name=name,
            description='A test cosmetic',
            item_type='cosmetic',
            price_gems=price_gems,
        )
        db.session.add(item)
        db.session.commit()
        return item.id


def _give_gems(app, email, gems):
    from app.models.user import User
    from app.extensions import db
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        user.gems = gems
        db.session.commit()


def test_list_shop_items(client, app):
    token = _signup(client)
    _create_shop_item(app)

    resp = client.get('/api/v1/shop/items',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1
    assert data[0]['name'] == 'Test Item'


def test_buy_item(client, app):
    token = _signup(client)
    item_id = _create_shop_item(app, price_gems=15)
    _give_gems(app, 'shop@test.com', 50)

    resp = client.post(f'/api/v1/shop/buy/{item_id}',
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'Purchased' in data['message']

    # Verify gems deducted
    profile = client.get('/api/v1/auth/profile',
                         headers={'Authorization': f'Bearer {token}'}).get_json()
    assert profile['gems'] == 35  # 50 - 15


def test_buy_item_insufficient_gems(client, app):
    token = _signup(client, 'poor@test.com')
    item_id = _create_shop_item(app, 'Expensive', price_gems=100)
    _give_gems(app, 'poor@test.com', 5)

    resp = client.post(f'/api/v1/shop/buy/{item_id}',
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 400
    assert 'Insufficient' in resp.get_json()['error']


def test_buy_item_duplicate(client, app):
    token = _signup(client, 'twice@test.com')
    item_id = _create_shop_item(app, 'Unique Cosmetic', price_gems=5)
    _give_gems(app, 'twice@test.com', 100)

    resp = client.post(f'/api/v1/shop/buy/{item_id}',
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200

    resp = client.post(f'/api/v1/shop/buy/{item_id}',
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 400
    assert 'already own' in resp.get_json()['error']


def test_buy_nonexistent_item(client, app):
    token = _signup(client, 'ghost@test.com')

    resp = client.post('/api/v1/shop/buy/nonexistent-id',
                       headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 404


def test_inventory(client, app):
    token = _signup(client, 'inv@test.com')
    item_id = _create_shop_item(app, 'Inventory Item', price_gems=5)
    _give_gems(app, 'inv@test.com', 100)

    client.post(f'/api/v1/shop/buy/{item_id}',
                headers={'Authorization': f'Bearer {token}'})

    resp = client.get('/api/v1/shop/inventory',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['item']['name'] == 'Inventory Item'


def test_empty_inventory(client, app):
    token = _signup(client, 'empty@test.com')

    resp = client.get('/api/v1/shop/inventory',
                      headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.get_json() == []
