"""Authentication API — signup, login, refresh, profile."""
from datetime import datetime, timezone

import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)

from app.extensions import db
from app.models.user import User
from app.utils.errors import APIError, ConflictError

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        raise APIError('JSON body required')

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    display_name = data.get('display_name', '').strip()

    if not email or not password or not display_name:
        raise APIError('email, password, and display_name are required')
    if len(password) < 6:
        raise APIError('Password must be at least 6 characters')

    if User.query.filter_by(email=email).first():
        raise ConflictError('Email already registered')

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        email=email,
        password_hash=password_hash,
        display_name=display_name,
    )
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Account created successfully',
        'user': user.to_dict(include_private=True),
        'access_token': access_token,
        'refresh_token': refresh_token,
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        raise APIError('JSON body required')

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise APIError('Invalid email or password', 401)

    if user.is_banned:
        raise APIError('Account has been banned', 403)

    user.last_active_at = datetime.now(timezone.utc)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'user': user.to_dict(include_private=True),
        'access_token': access_token,
        'refresh_token': refresh_token,
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise APIError('User not found', 404)
    return jsonify(user.to_dict(include_private=True))


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise APIError('User not found', 404)

    data = request.get_json()
    if not data:
        raise APIError('JSON body required')

    if 'display_name' in data:
        user.display_name = data['display_name'].strip()
    if 'bio' in data:
        user.bio = data['bio']
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    if 'privacy_settings' in data:
        user.privacy_settings = data['privacy_settings']
    if 'equipped_cosmetics' in data:
        user.equipped_cosmetics = data['equipped_cosmetics']

    db.session.commit()
    return jsonify(user.to_dict(include_private=True))
