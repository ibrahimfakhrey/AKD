"""Friends API — send, accept, block, list friend requests."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.social import Friend
from app.utils.errors import APIError, NotFoundError, ConflictError

friends_bp = Blueprint('friends', __name__, url_prefix='/api/v1/friends')


@friends_bp.route('/request', methods=['POST'])
@jwt_required()
def send_request():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'friend_email' not in data:
        raise APIError('friend_email is required')

    friend_email = data['friend_email']

    # Check target exists by email (case-insensitive)
    target = User.query.filter(User.email.ilike(friend_email)).first()
    if not target:
        raise NotFoundError('User with that email not found')
    
    # We use the target's actual UUID string from now on
    friend_id = target.id

    if friend_id == user_id:
        raise APIError('Cannot friend yourself')

    # Check duplicate
    existing = Friend.query.filter(
        ((Friend.user_id == user_id) & (Friend.friend_user_id == friend_id)) |
        ((Friend.user_id == friend_id) & (Friend.friend_user_id == user_id))
    ).first()
    if existing:
        if existing.status == 'blocked':
            raise APIError('Cannot send friend request')
        raise ConflictError('Friend request already exists')

    fr = Friend(user_id=user_id, friend_user_id=friend_id, status='requested')
    db.session.add(fr)
    db.session.commit()
    return jsonify(fr.to_dict()), 201


@friends_bp.route('/<request_id>/accept', methods=['POST'])
@jwt_required()
def accept_request(request_id):
    user_id = get_jwt_identity()
    fr = Friend.query.get(request_id)
    if not fr:
        raise NotFoundError('Friend request not found')
    if fr.friend_user_id != user_id:
        raise APIError('Not your friend request to accept', 403)
    if fr.status != 'requested':
        raise APIError(f'Request is already {fr.status}')

    fr.status = 'accepted'
    db.session.commit()
    return jsonify(fr.to_dict())


@friends_bp.route('/<request_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(request_id):
    user_id = get_jwt_identity()
    fr = Friend.query.get(request_id)
    if not fr:
        raise NotFoundError('Friend request not found')
    if fr.user_id != user_id and fr.friend_user_id != user_id:
        raise APIError('Not your friend record', 403)

    db.session.delete(fr)
    db.session.commit()
    return jsonify({'message': 'Friend removed'})


@friends_bp.route('/list', methods=['GET'])
@jwt_required()
def list_friends():
    user_id = get_jwt_identity()
    status_filter = request.args.get('status', 'accepted')

    friends = Friend.query.filter(
        ((Friend.user_id == user_id) | (Friend.friend_user_id == user_id)),
        Friend.status == status_filter,
    ).all()

    result = []
    for fr in friends:
        # Show the other person's info
        other_id = fr.friend_user_id if fr.user_id == user_id else fr.user_id
        other = User.query.get(other_id)
        result.append({
            'friendship_id': fr.id,
            'status': fr.status,
            'friend': other.to_dict() if other else None,
            'created_at': fr.created_at.isoformat(),
        })

    return jsonify(result)


@friends_bp.route('/pending', methods=['GET'])
@jwt_required()
def pending_requests():
    """Get incoming friend requests."""
    user_id = get_jwt_identity()
    pending = Friend.query.filter_by(friend_user_id=user_id, status='requested').all()
    result = []
    for fr in pending:
        requester = User.query.get(fr.user_id)
        result.append({
            'friendship_id': fr.id,
            'requester': requester.to_dict() if requester else None,
            'created_at': fr.created_at.isoformat(),
        })
    return jsonify(result)
