"""Admin API — moderation, quest management, analytics."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.quest import Quest, DailyQuest
from app.models.proof import Proof
from app.models.challenge import Challenge
from app.models.shop import Transaction
from app.models.admin import AdminAuditLog
from app.services.quest_service import complete_quest
from app.services.challenge_service import complete_challenge
from app.utils.decorators import admin_required
from app.utils.errors import APIError, NotFoundError

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')


def _audit(actor_id, action_type, target_id=None, details=None):
    """Log an admin action."""
    log = AdminAuditLog(
        actor_id=actor_id,
        action_type=action_type,
        target_id=target_id,
        details=details,
    )
    db.session.add(log)


# ── Quest Management ──────────────────────────────────────────

@admin_bp.route('/quests', methods=['GET'])
@jwt_required()
@admin_required
def list_quests():
    quests = Quest.query.order_by(Quest.created_at.desc()).all()
    return jsonify([q.to_dict() for q in quests])


@admin_bp.route('/quests', methods=['POST'])
@jwt_required()
@admin_required
def create_quest():
    admin_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get('title') or not data.get('description'):
        raise APIError('title and description are required')

    quest = Quest(
        title=data['title'],
        description=data['description'],
        category=data.get('category'),
        difficulty_hint=data.get('difficulty_hint', 'easy'),
        reward_points=data.get('reward_points', 10),
        reward_gems=data.get('reward_gems', 5),
        created_by_admin=admin_id,
    )
    db.session.add(quest)
    _audit(admin_id, 'create_quest', quest.id, {'title': quest.title})
    db.session.commit()
    return jsonify(quest.to_dict()), 201


@admin_bp.route('/quests/<quest_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_quest(quest_id):
    admin_id = get_jwt_identity()
    quest = Quest.query.get(quest_id)
    if not quest:
        raise NotFoundError('Quest not found')

    data = request.get_json()
    for field in ('title', 'description', 'category', 'difficulty_hint', 'reward_points', 'reward_gems', 'active'):
        if field in data:
            setattr(quest, field, data[field])

    _audit(admin_id, 'update_quest', quest.id, data)
    db.session.commit()
    return jsonify(quest.to_dict())


@admin_bp.route('/quests/<quest_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_quest(quest_id):
    admin_id = get_jwt_identity()
    quest = Quest.query.get(quest_id)
    if not quest:
        raise NotFoundError('Quest not found')
    quest.active = False  # Soft delete
    _audit(admin_id, 'delete_quest', quest.id)
    db.session.commit()
    return jsonify({'message': 'Quest deactivated'})


# ── Moderation ────────────────────────────────────────────────

@admin_bp.route('/proofs/pending', methods=['GET'])
@jwt_required()
@admin_required
def pending_proofs():
    proofs = Proof.query.filter_by(verified=False).order_by(Proof.upload_time.desc()).limit(50).all()
    
    # Attach proof type (quest or challenge) to moderation queue payload
    serialized_proofs = []
    for p in proofs:
        data = p.to_dict()
        data['proof_type'] = 'unknown'
        
        dq = DailyQuest.query.filter_by(proof_id=p.id).first()
        if dq:
            data['proof_type'] = 'quest'
            
        challenge = Challenge.query.filter_by(proof_id=p.id).first()
        if challenge:
            data['proof_type'] = 'challenge'
            
        serialized_proofs.append(data)

    return jsonify(serialized_proofs)


@admin_bp.route('/proofs/<proof_id>/verdict', methods=['POST'])
@jwt_required()
@admin_required
def verdict_proof(proof_id):
    admin_id = get_jwt_identity()
    proof = Proof.query.get(proof_id)
    if not proof:
        raise NotFoundError('Proof not found')

    data = request.get_json()
    approved = data.get('approved', False)

    proof.verified = approved
    proof.verifier = 'manual'
    proof.verifier_confidence = 1.0

    # Complete related quest or challenge
    dq = DailyQuest.query.filter_by(proof_id=proof_id).first()
    if dq:
        complete_quest(dq.id, verified=approved)

    challenge = Challenge.query.filter_by(proof_id=proof_id).first()
    if challenge:
        complete_challenge(challenge.id, verified=approved)

    _audit(admin_id, 'review_proof', proof.id, {'approved': approved})
    db.session.commit()
    return jsonify({'message': 'Verdict recorded', 'proof': proof.to_dict()})


# ── User Management ──────────────────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(
            User.display_name.ilike(f'%{search}%') | User.email.ilike(f'%{search}%')
        )
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'users': [u.to_dict(include_private=True) for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
    })


@admin_bp.route('/users/<user_id>/ban', methods=['POST'])
@jwt_required()
@admin_required
def ban_user(user_id):
    admin_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    user.is_banned = True
    _audit(admin_id, 'ban_user', user.id)
    db.session.commit()
    return jsonify({'message': f'User {user.display_name} banned'})


@admin_bp.route('/users/<user_id>/unban', methods=['POST'])
@jwt_required()
@admin_required
def unban_user(user_id):
    admin_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    user.is_banned = False
    _audit(admin_id, 'unban_user', user.id)
    db.session.commit()
    return jsonify({'message': f'User {user.display_name} unbanned'})


@admin_bp.route('/users/<user_id>/modify_balances', methods=['POST'])
@jwt_required()
@admin_required
def modify_user_balances(user_id):
    admin_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')

    data = request.get_json()
    points_delta = data.get('points_delta', 0)
    gems_delta = data.get('gems_delta', 0)

    user.points = max(0, user.points + points_delta)
    user.gems = max(0, user.gems + gems_delta)

    _audit(admin_id, 'modify_balances', user.id, {'points_delta': points_delta, 'gems_delta': gems_delta})
    db.session.commit()
    return jsonify({'message': 'Balances modified successfully', 'user': user.to_dict()})

# ── Audit Log ────────────────────────────────────────────────

@admin_bp.route('/audit-log', methods=['GET'])
@jwt_required()
@admin_required
def audit_log():
    limit = min(int(request.args.get('limit', 50)), 200)
    offset = int(request.args.get('offset', 0))
    logs = (
        AdminAuditLog.query
        .order_by(AdminAuditLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return jsonify([log.to_dict() for log in logs])


# ── Analytics ────────────────────────────────────────────────

@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required
def analytics():
    total_users = User.query.count()
    active_users = User.query.filter(User.is_banned == False).count()
    total_quests_completed = DailyQuest.query.filter_by(status='completed').count()
    total_challenges_completed = Challenge.query.filter_by(status='completed').count()
    pending_proofs = Proof.query.filter_by(verified=False).count()
    total_points_earned = db.session.query(db.func.sum(Transaction.amount_points)).filter_by(change_type='earn').scalar() or 0
    total_gems_earned = db.session.query(db.func.sum(Transaction.amount_gems)).filter_by(change_type='earn').scalar() or 0

    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_quests_completed': total_quests_completed,
        'total_challenges_completed': total_challenges_completed,
        'pending_proofs': pending_proofs,
        'total_points_earned': total_points_earned,
        'total_gems_earned': total_gems_earned,
    })
